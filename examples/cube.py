import _path
import anvil
from random import choice
import pattern

# Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
#region = anvil.EmptyRegion(-2, -2)
# region = anvil.Region.from_file('C:/Users/ssim9/AppData/Roaming/.minecraft/saves/testop/region/r.0.0.mca')
# chunk = region.get_chunk(4,4)

# cube = pattern.cube.Cube(blocks = [anvil.Block('minecraft', 'gold_block')], size = [8, 120, 14], region = region, chunk = chunk, down = -2)
# cube.filled()


word = anvil.World(r'C:\Users\zayd2\AppData\Roaming\.minecraft\saves\New World test sde fdp')
#region00 = word.get_region(0,0)

cube = pattern.cube.Cube(blocks = [anvil.Block('minecraft', 'glowstone')], point = (160, 64, 160), size = (3, 3, 3))
dictblockcube = cube.filled()
print(dictblockcube)
word.apply(dictblockcube)

# pyramid = pattern.pyramid.Pyramid(blocks = [anvil.Block('minecraft', 'sandstone')], point = (30, 60, 0), size = (18, 9, 18))
# dictblockpyramid = pyramid.filled()

# spiral = pattern.spiral.Spiral(blocks = [anvil.Block('minecraft', 'oak_log')], point = (60, 60, 0), size = (18, 30, 18))
# dictblockspiral = spiral.filled()

####

# world.apply()
# pour changer dans region

####

word.save()
