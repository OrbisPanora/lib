import _path
import anvil
from pattern import Cube, Pyramid, Spiral

# Example: Creating patterns in a Minecraft world using the World facade
# The World class provides caching for better performance

# Initialize world with custom cache sizes (optional)
# Default: chunk_cache_size=512, region_cache_size=32
world = anvil.World(
    r'C:\Users\zayd2\AppData\Roaming\.minecraft\saves\New World(3)',
    chunk_cache_size=1024,  # Cache up to 1024 chunks
    region_cache_size=64     # Cache up to 64 regions
)

# Create a cube pattern
cube = Cube(
    blocks=[anvil.Block('minecraft', 'diamond_block')], 
    point=(160, 64, 160), 
    size=(5, 5, 5)
)
cube_blocks = cube.filled()
world.apply(cube_blocks)

# Create a pyramid pattern
pyramid = Pyramid(
    blocks=[anvil.Block('minecraft', 'sandstone')], 
    point=(30, 60, 0), 
    size=(18, 9, 18)
)
pyramid_blocks = pyramid.filled()
world.apply(pyramid_blocks)

# Create a spiral pattern
spiral = Spiral(
    blocks=[anvil.Block('minecraft', 'oak_log')], 
    point=(60, 60, 0), 
    size=(18, 30, 18)
)
spiral_blocks = spiral.filled()
world.apply(spiral_blocks)

# Save all changes to disk
world.save()

# Optional: View cache statistics
stats = world.get_cache_stats()
print(f"Chunk cache: {stats['chunk_cache']['hit_rate']} hit rate")
print(f"Region cache: {stats['region_cache']['hit_rate']} hit rate")
