import examples._path
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

        for y in range(self.size[1]): # 18 5 18 
            for z in range(self.size[2]):
                for x in range(self.size[0]):
                    gx = x + self.point[0] # 0
                    gy = y + self.point[1] # 160
                    gz = z + self.point[2] # 0

                    #if (x == 0 or x == self.size[0]-1) or (z == 0 or z == self.size[2]-1) or (y == 0 or y == self.size[1]-1):
                    dictblock[(gx, gy, gz)] = choice(self.blocks)
                        #dictblock[(gx-self.size[0]+1, gy, gz-self.size[2]+1)] = choice(self.blocks)

        return dictblock

    def cube_create(self):
        pass