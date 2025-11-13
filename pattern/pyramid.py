import anvil
from random import choice
import pattern

class Pyramid(pattern.figure.Figure):

    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        super().__init__(blocks, point, size)

    def empty(self):
        dictblock = {}
        gx, gy, gz = 0, 0, 0
        height = self.size[1]
        base_x = self.size[0]
        base_z = self.size[2]

        for y in range(height):
            layer_size_x = base_x - (y * 2)
            layer_size_z = base_z - (y * 2)
            for z in range(layer_size_z):
                for x in range(layer_size_x):
                    gx = x + self.point[0] + y
                    gy = y + self.point[1]
                    gz = z + self.point[2] + y
                    if (x == 0 or x == layer_size_x - 1) or (z == 0 or z == layer_size_z - 1):
                        dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock

    def filled(self):
        dictblock = {}
        gx, gy, gz = 0, 0, 0
        height = self.size[1]
        base_x = self.size[0]
        base_z = self.size[2]

        for y in range(height):
            layer_size_x = base_x - (y * 2)
            layer_size_z = base_z - (y * 2)
            for z in range(layer_size_z):
                for x in range(layer_size_x):
                    gx = x + self.point[0] + y
                    gy = y + self.point[1]
                    gz = z + self.point[2] + y
                    dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock