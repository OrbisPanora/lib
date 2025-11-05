from anvil.region import Region
from anvil.chunk import Chunk
from anvil.block import Block

class GeneralPattern:
    size : tuple[int, int, int] = (0, 0, 0) # x, y, z dimensions
    blocks : dict[tuple[int, int, int], int] = {} # (x, y, z) -> block type
    palette : list[dict[int, str]] = [] # block type -> properties

    region : Region = None
    chunk : Chunk = None

    type_blocks : list[Block] = []



    def __init__(self, region=None : Region, chunk=None : Chunk):
        self.size = size
        self.region = region
        self.chunk = chunk