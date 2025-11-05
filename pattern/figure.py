from anvil.region import Region
from anvil.chunk import Chunk
from anvil.block import Block

class Figure():
    blocks : list[Block]
    size : tuple[int, int, int]
    point : tuple[int, int, int]

    def __init__(self, blocks : list[Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        self.point = point
        self.blocks = blocks
        self.size = size

    def empty(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def filled(self):
        raise NotImplementedError("Subclasses must implement this method.")