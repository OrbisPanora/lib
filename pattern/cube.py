import _path
import anvil
from random import choice
from pattern.figure import Figure

class Cube(Figure):

    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        super().__init__(blocks, point, size)

    def empty(self):
        pass

    def filled(self):
        dictblock = {}
        gx, gy, gz = 0, 0, 0

        for y in range(self.size[1]):
            for z in range(self.size[2]):
                for x in range(self.size[0]):
                    gx = x + self.point[0]
                    gy = y + self.point[1]
                    gz = z + self.point[2]
                    dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock