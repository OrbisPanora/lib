import os
import anvil
from random import choice
from patterns.figure import Figure

class Cube(Figure):
    """
    Represents a cube pattern for block placement.
    Inherits from Figure and provides methods to generate empty and filled cubes.
    
    Attributes
    ----------
    blocks : list[anvil.Block]
        List of block types to use
    point : tuple[int, int, int]
        Starting point (x, y, z)
    size : tuple[int, int, int]
        Size of the cube (width, height, depth)
    """

    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        """
        Initialize a Cube object.
        
        Parameters
        ----------
        blocks : list[anvil.Block]
            List of block types to use
        point : tuple[int, int, int]
            Starting point (x, y, z)
        size : tuple[int, int, int]
            Size of the cube (width, height, depth)
        """
        super().__init__(blocks, point, size)

    def empty(self):
        """
        Generate a dictionary of blocks for an empty (hollow) cube.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
        dictblock = {}
        gx, gy, gz = 0, 0, 0

        for y in range(self.size[1]):
            for z in range(self.size[2]):
                for x in range(self.size[0]):
                    gx = x + self.point[0]
                    gy = y + self.point[1]
                    gz = z + self.point[2]

                    if (x == 0 or x == self.size[0]-1) or (z == 0 or z == self.size[2]-1) or (y == 0 or y == self.size[1]-1):
                        dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock

    def filled(self):
        """
        Generate a dictionary of blocks for a filled cube.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
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