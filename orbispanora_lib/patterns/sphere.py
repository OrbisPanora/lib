"""Sphere: an ellipsoid pattern of blocks, empty or filled."""

from random import choice

from orbispanora_lib import anvil
from orbispanora_lib.patterns.figure import Figure


class Sphere(Figure):
    """
    Represents a sphere (ellipsoid) pattern for block placement.
    Inherits from Figure and provides methods to generate empty and filled spheres.

    Attributes
    ----------
    blocks : list[anvil.Block]
        List of block types to use
    point : tuple[int, int, int]
        Starting point (x, y, z)
    size : tuple[int, int, int]
        Size of the ellipsoid (width, height, depth)
    """

    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        """
        Initialize a Sphere object.

        Parameters
        ----------
        blocks : list[anvil.Block]
            List of block types to use
        point : tuple[int, int, int]
            Starting point (x, y, z)
        size : tuple[int, int, int]
            Size of the ellipsoid (width, height, depth)
        """
        super().__init__(blocks, point, size)


    def empty(self):
        """
        Generate a dictionary of blocks for an empty (hollow) sphere.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
        dictblock = {}
        gx, gy, gz = 0, 0, 0
        radius_x = self.size[0] / 2
        radius_y = self.size[1] / 2
        radius_z = self.size[2] / 2

        for y in range(self.size[1]):
            for z in range(self.size[2]):
                for x in range(self.size[0]):
                    gx = x + self.point[0]
                    gy = y + self.point[1]
                    gz = z + self.point[2]

                    # Check if the point is on the surface of the ellipsoid
                    if 0.9 <= (((x - radius_x) ** 2) / (radius_x ** 2) +
                                ((y - radius_y) ** 2) / (radius_y ** 2) +
                                ((z - radius_z) ** 2) / (radius_z ** 2)) <= 1.1:
                        dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock

    def filled(self):
        """
        Generate a dictionary of blocks for a filled sphere.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
        dictblock = {}
        gx, gy, gz = 0, 0, 0
        radius_x = self.size[0] / 2
        radius_y = self.size[1] / 2
        radius_z = self.size[2] / 2

        for y in range(self.size[1]):
            for z in range(self.size[2]):
                for x in range(self.size[0]):
                    gx = x + self.point[0]
                    gy = y + self.point[1]
                    gz = z + self.point[2]

                    # Check if the point is inside the ellipsoid
                    if (((x - radius_x) ** 2) / (radius_x ** 2) +
                        ((y - radius_y) ** 2) / (radius_y ** 2) +
                        ((z - radius_z) ** 2) / (radius_z ** 2)) <= 1:
                        dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock
