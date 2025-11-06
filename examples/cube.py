import _path
import anvil
from random import choice
from pattern import Cube, Pyramid, Spiral

# Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
#region = anvil.EmptyRegion(-2, -2)
# region = anvil.Region.from_file('C:/Users/ssim9/AppData/Roaming/.minecraft/saves/testop/region/r.0.0.mca')
# chunk = region.get_chunk(4,4)

# cube = Cube(blocks = [anvil.Block('minecraft', 'gold_block')], size = [8, 120, 14], region = region, chunk = chunk, down = -2)
# cube.filled()


word = anvil.World('C:/Users/ssim9/AppData/Roaming/.minecraft/saves/testop2')
#region00 = word.get_region(0,0)

cube = Cube(blocks = [anvil.Block('minecraft', 'diamond_block'), anvil.Block('minecraft', 'gold_block')], point = (200, 160, 200), size = (3,3,3))
dictblockcube = cube.filled()
word.apply(dictblockcube)

pyramid = Pyramid(blocks = [anvil.Block('minecraft', 'sandstone'), anvil.Block('minecraft', 'gold_block')], point = (300, 160, 200), size = (18, 9, 18))
dictblockpyramid = pyramid.filled()
word.apply(dictblockpyramid)

spiral = Spiral(blocks = [anvil.Block('minecraft', 'oak_log'), anvil.Block('minecraft', 'gold_block')], point = (200, 160, 300), size = (18, 30, 18))
dictblockspiral = spiral.filled()
word.apply(dictblockspiral)

####

# world.apply()
# pour changer dans region

####

word.save()
