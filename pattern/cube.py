import _path
import anvil
from random import choice
from pattern.figure import Figure

class Cube(Figure):

    def __init__(self, blocks : list[anvil.Block], size : list[int], region : anvil.Region = None, chunk : anvil.Chunk = None, down : int = 0):
        super().__init__(blocks, size, region, chunk, down)

    def empty(self):
        pass
    
    def filled(self):
        ### a coriger pas bien faite, faut pouvoire entrer les coordones
        if self.chunk is None:
            raise ValueError("Chunk n'est pas défini")
        for y in range(self.size[1]):
            for z in range(self.size[2]):
                for x in range(self.size[0]):
                    self.chunk.set_block(choice(self.blocks), x, y+self.down, z)