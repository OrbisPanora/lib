import _path
import anvil
from random import choice
import pattern

# Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
#region = anvil.EmptyRegion(-2, -2)
region = anvil.Region.from_file('C:/Users/ssim9/AppData/Roaming/.minecraft/saves/testop/region/r.0.0.mca')
chunk = region.get_chunk(4,4)

cube = pattern.cube.Cube(blocks = [anvil.Block('minecraft', 'gold_block')], size = [8, 120, 14], region = region, chunk = chunk, down = -2)
cube.filled()





# # Create `Block` objects that are used to set blocks
# stone = anvil.Block('minecraft', 'stone')
# dirt = anvil.Block('minecraft', 'dirt')

# # pour region
# base_x = chunk.x * -1024   # = 512
# base_z = chunk.z * -1024  # = 512


# # Make a 16x16x16 cube of either stone or dirt blocks
# for y in range(16):
#     for z in range(16):
#         for x in range(16):
#             #gx = x+base_x
#             #gz = z+base_z
#             chunk.set_block(choice((stone, dirt)), x, y+100, z)

# Save to a file
chunk.save('C:/Users/ssim9/AppData/Roaming/.minecraft/saves/testop/region/r.0.0.mca')
