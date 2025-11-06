from math import cos, sin
import examples._path
import anvil
from random import choice
import pattern

class Spiral(pattern.figure.Figure):
    def __init__(self, blocks : list[anvil.Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        super().__init__(blocks, point, size)

    def empty(self):
        pass

    def filled(self):
        dictblock = {}
        gx, gy, gz = 0, 0, 0

        # Spiral parameters
        r = min(self.size[0], self.size[2]) // 2  # radius based on size
        k = self.size[1] / (4 * 3.14159)          # vertical rise per radian
        n_tours = 3
        step = 5                                 # degrees per step

        for angle_deg in range(0, 360 * n_tours, step):
            theta = angle_deg * (3.14159 / 180)  # convert to radians
            x = r * cos(theta)
            z = r * sin(theta)
            y = k * theta                        # vertical progression

            gx = round(x) + self.point[0] + r
            gy = round(y) + self.point[1]
            gz = round(z) + self.point[2] + r

            if (0 <= gx - self.point[0] < self.size[0] and
                0 <= gy - self.point[1] < self.size[1] and
                0 <= gz - self.point[2] < self.size[2]):
                dictblock[(gx, gy, gz)] = choice(self.blocks)

        return dictblock



# import _path
# import anvil
# from random import choice
# import pattern
# from math import sin, cos, radians


# class Spiral(Figure):
#     def __init__(self, blocks: List[anvil.Block], point: Tuple[int, int, int], size: Tuple[int, int, int]):
#         super().__init__(blocks, point, size)

#     def empty(self):
#         pass

#     def filled(self):
#         #### tester !!!!!

#         coords = []
#         r = 10         # rayon
#         k = 0.5        # montée par radian
#         n_tours = 5
#         step = 5       # degrés par pas (plus petit = spirale plus fine)

#         for angle_deg in range(0, 360 * n_tours, step):
#             theta = radians(angle_deg)
#             x = r * cos(theta)
#             z = r * sin(theta)
#             y = k * theta  # progression verticale
#             coords.append((round(x), round(y), round(z)))