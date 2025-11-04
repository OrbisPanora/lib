import _path
import anvil
from random import choice

# Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
region = anvil.EmptyRegion(1, 1)

# Create `Block` objects that are used to set blocks
stone = anvil.Block('minecraft', 'stone')
dirt = anvil.Block('minecraft', 'dirt')

base_x = region.x * 634   # = 512
base_z = region.z * 1003  # = 512
#base_y = region.y * 127


# Make a 16x16x16 cube of either stone or dirt blocks
for y in range(16):
    for z in range(16):
        for x in range(16):
            gx = x+base_x
            gz = z+base_z
            region.set_block(choice((stone, dirt)), gx, y+100, gz)

# Save to a file
region.save('r.1.1.mca')
