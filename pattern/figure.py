from anvil.region import Region
from anvil.chunk import Chunk
from anvil.block import Block

class Figure():
    region : Region
    chunk : Chunk
    blocks : list[Block]
    size : list[int]
    down : int

    def __init__(self, blocks : list[Block], size : list[int], region : Region = None, chunk : Chunk = None, down : int = 0):
        self.region = region
        self.chunk = chunk
        self.blocks = blocks
        self.size = size
        self.down = down

    def empty(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def filled(self):
        raise NotImplementedError("Subclasses must implement this method.")