import os
import anvil
from random import choice
import patterns

class Pyramid(patterns.figure.Figure):
    """
    Represents a pyramid pattern for block placement.
    Inherits from Figure and provides methods to generate empty and filled pyramids.
    """

    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        """
        Initialize a Pyramid object.
        """
        super().__init__(blocks, point, size)


    def empty(self):
        """
        Generate a dictionary of blocks for an empty (hollow) pyramid.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
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
        """
        Generate a dictionary of blocks for a filled pyramid.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
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