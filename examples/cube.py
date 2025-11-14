import _path
import anvil
from patterns import Cube, Pyramid, Spiral, Sphere

# Example: Creating patterns in a Minecraft world using the World facade
# The World class provides caching for better performance

# Initialize world with custom cache sizes (optional)
# Default: chunk_cache_size=512, region_cache_size=32
world = anvil.World(
    r'your path',
    chunk_cache_size=1024,  # Cache up to 1024 chunks
    region_cache_size=64     # Cache up to 64 regions
)

###########################################################################
############        Uncomment to create patterns        ###################
###########################################################################
###########################################################################
# Create a cube pattern using apply_figure
world.apply_figure(
    Cube,
    blocks=[anvil.Block('minecraft', 'diamond_block')],
    point=(160, 64, 160),
    size=(5, 5, 5),
    filled=True
)

# # Create a pyramid pattern
# pyramid = Pyramid(
#     blocks=[anvil.Block('minecraft', 'sandstone')], 
#     point=(30, 60, 0), 
#     size=(18, 9, 18)
# )
# pyramid_blocks = pyramid.filled()
# world.apply(pyramid_blocks)

# # Create a spiral pattern
# spiral = Spiral(
#     blocks=[anvil.Block('minecraft', 'oak_log')], 
#     point=(60, 60, 0), 
#     size=(18, 30, 18)
# )
# spiral_blocks = spiral.filled()
# world.apply(spiral_blocks)

# # Create a sphere pattern
# sphere = Sphere(
#     blocks=[anvil.Block('minecraft', 'gold_block')], 
#     point=(200, 170, 200), 
#     size=(10, 10, 10)
# )
# sphere_blocks = sphere.filled()
# world.apply(sphere_blocks)

# # Create a hollow sphere pattern
# hollow_sphere = Sphere(
#     blocks=[anvil.Block('minecraft', 'iron_block')], 
#     point=(200, 100, 200), 
#     size=(20, 20, 20)
# )
# hollow_sphere_blocks = hollow_sphere.empty()
# world.apply(hollow_sphere_blocks)

# # Create a hollow cube pattern
# hollow_cube = Cube(
#     blocks=[anvil.Block('minecraft', 'emerald_block')], 
#     point=(160, 150, 160), 
#     size=(18, 18, 18)
# )
# hollow_cube_blocks = hollow_cube.empty()
# world.apply(hollow_cube_blocks)

# #Create a hollow pyramid pattern
# hollow_pyramid = Pyramid(
#     blocks=[anvil.Block('minecraft', 'quartz_block')], 
#     point=(30, 140, 0), 
#     size=(18, 9, 18)
# )
# hollow_pyramid_blocks = hollow_pyramid.empty()
# world.apply(hollow_pyramid_blocks)
###########################################################################

# Save all changes to disk
world.save()

# Optional: View cache statistics
stats = world.get_cache_stats()
print(f"Chunk cache: {stats['chunk_cache']['hit_rate']} hit rate")
print(f"Region cache: {stats['region_cache']['hit_rate']} hit rate")
