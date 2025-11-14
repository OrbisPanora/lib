import os
from math import cos, sin
import anvil
from random import choice
import patterns

class Spiral(patterns.figure.Figure):
    """
    Represents a spiral pattern for block placement.
    Inherits from Figure and provides methods to generate empty and filled spirals.
    """
    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        """
        Initialize a Spiral object.
        """
        super().__init__(blocks, point, size)

    def get_path(self) -> str:
        """
        Get the path to the pattern file.
        Returns
        -------
        str
            Absolute path to this pattern file
        """
        return os.path.abspath(__file__)

    def empty(self):
        """
        Generate a dictionary of blocks for an empty (hollow) spiral.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
        dictblock = {}
        gx, gy, gz = 0, 0, 0

        # Spiral parameters
        r = min(self.size[0], self.size[2]) // 2  # Radius based on size
        k = self.size[1] / (4 * 3.14159)          # Vertical rise per radian
        n_tours = 3
        step = 5                                 # Degrees per step

        for angle_deg in range(0, 360 * n_tours, step):
            theta = angle_deg * (3.14159 / 180)  # Convert to radians
            x = r * cos(theta)
            z = r * sin(theta)
            y = k * theta                        # Vertical progression

            gx = round(x) + self.point[0] + r
            gy = round(y) + self.point[1]
            gz = round(z) + self.point[2] + r

            if (0 <= gx - self.point[0] < self.size[0] and
                0 <= gy - self.point[1] < self.size[1] and
                0 <= gz - self.point[2] < self.size[2]):
                dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock

    def filled(self):
        """
        Generate a dictionary of blocks for a filled spiral.
        Returns
        -------
        dict
            Dictionary mapping (x, y, z) to block
        """
        dictblock = {}
        gx, gy, gz = 0, 0, 0

        # Spiral parameters
        r = min(self.size[0], self.size[2]) // 2  # Radius based on size
        k = self.size[1] / (4 * 3.14159)          # Vertical rise per radian
        n_tours = 3
        step = 5                                 # Degrees per step

        for angle_deg in range(0, 360 * n_tours, step):
            theta = angle_deg * (3.14159 / 180)  # Convert to radians
            x = r * cos(theta)
            z = r * sin(theta)
            y = k * theta                        # Vertical progression

            gx = round(x) + self.point[0] + r
            gy = round(y) + self.point[1]
            gz = round(z) + self.point[2] + r

            if (0 <= gx - self.point[0] < self.size[0] and
                0 <= gy - self.point[1] < self.size[1] and
                0 <= gz - self.point[2] < self.size[2]):
                dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock

