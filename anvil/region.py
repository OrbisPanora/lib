from typing import Tuple, Union, BinaryIO
from nbt import nbt
import zlib
import os
from io import BytesIO
import anvil
from .errors import GZipChunkData
from .versions import VERSION_21w43a
import tempfile
import gzip

class Region:
    """
    Region handler for Minecraft worlds

    Attributes
    ----------
    data: :class:`bytes`
        Region file (``.mca``) as bytes
    """
    __slots__ = ('data',)
    def __init__(self, data: bytes):
        """Makes a Region object from data, which is the region file content"""
        self.data = data

    @staticmethod
    def header_offset(chunk_x: int, chunk_z: int) -> int:
        """
        Returns the byte offset for given chunk in the header
        
        Parameters
        ----------
        chunk_x
            Chunk's X value
        chunk_z
            Chunk's Z value
        """
        return 4 * (chunk_x % 32 + chunk_z % 32 * 32)

    def chunk_location(self, chunk_x: int, chunk_z: int) -> Tuple[int, int]:
        """
        Returns the chunk offset in the 4KiB sectors from the start of the file,
        and the length of the chunk in sectors of 4KiB

        Will return ``(0, 0)`` if chunk hasn't been generated yet

        Parameters
        ----------
        chunk_x
            Chunk's X value
        chunk_z
            Chunk's Z value
        """
        b_off = self.header_offset(chunk_x, chunk_z)
        off = int.from_bytes(self.data[b_off : b_off + 3], byteorder='big')
        sectors = self.data[b_off + 3]
        return (off, sectors)

    def chunk_data(self, chunk_x: int, chunk_z: int) -> nbt.NBTFile:
        """
        Returns the NBT data for a chunk
        
        Parameters
        ----------
        chunk_x
            Chunk's X value
        chunk_z
            Chunk's Z value

        Raises
        ------
        anvil.GZipChunkData
            If the chunk's compression is gzip
        """
        off = self.chunk_location(chunk_x, chunk_z)
        # (0, 0) means it hasn't generated yet, aka it doesn't exist yet
        if off == (0, 0):
            return
        off = off[0] * 4096
        length = int.from_bytes(self.data[off:off + 4], byteorder='big')
        compression = self.data[off + 4] # 2 most of the time
        if compression == 1:
            raise GZipChunkData('GZip is not supported')
        compressed_data = self.data[off + 5 : off + 5 + length] # - 1
        return nbt.NBTFile(buffer=BytesIO(zlib.decompress(compressed_data)))

    def get_chunk(self, chunk_x: int, chunk_z: int) -> 'anvil.Chunk':
        """
        Returns the chunk at given coordinates,
        same as doing ``Chunk.from_region(region, chunk_x, chunk_z)``

        Parameters
        ----------
        chunk_x
            Chunk's X value
        chunk_z
            Chunk's Z value
        
        
        :rtype: :class:`anvil.Chunk`
        """
        return anvil.Chunk.from_region(self, chunk_x, chunk_z) ## au lieu de self il faut path ## faut voir sil est utiliser ailleurs

    def set_block(self, block: 'anvil.Block', x: int, y: int, z: int, file_path: str) -> None:
        """
        Sets a block at the specified coordinates and saves the changes to the region file.
        
        Parameters
        ----------
        block : :class:`anvil.Block`
            The block to set
        x : int
            Global X coordinate
        y : int
            Global Y coordinate
        z : int
            Global Z coordinate
        file_path : str
            Path to the region file to save to
        """
        chunk_x = x >> 4  
        chunk_z = z >> 4  
        
        local_x = x & 15  
        local_z = z & 15  
        
        try:
            print("chunk quon recup ", chunk_x, chunk_z)
            # anvil.Chunk.from_region(self, chunk_x, chunk_z)
            chunk = self.get_chunk(chunk_x % 32, chunk_z % 32) ## faut lui passer file_path
            print("TEST100")
            print(local_x,y,local_z, " coordonnes block dans regionset")
            chunk.set_block(block, local_x, y, local_z)
            
            self.save_chunk(chunk, file_path)
        except Exception as e:
            print(f"Failed to set block at ({x}, {y}, {z}): {e}")
            #raise Exception(f"Failed to set block at ({x}, {y}, {z}): {e}") from e
            raise e #Exception(f"Failed to set block at ({x}, {y}, {z})") from e
    
    def save_chunk(self, chunk: 'anvil.Chunk', file_path: str) -> None:
        """
        Saves a modified chunk to the region file.
        
        Parameters
        ----------
        chunk : :class:`anvil.Chunk`
            The chunk to save
        file_path : str
            Path to the region file to save to
        """
        nbt_data = chunk.data
        
        if chunk.version >= VERSION_21w43a:
            # Modern format - data is already the root (1.13+)
            nbt_file = nbt.NBTFile()
            nbt_file.tags = nbt_data.tags if hasattr(nbt_data, 'tags') else [nbt_data]
        else:
            # Legacy format - need to wrap in Level tag
            nbt_file = nbt.NBTFile()
            level_tag = nbt.TAG_Compound(name='Level')
            if hasattr(nbt_data, 'tags'):
                for tag in nbt_data.tags:
                    level_tag.tags.append(tag)
            else:
                level_tag.tags.append(nbt_data)
            nbt_file.tags = [level_tag]
        

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.nbt') as tmp:
                nbt_file.write_file(tmp.name)
                with gzip.open(tmp.name, 'rb') as gz_file:
                    decompressed = gz_file.read()
                compressed_data = zlib.compress(decompressed)
        finally:
            try:
                os.unlink(tmp.name)
            except:
                pass
        
        chunk_x, chunk_z = chunk.x, chunk.z
        off = self.header_offset(chunk_x, chunk_z)
        
        data_length = len(compressed_data) + 1  # +1 for compression byte
        sectors_needed = (data_length + 4095) // 4096  # Round up to 4KiB sectors
        
        # Find free space in region (need optimization)
        current_offset, current_sectors = self.chunk_location(chunk_x, chunk_z)
        
        if current_offset == 0:
            max_offset = 0
            for z in range(32):
                for x in range(32):
                    offset, sectors = self.chunk_location(x, z)
                    if offset + sectors > max_offset:
                        max_offset = offset + sectors
            new_offset = max_offset
        else:
            if sectors_needed <= current_sectors:
                new_offset = current_offset
            else:
                max_offset = 0
                for z in range(32):
                    for x in range(32):
                        offset, sectors = self.chunk_location(x, z)
                        if offset + sectors > max_offset:
                            max_offset = offset + sectors
                new_offset = max_offset
        
        header_data = bytearray(self.data)
        header_data[off:off + 3] = new_offset.to_bytes(3, byteorder='big')
        header_data[off + 3] = sectors_needed
        self.data = bytes(header_data)
        
        chunk_data_start = new_offset * 4096
        
        chunk_data = bytearray()
        chunk_data.extend(len(compressed_data).to_bytes(4, byteorder='big')) 
        chunk_data.append(2)  # Compression type (2 = zlib)
        chunk_data.extend(compressed_data)
        
        # Pad to sector boundary
        while len(chunk_data) < sectors_needed * 4096:
            chunk_data.append(0)
     
        region_data = bytearray(self.data)
        region_data[chunk_data_start:chunk_data_start + len(chunk_data)] = chunk_data
        self.data = bytes(region_data)
        
        with open(file_path, 'wb') as f:
            f.write(self.data)

    @classmethod
    def from_file(cls, file: Union[str, BinaryIO]):
        """
        Creates a new region with the data from reading the given file

        Parameters
        ----------
        file
            Either a file path or a file object
        """
        if isinstance(file, str):
            with open(file, 'rb') as f:
                return cls(data=f.read())
        else:
            return cls(data=file.read())
