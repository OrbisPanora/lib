from typing import Tuple, Union, BinaryIO
from nbt import nbt
from io import BytesIO
from anvil import Block
from anvil import Chunk
from .errors import GZipChunkData
from .versions import VERSION_21w43a

class Structure:
    """
    Read-only structure

    Attributes
    ----------
    data: :class:`nbt.TAG_Compound`
        Raw NBT data of the chunk
    size: :class:`
    """
    def __init__(self, data: nbt):
        """Makes a Structure object from data, which is the region file content"""
        self.nbtData = data
        self.size: tuple[int, int, int] = self.nbtData.get("size", [])
        self.entities: list[tuple[tuple[int, int, int], int]] = [((i["pos"][0].value, i["pos"][1].value, i["pos"][2].value),i["state"].value) for i in self.nbtData.get("entities", [])]
        self.blocks: list[tuple[tuple[int, int, int], int]] = [((i["pos"][0].value, i["pos"][1].value, i["pos"][2].value),i["state"].value) for i in self.nbtData.get("blocks", [])]
        self.palette: list[str] = [Block.from_palette(i) for i in self.nbtData.get("palette", [])]

    @classmethod
    def from_file(cls, fileName: str):
        """
        Creates a new structure with the data from reading the given file

        Parameters
        ----------
        fileName
            file path
        """
        data = nbt.NBTFile(fileName)
        if data is None:
            raise TypeError("Error from file to get datas")
        return cls(data)
    
    def generate(self, chunk: Chunk, y:int):
        for block in self.blocks:
            chunk.set_block(self.palette[block[1]], block[0][0], block[0][1]+y, block[0][2])
            #print(self.palette[block[1]])
            #print(block[0][0])
            #print(block[0][1]+ y)
            #print(block[0][2])
        return chunk
