# Orbis Panora library

A Python library designed to read, modify, and write **Minecraft world save files** (Anvil and NBT formats). It provides an object-oriented interface for easy access to **chunks, blocks, entities, and biomes**.

## Project Origin 

`anvil-parser2` is a **fork** of **0xTiger's anvil-parser**, which itself was originally forked from [matcool's anvil-parser](https://github.com/matcool/anvil-parser). The initial fork by 0xTiger aimed to add support for Minecraft versions **1.18 and above**. Our current version continues this development as the core data layer for a larger project that includes a REST API and a web-based isometric viewer.

---

# Usage

## install OP lib

```bash
pip install git+ssh://git@codefirst.iut.uca.fr/IUT_INF63/projets-etudiants/OrbisPanora/lib.git@origin/dev
```

## test simple region, chunk, block retrieval

```python
import anvil

# link to mca file
path = '../sae/Egyptian_Odyssey/region/r.0.0.mca'

# retrieve a region
region = anvil.Region.from_file(path) 

# retrieve a chunk at x<32, z<32 
chunk = region.get_chunk(0, 0)

# retrieve a block at coordinates x<16, -64<y<319, z<16
block = chunk.get_block(0, 0, 0)

# display details about the block
print(block.id)   # ex: minecraft:flowing_water
print(block.properties)	# ex {"level": 0, "falling": true}
```


## test World

```python
import anvil

# link to the world folder (the one in "/saves")
path = './testop2'

# retrieve the world
world = anvil.World(path) 

# retrieve a region (r.x.z.mca)
region = world.get_region(0, 0)

# retrieve a chunk with global coordinates x, z (no need to stay limited to 32, 32)
chunk = world.get_chunk(0, 0)

# retrieve a block with global coordinates x, y, z (no need to stay limited to 16, 16, 16)
block = world.get_block(0, 0, 0)

# display the block
print(block)

# place a block
block2 = anvil.Block('minecraft', 'gold_block')
world.set_block(block2, 201, 162, 201)

# check it in Minecraft (if you test with print, it will display None at first try)
```

---

# OrbisPanora Functionalities

## Patterns

The library includes geometric pattern generators for creating complex structures easily.

### Available Patterns

- **Cube**: Rectangular box structures (filled or hollow)
- **Pyramid**: Stepped pyramid structures
- **Sphere**: Spherical/ellipsoid structures
- **Spiral**: Helical spiral structures

### Using Patterns

```python
import anvil
from patterns import Cube, Pyramid, Sphere, Spiral

world = anvil.World('./my_world')

# Create a filled cube
cube = Cube(
    blocks=[anvil.Block('minecraft', 'diamond_block'), anvil.Block('minecraft', 'gold_block')],
    point=(200, 160, 200),
    size=(10, 10, 10)
)
world.apply(cube.filled())

# Create a hollow cube
hollow_cube = Cube(
    blocks=[anvil.Block('minecraft', 'glass')],
    point=(220, 160, 200),
    size=(15, 15, 15)
)
world.apply(hollow_cube.empty())

# Create a pyramid
pyramid = Pyramid(
    blocks=[anvil.Block('minecraft', 'sandstone'), anvil.Block('minecraft', 'smooth_sandstone')],
    point=(300, 160, 200),
    size=(21, 11, 21)
)
world.apply(pyramid.filled())

# Create a sphere
sphere = Sphere(
    blocks=[anvil.Block('minecraft', 'sea_lantern')],
    point=(400, 160, 200),
    size=(20, 20, 20)
)
world.apply(sphere.filled())

# Create a spiral
spiral = Spiral(
    blocks=[anvil.Block('minecraft', 'oak_log'), anvil.Block('minecraft', 'oak_planks')],
    point=(500, 160, 200),
    size=(20, 30, 20)
)
world.apply(spiral.filled())
```

### Pattern Methods

All pattern classes inherit from `Figure` and provide two main methods:

- **`filled()`**: Returns a dictionary of all blocks in the filled structure
- **`empty()`**: Returns a dictionary of only the outer shell blocks (hollow structure)

The `world.apply(dict)` method places all blocks from the pattern dictionary into the world.

## Biome Operations

### Get and Set Biomes

```python
import anvil
from anvil import Biome

world = anvil.World('./my_world')

# Get biome at coordinates
biome = world.get_biome(100, 64, 200)
print(biome.name())  # e.g., "minecraft:plains"

# Set a single biome
world.set_biome(Biome('desert'), 100, 64, 200)

# Create biome from namespace
custom_biome = Biome('minecraft', 'cherry_grove')
world.set_biome(custom_biome, 150, 64, 250)
```

### Replace Biomes in Area

```python
# Replace all desert biomes with plains in a specific area
count = world.replace_biomes(
    "minecraft:desert",
    "minecraft:plains",
    bounds=(0, 60, 0, 200, 80, 200)
)
print(f"Replaced {count} biome blocks")

# Replace biomes without bounds (entire loaded world)
count = world.replace_biomes("minecraft:ocean", "minecraft:deep_ocean")
```

## Block Search and Detection

### Find Blocks

```python
# Find up to 10 diamond ore blocks
positions = world.find_blocks("minecraft:diamond_ore", limit=10)
for x, y, z in positions:
    print(f"Diamond ore at ({x}, {y}, {z})")

# Find blocks in a specific area
positions = world.find_blocks(
    "minecraft:ancient_debris",
    bounds=(0, 8, 0, 100, 20, 100),
    limit=5
)
```

### Find Nearest Block

```python
# Find nearest diamond ore from a position
result = world.find_nearest_block("minecraft:diamond_ore", 100, 64, 200, max_radius=50)
if result:
    x, y, z, distance = result
    print(f"Nearest diamond at ({x}, {y}, {z}), {distance:.2f} blocks away")
else:
    print("No diamond ore found within 50 blocks")
```

### Scan Area for Block Distribution

```python
# Get all block types and their counts in an area
distribution = world.scan_area(0, 60, 0, 16, 80, 16)
for block_name, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
    print(f"{block_name}: {count}")
```

## Area Operations

### Fill Area

```python
# Fill a cubic area with stone
count = world.fill_area("minecraft:stone", 0, 64, 0, 10, 74, 10)
print(f"Placed {count} blocks")

# Create a platform
world.fill_area("minecraft:oak_planks", 100, 64, 100, 120, 64, 120)
```

### Copy Area

```python
# Copy a structure from one location to another
count = world.copy_area(
    0, 64, 0, 10, 74, 10,    # Source bounds (x1, y1, z1, x2, y2, z2)
    100, 64, 100              # Destination start point (to_x, to_y, to_z)
)
print(f"Copied {count} blocks")
```

### Clear Area

```python
# Clear an area (replace with air)
count = world.clear_area(0, 64, 0, 10, 74, 10)
print(f"Cleared {count} blocks")
```

## Replace Blocks

### Replace Underwater Blocks Example

```python
import anvil
from anvil import Block

world = anvil.World('./my_world')

# Define search area
area_bounds = (0, -64, 0, 100, 100, 100)

print("Looking for underwater blocks...")
replaced_count = 0

# Stream through all blocks in the area
for x, y, z, block in world.stream_blocks(*area_bounds):
    if block is None:
        continue
    
    # Skip if current block is water
    if block.name() == "minecraft:water":
        continue
    
    # Check if block above is water
    block_above = world.get_block(x, y + 1, z)
    
    if block_above and block_above.name() == "minecraft:water":
        # Replace with desired block
        world.set_block(Block('minecraft', 'prismarine'), x, y, z)
        replaced_count += 1

print(f"Replaced {replaced_count} underwater blocks!")
world.save()
```

---

# Advanced World Features

The `World` class includes powerful features for statistics, memory management, and streaming operations.

## World Statistics

```python
# Get comprehensive world information
info = world.get_world_info()
print(f"World folder: {info['world_folder']}")
print(f"Loaded regions: {info['loaded_regions']}")
print(f"World size: {info['size_x']} x {info['size_z']}")
   
# Get block distribution
top_blocks = world.get_block_distribution(top_n=10)
for block_name, count in top_blocks.items():
    print(f"{block_name}: {count:,}")

# Get height at coordinates
height = world.get_height_map(100, 200)
print(f"Surface at (100, 200): Y={height}")

# Count specific blocks in an area
stone_count = world.count_blocks("minecraft:stone", bounds=(0, 0, 0, 100, 100, 100))
print(f"Stone blocks: {stone_count:,}")
```

## Stream Blocks

```python
# Stream through blocks efficiently without loading everything into memory
for x, y, z, block in world.stream_blocks(0, 0, 0, 1000, 100, 1000):
    if block.name() == "minecraft:diamond_ore":
        print(f"Found diamond ore at ({x}, {y}, {z})")
```

## Memory Management

```python
# Check memory usage
stats = world.get_memory_usage()
print(f"Loaded regions: {stats['loaded_regions']}")
print(f"Cached chunks: {stats['cached_chunks']}")

# Unload a specific region
world.unload_region(0, 0, save=True)

# Unload all regions
count = world.unload_all_regions(save=True)
print(f"Unloaded {count} regions")

# Clear chunk cache
world.clear_cache()
```

## Performance Tips

```python
world = anvil.World(
    './my_world',
    chunk_cache_size=1024,  # Cache up to 1024 chunks
    region_cache_size=64     # Cache up to 64 regions
)

world = anvil.World('./my_world', chunk_cache_size=None, region_cache_size=None)

positions = world.find_blocks(
    "minecraft:diamond_ore",
    bounds=(0, -64, 0, 100, 20, 100),  # Only search this area
    limit=10  # Stop after finding 10
)

for x, y, z, block in world.stream_blocks(0, 0, 0, 1000, 100, 1000):
    if block.name() == "minecraft:diamond_ore":
        print(f"Found at ({x}, {y}, {z})")
```

## Replace Underwater Blocks

Here's a practical example showing how to replace all blocks that are underwater (below water blocks):

```python
import anvil
from anvil import Block

world = anvil.World(r'C:\path\to\your\minecraft\world')

area_bounds = (0, -64, 0, 100, 100, 100)

print("Looking for underwater blocks...")

replaced_count = 0

for x, y, z, block in world.stream_blocks(*area_bounds):
    if block is None:
        continue
    
    current_block_name = block.name()
    
    if current_block_name == "minecraft:water":
        continue
    
    block_above = world.get_block(x, y + 1, z)
    
    if block_above and block_above.name() == "minecraft:water":
        world.set_block(Block('minecraft', 'bedrock'), x, y, z)
        replaced_count += 1
        if replaced_count <= 10:  
            print(f"Replaced {current_block_name} with bedrock at ({x}, {y}, {z})")

if replaced_count > 10:
    print(f"... and {replaced_count - 10} more blocks")

print(f"Replaced {replaced_count} underwater blocks!")

print("Saving world...")
world.save()
print("Done!")
```

## Working with Dimensions

The library supports all three Minecraft dimensions: **Overworld**, **Nether** (DIM-1), and **The End** (DIM1).

### Creating World Instances for Different Dimensions

```python
import anvil
from anvil import Block

world_path = r'C:\path\to\your\minecraft\world'

# Overworld (default)
overworld = anvil.World(world_path)
# or explicitly
overworld = anvil.World(world_path, dimension='overworld')

# Nether
nether = anvil.World(world_path, dimension='nether')

# The End
end = anvil.World(world_path, dimension='end')

# Work with each dimension independently
overworld.set_block(Block('minecraft', 'grass_block'), 100, 64, 100)
nether.set_block(Block('minecraft', 'netherrack'), 100, 64, 100)
end.set_block(Block('minecraft', 'end_stone'), 100, 64, 100)

# Save each dimension
overworld.save()
nether.save()
end.save()
```

### Switching Dimensions

```python
import anvil

world = anvil.World(r'C:\path\to\world', dimension='overworld')

# Get current dimension
print(f"Current dimension: {world.get_dimension()}")

# Switch to Nether (saves current dimension first)
world.switch_dimension('nether', save_current=True)

# Get dimension info
info = world.get_dimension_info()
print(f"Dimension: {info['name']}")
print(f"Path: {info['path']}")
print(f"Loaded regions: {info['loaded_regions']}")

# Switch to The End
world.switch_dimension('end')
```

### Nether Portal Coordinates

Nether coordinates are 1/8 of Overworld coordinates (X and Z only):

```python
# Overworld coordinates
overworld_x, overworld_z = 800, 800

# Corresponding Nether coordinates
nether_x = overworld_x // 8  # 100
nether_z = overworld_z // 8  # 100

# Set portal markers
overworld = anvil.World(world_path, dimension='overworld')
nether = anvil.World(world_path, dimension='nether')

overworld.set_block(Block('minecraft', 'obsidian'), overworld_x, 64, overworld_z)
nether.set_block(Block('minecraft', 'obsidian'), nether_x, 64, nether_z)
```

---

# OrbisPanora Functionalities

This section documents features added post-fork to enhance the library with advanced world manipulation capabilities.

## Patterns

The library includes geometric pattern generators for creating complex structures easily. All patterns support both filled and hollow variants.

### Available Patterns

- **Cube**: Rectangular box structures
- **Pyramid**: Stepped pyramid structures  
- **Sphere**: Spherical/ellipsoid structures
- **Spiral**: Helical spiral structures

### Using Patterns

```python
import anvil
from patterns import Cube, Pyramid, Sphere, Spiral

world = anvil.World('./my_world')

# Create a filled cube
cube = Cube(
    blocks=[anvil.Block('minecraft', 'diamond_block'), anvil.Block('minecraft', 'gold_block')],
    point=(200, 160, 200),
    size=(10, 10, 10)
)
world.apply(cube.filled())

# Create a hollow cube
hollow_cube = Cube(
    blocks=[anvil.Block('minecraft', 'glass')],
    point=(220, 160, 200),
    size=(15, 15, 15)
)
world.apply(hollow_cube.empty())

# Create a pyramid
pyramid = Pyramid(
    blocks=[anvil.Block('minecraft', 'sandstone'), anvil.Block('minecraft', 'smooth_sandstone')],
    point=(300, 160, 200),
    size=(21, 11, 21)
)
world.apply(pyramid.filled())

# Create a sphere
sphere = Sphere(
    blocks=[anvil.Block('minecraft', 'sea_lantern')],
    point=(400, 160, 200),
    size=(20, 20, 20)
)
world.apply(sphere.filled())

# Create a spiral
spiral = Spiral(
    blocks=[anvil.Block('minecraft', 'oak_log'), anvil.Block('minecraft', 'oak_planks')],
    point=(500, 160, 200),
    size=(20, 30, 20)
)
world.apply(spiral.filled())
```

### Pattern Methods

All pattern classes inherit from `Figure` and provide:

- **`filled()`**: Returns a dictionary of all blocks in the filled structure
- **`empty()`**: Returns a dictionary of only the outer shell blocks (hollow structure)

The `world.apply(dict)` method places all blocks from the pattern dictionary into the world.

## Biome Operations

### Get and Set Biomes

```python
import anvil
from anvil import Biome

world = anvil.World('./my_world')

# Get biome at coordinates
biome = world.get_biome(100, 64, 200)
print(biome.name())  # e.g., "minecraft:plains"

# Set a single biome
world.set_biome(Biome('desert'), 100, 64, 200)

# Create biome from namespace
custom_biome = Biome('minecraft', 'cherry_grove')
world.set_biome(custom_biome, 150, 64, 250)
```

### Replace Biomes

```python
# Replace all desert biomes with plains in a specific area
count = world.replace_biomes(
    "minecraft:desert",
    "minecraft:plains",
    bounds=(0, 60, 0, 200, 80, 200)
)
print(f"Replaced {count} biome blocks")

# Replace biomes without bounds (entire loaded world)
count = world.replace_biomes("minecraft:ocean", "minecraft:deep_ocean")
```

## Block Replacement Functions

### Replace Block at Position

```python
# Replace a single block at specific coordinates
success = world.replace_block_at(100, 64, 200, "minecraft:diamond_block")
if success:
    print("Block replaced successfully")
```

### Replace All Blocks

```python
# Replace all occurrences of a block type in the entire world
count = world.replace_blocks("minecraft:stone", "minecraft:dirt")
print(f"Replaced {count} blocks")

# Replace blocks in a specific area
count = world.replace_blocks(
    "minecraft:oak_log",
    "minecraft:birch_log",
    bounds=(0, 60, 0, 100, 70, 100)
)
print(f"Replaced {count} blocks in the area")

# Replace blocks using Block objects
old_block = anvil.Block('minecraft', 'water')
new_block = anvil.Block('minecraft', 'ice')
count = world.replace_blocks(old_block, new_block, bounds=(0, 0, 0, 100, 100, 100))
```

### Replace Blocks in Area

```python
# Convenience method with explicit coordinates
count = world.replace_blocks_in_area(
    "minecraft:grass_block",
    "minecraft:mycelium",
    x1=0, y1=60, z1=0,
    x2=100, y2=70, z2=100
)
print(f"Replaced {count} blocks")
```

## Structure Support

Load and place Minecraft structure files (`.nbt` format) into your world.

### Loading Structures

```python
from anvil import Structure

# Load a structure from file
structure = Structure.from_file("path/to/structure.nbt")

# Get structure information
print(f"Structure size: {structure.size}")
print(f"Number of blocks: {len(structure.blocks)}")
print(f"Number of entities: {len(structure.entities)}")
```

### Placing Structures

```python
import anvil
from anvil import Structure

world = anvil.World('./my_world')

# Load structure
house = Structure.from_file("structures/house.nbt")

# Place structure at coordinates
world = house.generate_in_world(world, x=100, y=64, z=200)

# Save the world
world.save()
```

## Cache Management

The library includes an LRU cache system for efficient memory management when working with large worlds.

### Configuring Cache

```python
# Initialize world with custom cache sizes
world = anvil.World(
    './my_world',
    chunk_cache_size=1024,   # Cache up to 1024 chunks
    region_cache_size=64      # Cache up to 64 regions
)

# Disable caching entirely
world = anvil.World(
    './my_world',
    chunk_cache_size=None,
    region_cache_size=None
)
```

### Cache Operations

```python
# Get cache statistics
stats = world.get_cache_stats()
print(f"Chunk cache hits: {stats['chunk_cache']['hits']}")
print(f"Chunk cache misses: {stats['chunk_cache']['misses']}")
print(f"Current cache size: {stats['chunk_cache']['size']}")

# Clear all caches
world.clear_cache()

# Invalidate specific chunks/regions
world.invalidate_chunk(chunk_x=10, chunk_z=20)
world.invalidate_region(region_x=0, region_z=0)
```

### Cache Manager

The `CacheManager` class provides thread-safe LRU caching:

- Automatically evicts least recently used items when full
- Tracks cache hits and misses for performance analysis
- Thread-safe for concurrent operations
- Configurable maximum size
