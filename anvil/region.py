from typing import Tuple, Union, BinaryIO, Optional
from nbt import nbt
import zlib
from io import BytesIO
import anvil
from .errors import GZipChunkData
from .versions import VERSION_21w43a
from .cache_manager import CacheManager
import tempfile
import re
import gzip

class Region:
    """
    Region handler for Minecraft worlds with optional chunk caching

    Attributes
    ----------
    data: :class:`bytes`
        Region file (``.mca``) as bytes
    _chunk_cache: :class:`CacheManager` or None
        Optional LRU cache for loaded chunks
    """
    __slots__ = ('data', '_chunk_cache', 'xpos', 'zpos')
    
    def __init__(self, data: bytes, cache_size: Optional[int] = 64, region_x: Optional[int] = None, region_z: Optional[int] = None):
        """
        Makes a Region object from data, which is the region file content
        
        Parameters
        ----------
        data : bytes
            Region file content
        cache_size : Optional[int]
            Maximum number of chunks to cache. If None, caching is disabled.
            Default is 64 chunks.
        """
        self.data = data
        self._chunk_cache = CacheManager(max_size=cache_size) if cache_size else None

        self.region_x: int = region_x
        self.region_z: int = region_z

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

    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional['anvil.Chunk']:
        """
        Returns the chunk at given coordinates with optional caching,
        same as doing ``Chunk.from_region(region, chunk_x, chunk_z)``

        Parameters
        ----------
        chunk_x
            Chunk's X value
        chunk_z
            Chunk's Z value
        
        
        :rtype: :class:`anvil.Chunk`
        """
        if self._chunk_cache is not None:
            cache_key = (chunk_x, chunk_z)
            cached_chunk = self._chunk_cache.get(cache_key)
            if cached_chunk is not None:
                return cached_chunk
        
        # Load chunk from region file
        chunk = anvil.Chunk.from_region(self, chunk_x, chunk_z)
        
        # Cache the loaded chunk if caching is enabled
        if self._chunk_cache is not None and chunk is not None:
            self._chunk_cache.put((chunk_x, chunk_z), chunk)
        
        return chunk

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
            # Get chunk from region
            chunk = self.get_chunk(chunk_x % 32, chunk_z % 32)
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
        
        # Serialize NBT data to bytes
        buffer = BytesIO()
        nbt_file.write_file(fileobj=buffer)
        buffer.seek(0)

        # Skip the gzip header (10 bytes) and footer (8 bytes) to get raw deflate data
        # or better: decompress gzip then recompress with zlib
        nbt_bytes = gzip.decompress(buffer.read())
        compressed_data = zlib.compress(nbt_bytes)

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
        chunk_data.extend((len(compressed_data) + 1).to_bytes(4, byteorder='big'))  # +1 for compression byte
        chunk_data.append(2)  # Compression type (2 = zlib)
        chunk_data.extend(compressed_data)
        
        # Pad to sector boundary
        while len(chunk_data) < sectors_needed * 4096:
            chunk_data.append(0)
     
        region_data = bytearray(self.data)

        # Extend the region data if necessary
        required_size = chunk_data_start + len(chunk_data)
        if len(region_data) < required_size:
            region_data.extend(bytearray(required_size - len(region_data)))

        region_data[chunk_data_start:chunk_data_start + len(chunk_data)] = chunk_data
        self.data = bytes(region_data)
        
        with open(file_path, 'wb') as f:
            f.write(self.data)

    @classmethod
    def from_file(cls, file: Union[str, BinaryIO], cache_size: Optional[int] = 64):
        """
        Creates a new region with the data from reading the given file

        Parameters
        ----------
        file
            Either a file path or a file object
        cache_size : Optional[int]
            Maximum number of chunks to cache. If None, caching is disabled.
            Default is 64 chunks.
        """
        if isinstance(file, str):
            base = os.path.basename(file)
            match = re.match(r"r\.(-?\d+)\.(-?\d+)\.mca$", base)
            if not match:
                raise ValueError(f"Invalid region file name: {filename}")

            x = int(match.group(1))
            z = int(match.group(2))
            with open(file, 'rb') as f:
                return cls(data=f.read(), cache_size=cache_size, xpos=x, zpos=z)
        else:
            return cls(data=file.read(), cache_size=cache_size)


    def replace_block_at(self, x: int, y: int, z: int, new_block: Union[str, 'anvil.Block'], file_path: str) -> bool:
        """
        Replace a single block at specific global coordinates.

        Parameters
        ----------
        x : int
            Global X coordinate
        y : int
            Global Y coordinate
        z : int
            Global Z coordinate
        new_block : Union[str, anvil.Block]
            The replacement block
        file_path : str
            Path to the region file to save to

        Returns
        -------
        bool
            True if the block was replaced, False otherwise

        Example
        -------
        >>> region.replace_block_at(100, 64, 200, "minecraft:diamond_block", "r.0.0.mca")
        """
        chunk_x = x >> 4
        chunk_z = z >> 4

        local_x = x & 15
        local_z = z & 15

        try:
            chunk = self.get_chunk(chunk_x % 32, chunk_z % 32)

            if chunk.replace_block_at(local_x, y, local_z, new_block):
                self.save_chunk(chunk, file_path)
                return True

            return False
        except Exception:
            return False

    def replace_blocks(
        self,
        old_block: Union[str, 'anvil.Block'],
        new_block: Union[str, 'anvil.Block'],
        file_path: str,
        chunks: Union[Tuple[int, int], list[Tuple[int, int]], None] = None
    ) -> int:
        """
        Replace all occurrences of a specific block type with another block type
        in one or more chunks of the region.

        Parameters
        ----------
        old_block : Union[str, anvil.Block]
            The block to replace (either a block name like "minecraft:stone" or a Block object)
        new_block : Union[str, anvil.Block]
            The replacement block (either a block name like "minecraft:dirt" or a Block object)
        file_path : str
            Path to the region file to save to
        chunks : Union[Tuple[int, int], list[Tuple[int, int]], None], optional
            Either:
            - A single chunk coordinate tuple (chunk_x, chunk_z)
            - A list of chunk coordinate tuples [(chunk_x1, chunk_z1), (chunk_x2, chunk_z2), ...]
            - None to process all chunks in the region (default)

        Returns
        -------
        int
            The total number of blocks replaced across all processed chunks

        Examples
        --------
        >>> # Replace in a single chunk
        >>> count = region.replace_blocks("minecraft:stone", "minecraft:dirt", "r.0.0.mca", chunks=(5, 10))

        >>> # Replace in multiple chunks
        >>> count = region.replace_blocks("minecraft:oak_log", "minecraft:birch_log", "r.0.0.mca",
        ...                               chunks=[(0, 0), (1, 0), (0, 1)])

        >>> # Replace in all chunks of the region
        >>> count = region.replace_blocks("minecraft:sand", "minecraft:gravel", "r.0.0.mca")
        """
        from typing import List

        total_count = 0
        chunks_to_process: List[Tuple[int, int]] = []

        # Determine which chunks to process
        if chunks is None:
            # Process all chunks in the region (32x32)
            for chunk_z in range(32):
                for chunk_x in range(32):
                    if self.chunk_location(chunk_x, chunk_z) != (0, 0):
                        chunks_to_process.append((chunk_x, chunk_z))
        elif isinstance(chunks, tuple) and len(chunks) == 2:
            # Single chunk
            chunks_to_process.append(chunks)
        elif isinstance(chunks, list):
            # Multiple chunks
            chunks_to_process = chunks
        else:
            raise ValueError("chunks parameter must be a tuple (x, z), a list of tuples, or None")
    
        for chunk_x, chunk_z in chunks_to_process:
            try:
                chunk = self.get_chunk(chunk_x % 32, chunk_z % 32)

                count = chunk.replace_blocks(old_block, new_block)

                if count > 0:
                    self.save_chunk(chunk, file_path)
                    total_count += count

            except Exception:
                continue

        return total_count
    
    def clear_cache(self) -> None:
        """Clear the chunk cache if enabled."""
        if self._chunk_cache is not None:
            self._chunk_cache.clear()
    
    def get_cache_stats(self) -> Optional[dict]:
        """
        Get cache statistics.
        
        Returns
        -------
        Optional[dict]
            Cache statistics if caching is enabled, None otherwise
        """
        if self._chunk_cache is not None:
            return self._chunk_cache.get_stats()
        return None
    
    def invalidate_chunk(self, chunk_x: int, chunk_z: int) -> None:
        """
        Invalidate a specific chunk in the cache.
        
        Parameters
        ----------
        chunk_x : int
            Chunk X coordinate
        chunk_z : int
            Chunk Z coordinate
        """
        if self._chunk_cache is not None:
            self._chunk_cache.invalidate((chunk_x, chunk_z))
    
    def to_dict(self, include_chunks: bool = False) -> dict:
        """
        Convert the region to a dictionary for JSON serialization (API-friendly).
        
        Parameters
        ----------
        include_chunks : bool
            If True, include list of available chunks (default: False)
        
        Returns
        -------
        dict
            Dictionary with region metadata
            
        Example
        -------
        >>> region = Region.from_file('r.0.0.mca')
        >>> region.to_dict(include_chunks=True)
        {'region_x': 0, 'region_z': 0, 'chunks': [[0, 0], [0, 1], ...]}
        """
        data = {
            'region_x': self.region_x if hasattr(self, 'region_x') else None,
            'region_z': self.region_z if hasattr(self, 'region_z') else None
        }
        
        if include_chunks:
            chunks_list = []
            for chunk_x in range(32):
                for chunk_z in range(32):
                    try:
                        chunk = self.get_chunk(chunk_x, chunk_z)
                        if chunk is not None:
                            chunks_list.append([chunk_x, chunk_z])
                    except:
                        pass
            data['chunks'] = chunks_list
            data['chunk_count'] = len(chunks_list)
        
        return data

    def save(self, file_path: str) -> None:
        """
        Save the region data to a file.
        
        Parameters
        ----------
        file_path : str
            Path to the region file to save to
        
        Example
        -------
        >>> region.save('r.0.0.mca')
        """
        with open(file_path, 'wb') as f:
            f.write(self.data)
