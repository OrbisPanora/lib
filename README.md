# Orbis Panora library

A Python library designed to read, modify, and write **Minecraft world save files** (Anvil and NBT formats). It provides an object-oriented interface for easy access to **chunks, blocks, entities, and biomes**.

## Project Origin 

`anvil-parser2` is a **fork** of **0xTiger's anvil-parser**, which itself was originally forked from [matcool's anvil-parser](https://github.com/matcool/anvil-parser). The initial fork by 0xTiger aimed to add support for Minecraft versions **1.18 and above**. Our current version continues this development as the core data layer for a larger project that includes a REST API and a web-based isometric viewer.

## Installation
You can install the library using pip:

```bash
cd lib
pip install .
```
## Usage

### Chunk Manipulation
#### Loading a Chunk

```python
from anvil import Region, Chunk

# Load a region
region = Region.from_file('region/r.0.0.mca')

# Get a specific chunk
chunk = region.get_chunk(0, 0)

# Or create a chunk directly from a region
chunk = Chunk.from_region('region/r.0.0.mca', 0, 0)

print(f"Chunk position: ({chunk.x}, {chunk.z})")
print(f"Version: {chunk.version}")
```

#### Reading Blocks

```python
# Get a block at specific coordinates
block = chunk.get_block(5, 64, 10)
print(f"Block at (5, 64, 10): {block.id}")
print(f"Properties: {block.properties}")

# Get the palette of a section
palette = chunk.get_palette(section=4)  # Section Y=4
for block in palette:
    print(f"- {block.id}")

# Iterate through all blocks in a section
for block in chunk.stream_blocks(section=4):
    if block.id == 'minecraft:diamond_ore':
        print(f"Found diamond ore!")

# Iterate through all blocks in the chunk
for block in chunk.stream_chunk():
    if block.id == 'minecraft:chest':
        print(f"Found chest!")
```

#### Modifying Blocks

```python
from anvil import Block

# Replace a single block
chunk.replace_block_at(5, 64, 10, "minecraft:diamond_block")

# Or use a Block object
diamond = Block.from_name("minecraft:diamond_block")
chunk.replace_block_at(5, 64, 10, diamond)

# Replace all blocks of a type
count = chunk.replace_blocks("minecraft:dirt", "minecraft:grass_block")
print(f"Replaced {count} dirt blocks with grass")

# Set a block with custom properties
from nbt import nbt

block = Block("minecraft", "oak_stairs")
block.properties = nbt.TAG_Compound()
block.properties.tags.append(nbt.TAG_String(name="facing", value="north"))
block.properties.tags.append(nbt.TAG_String(name="half", value="top"))

chunk.set_block(block, 8, 65, 8)
```

#### Working with Biomes

```python
from anvil import Biome

# Get the biome at a position
biome = chunk.get_biome(8, 64, 8)
print(f"Biome: {biome}")

# Set the biome at a specific position
desert = Biome.from_name("minecraft:desert")
chunk.set_biome(desert, 8, 64, 8)

# Set the biome for the entire chunk (optimized)
plains = Biome.from_name("minecraft:plains")
chunk.set_chunk_biome(plains)
```

#### Heights and Surfaces

```python
# Get the surface height at a position
height = chunk.get_surface_height(8, 8)
print(f"Surface height at (8, 8): Y={height}")

# Generate a complete heightmap (16x16)
heightmap = chunk.to_heightmap()
for z in range(16):
    for x in range(16):
        print(f"{heightmap[z][x]:3d}", end=" ")
    print()

# Get only surface blocks 
surface_blocks = chunk.get_surface_blocks(include_biome=True)
for block_data in surface_blocks[:5]:  # Display first 5
    print(f"Position: ({block_data['x']}, {block_data['y']}, {block_data['z']})")
    print(f"Block: {block_data['block']}")
    print(f"Biome: {block_data.get('biome', 'N/A')}")
```

#### Tile Entities

```python
# Get a tile entity at a position
tile_entity = chunk.get_tile_entity(5, 64, 10)
if tile_entity:
    print(f"Tile entity type: {tile_entity['id']}")
    # Example for a chest
    if tile_entity['id'].value == 'minecraft:chest':
        items = tile_entity.get('Items', [])
        print(f"Chest contains {len(items)} items")

# Iterate through all tile entities in the chunk
for te in chunk.tile_entities:
    print(f"Tile entity at ({te['x']}, {te['y']}, {te['z']}): {te['id']}")
```

#### Sections

```python
# Get a specific section
section = chunk.get_section(y=4)  # Section Y=4 (height 64-79)
if section:
    print(f"Section Y=4 exists")
    palette = chunk.get_palette(section)
    print(f"Palette size: {len(palette)}")

# Create a new empty section
new_section = chunk.create_section(section_y=5)

# Add a block to a section's palette
from anvil import Block
section = chunk.get_section(4)
stone = Block.from_name("minecraft:stone")
palette_index = chunk.add_block_to_palette(section, stone)
print(f"Stone added at palette index: {palette_index}")
```

#### Saving Changes

```python
# Save the modified chunk
chunk.save('region/r.0.0.mca')

# Complete example of modification and saving
region = Region.from_file('region/r.0.0.mca')
chunk = region.get_chunk(0, 0)

# Replace all stone blocks with diamond
count = chunk.replace_blocks("minecraft:stone", "minecraft:diamond_block")
print(f"Replaced {count} stone blocks")

# Save
chunk.save()
print("Chunk saved successfully!")
```

### Export and Serialization

```python
# Convert to dictionary (lightweight, metadata + palette only)
chunk_data = chunk.to_dict(simplify=True)
print(f"Chunk at ({chunk_data['x']}, {chunk_data['z']})")
print(f"Sections: {len(chunk_data['sections'])}")

# Include all blocks (warning: very heavy, 500KB-2MB)
full_data = chunk.to_dict(simplify=False, include_blocks=True)

# Convert to JSON
import json
with open('chunk_data.json', 'w') as f:
    json.dump(chunk_data, f, indent=2)
```

### Region Manipulation

#### Loading a Region

```python
from anvil import Region

# Load a region from file (default cache: 64 chunks)
region = Region.from_file('region/r.0.0.mca')

# Custom cache size or disable caching
region = Region.from_file('region/r.0.0.mca', cache_size=128)  # 128 chunks
region = Region.from_file('region/r.0.0.mca', cache_size=None)  # No cache

print(f"Region: ({region.region_x}, {region.region_z})")
```

#### Getting Chunks

```python
# Get a chunk (returns None if not generated)
chunk = region.get_chunk(0, 0)

# Get chunk NBT data
nbt_data = region.chunk_data(5, 10)

# Check if chunk exists
offset, length = region.chunk_location(5, 10)
if offset == 0:
    print("Chunk not generated yet")
```

#### Cache Management

```python
# Get cache statistics
stats = region.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")

# Invalidate specific chunk or clear all
region.invalidate_chunk(0, 0)
region.clear_cache()
```

#### Modifying Blocks

```python
from anvil import Block

# Set block at global coordinates
region.set_block(Block.from_name("minecraft:diamond_block"), 100, 64, 200, 'r.0.0.mca')

# Replace single block
region.replace_block_at(100, 64, 200, "minecraft:gold_block", 'r.0.0.mca')

# Replace in one chunk
count = region.replace_blocks("minecraft:stone", "minecraft:dirt", 'r.0.0.mca', chunks=(5, 10))

# Replace in multiple chunks
count = region.replace_blocks("minecraft:oak_log", "minecraft:birch_log", 'r.0.0.mca',
                             chunks=[(0, 0), (1, 0), (0, 1)])

# Replace in entire region (don't do this it will take forever
count = region.replace_blocks("minecraft:sand", "minecraft:gravel", 'r.0.0.mca')
print(f"Replaced {count} blocks")
```

#### Saving

```python
# Save entire region
region.save('region/r.0.0.mca')

# Save specific chunk
chunk = region.get_chunk(0, 0)
# ... modify chunk ...
region.save_chunk(chunk)
```

#### Export to JSON

```python
import json

# Basic metadata
data = region.to_dict()

# Include chunk list
data = region.to_dict(include_chunks=True)
print(f"Chunks: {len(data['chunks'])}")

# Save to JSON
with open('region.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### World Manipulation

#### Loading a World

```python
from anvil import World

# Load a world (default: overworld, 512 chunk cache, 32 region cache) - the folder name is the name of your world not "region"
world = World('path/to/world')

# Custom cache sizes
world = World('path/to/world', chunk_cache_size=1024, region_cache_size=64)

# Load specific dimension
world = World('path/to/world', dimension='nether')  # 'overworld', 'nether', 'end'
```

#### Getting Blocks and Chunks

```python
# Get block at global coordinates
block = world.get_block(100, 64, -50)
print(f"Block: {block.id}")

# Get chunk
chunk = world.get_chunk(0, 0)

# Get region
region = world.get_region(0, 0)

# Get biome
biome = world.get_biome(100, 64, -50)
```

#### Modifying Blocks

```python
from anvil import Block

# Set single block
world.set_block(Block.from_name("minecraft:diamond_block"), 100, 64, -50)

# Replace single block
world.replace_block_at(100, 64, -50, "minecraft:gold_block")

# Replace in specific area
count = world.replace_blocks_in_area(
    "minecraft:stone", "minecraft:pumpkin",
    0, 60, 0, 100, 70, 100
)
print(f"Replaced {count} blocks")
```

#### Area Operations

```python
# Fill area with blocks
count = world.fill_area("minecraft:stone", 0, 64, 0, 10, 74, 10)

# Clear area (fill with air)
count = world.clear_area(0, 64, 0, 10, 74, 10)

# Copy area
count = world.copy_area(0, 64, 0, 10, 74, 10, 100, 64, 100)

# Scan area for block distribution
distribution = world.get_block_distribution(bounds= (0, 60, 0, 16, 70, 16))
for block_name, count in distribution.items():
    print(f"{block_name}: {count}")
```

#### Finding Blocks

```python
# Find all occurrences
positions = world.find_blocks("minecraft:diamond_ore", limit=10)
for x, y, z in positions:
    print(f"Found at ({x}, {y}, {z})")

# Find nearest block
result = world.find_nearest_block("minecraft:diamond_ore", 100, 64, 200, max_radius=100)
if result:
    x, y, z, distance = result
    print(f"Nearest at ({x}, {y}, {z}), distance: {distance:.2f}")

# Count blocks
count = world.count_blocks("minecraft:stone")
count_in_area = world.count_blocks("minecraft:dirt", (0, 60, 0, 100, 70, 100))
```

#### Block Analysis

```python
# Get block distribution
distribution = world.get_block_distribution(top_n=10)
for block_name, count in distribution.items():
    print(f"{block_name}: {count}")

# Get distribution in area
distribution = world.get_block_distribution(
    bounds=(0, 60, 0, 100, 70, 100),
    top_n=5
)
```

#### Biome Management

```python
from anvil import Biome

# Set biome at position (4x4x4 volume)
world.set_biome(Biome.from_name("minecraft:desert"), 100, 64, -50)

# Set entire chunk to one biome
world.set_chunk_biome(Biome.from_name("minecraft:plains"), 5, -3)

# Set entire region to one biome
world.set_region_biome(Biome.from_name("minecraft:ice_spikes"), 0, 0)
```

#### Heightmap and Terrain

```python
# Get height at position
height = world.get_height_map(100, 200)
print(f"Surface at Y={height}")

# Get heightmap for area
heightmap = world.get_area_heightmap(0, 0, 64, 64)
print(f"Size: {heightmap['width']}x{heightmap['height']}")
```

#### Streaming Data

```python
# Stream blocks in area
for x, y, z, block in world.stream_blocks(0, 60, 0, 10, 65, 10):
    if block.id == "minecraft:diamond_ore":
        print(f"Diamond at ({x}, {y}, {z})")

# Stream chunks in area
for chunk_x, chunk_z, chunk in world.stream_chunks(-10, -10, 10, 10):
    if chunk:
        print(f"Chunk at ({chunk_x}, {chunk_z})")
```

#### Chunk Data (for Viewer/API)

```python
# Get chunk data in different formats
heightmap_data = world.get_chunk_data(0, 0, mode='heightmap')  # ~1KB
surface_data = world.get_chunk_data(0, 0, mode='surface')      # ~10-50KB
simplified_data = world.get_chunk_data(0, 0, mode='simplified') # ~5KB
full_data = world.get_chunk_data(0, 0, mode='full')            # ~500KB-2MB

# Get tile data (16x16 chunks by default)
tile = world.get_tile_data(0, 0, tile_size=16)
print(f"Tile has {len(tile['chunks'])} chunks")
```

#### Dimensions

```python
# Get current dimension
dim = world.get_dimension()
print(f"Current: {dim}")

# Switch dimension
world.switch_dimension('nether')
world.switch_dimension('end', save_current=True)
world.switch_dimension('overworld')

# Get dimension info
info = world.get_dimension_info()
print(f"Path: {info['path']}")
```

#### Cache Management

```python
# Get cache statistics
stats = world.get_cache_stats()
print(f"Chunk cache hit rate: {stats['chunks']['hit_rate']:.2%}")
print(f"Region cache hit rate: {stats['regions']['hit_rate']:.2%}")

# Invalidate caches
world.invalidate_chunk(0, 0)
world.invalidate_region(0, 0)
world.clear_cache()

# Get memory usage
mem = world.get_memory_usage()
print(f"Loaded regions: {mem['loaded_regions']}")
print(f"Cached chunks: {mem['cached_chunks']}")
```

#### Region Management

```python
# Get loaded regions
regions = world.get_loaded_regions()
print(f"Loaded: {len(regions)} regions")

# Unload region
world.unload_region(0, 0, save=True)

# Unload all regions
count = world.unload_all_regions(save=True)
print(f"Unloaded {count} regions")
```

#### World Information

```python
# Get world bounds
bounds = world.get_world_bounds()
if bounds:
    min_x, min_y, min_z, max_x, max_y, max_z = bounds
    print(f"World size: {max_x - min_x}x{max_z - min_z} blocks")

# Get world info
info = world.get_world_info()
print(f"Folder: {info['world_folder']}")
print(f"Dimension: {info['dimension']}")
print(f"Loaded regions: {info['loaded_regions']}")
```

#### Saving

```python
# Save all modified regions
world.save()
```

### Patterns
The library includes geometric pattern generators that make it easy to create complex structures.

#### Available Patterns

Cube: Rectangular box structures
Pyramid: Stepped pyramid structures
Sphere: Spherical/ellipsoid structures
Spiral: Helical spiral structures

#### Using Patterns
```python
import anvil
from patterns import Cube, Pyramid, Spiral, Sphere
from nbt import nbt

WORLD_PATH = r'PATH_TO_YOUR_WORLD'
world = anvil.World(
    WORLD_PATH,
    chunk_cache_size=1024,  # Cache up to 1024 chunks
    region_cache_size=64    # Cache up to 64 regions
)

world.apply_figure(
    Pyramid,  # Choose your pattern (Cube, Pyramid, Sphere, Spiral)
    blocks=[anvil.Block('minecraft', 'lapis_block')],  # Choose any Minecraft block
    point=(-50, 100, -50),  # (x, y, z)
    size=(18, 9, 18),  # (width, height, length)
    filled=False  # False for hollow, True for solid
)
```

### Structure Manipulation
```python
from anvil import Structure

world_path = 'path/to/your/save/folder
structure_file = 'path/to/the/nbt-file' # ./plains_large_farm_1.nbt

structure = Structure.from_file(structure_file)

world = World(world_path)
world.create_structure(x, y, z, structure)

world.save()
```