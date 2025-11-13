from typing import Tuple, Union, BinaryIO
from nbt import nbt
from io import BytesIO
from anvil import Block
from anvil import World
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
        raw_palette = self.nbtData.get("palette", [])
        print(f"Structure palette info: {len(raw_palette)} entries")
        for i, entry in enumerate(raw_palette):
            print(f"Palette entry {i}: {entry}")
        self.palette: list[str] = [Block.from_palette(i) for i in raw_palette]
        palette_len = len(self.palette)
        print(f"Processed palette length: {palette_len}")
        
        blocks = []
        for block in self.nbtData.get("blocks", []):
            pos = (block["pos"][0].value, block["pos"][1].value, block["pos"][2].value)
            state = block["state"].value
            if state >= palette_len:
                print(f"Warning: Structure contains invalid palette index {state} at position {pos}, skipping block")
                continue
            blocks.append((pos, state))
        self.blocks = blocks

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
    
    def generate_in_world(self, world: World, x:int, y:int, z:int):
        for block in self.blocks:
            palette_index = block[1]
            if not world.is_in_palette_section(self.palette[palette_index], block[0][0], block[0][1], block[0][2]):
                world.add_block_to_palette(self.palette[palette_index], block[0][0], block[0][1], block[0][2])
        for block in self.blocks:
            palette_index = block[1]
            if palette_index >= len(self.palette):
                air_block = Block.from_name("minecraft:air")
                world.set_block(air_block, block[0][0]+x, block[0][1]+y, block[0][2]+z)
                continue
            world.set_block(self.palette[palette_index], block[0][0]+x, block[0][1]+y, block[0][2]+z)
        return world