# Orbis Panora library

A Python library designed to read, modify, and write **Minecraft world save files** (Anvil and NBT formats). It provides an object-oriented interface for easy access to **chunks, blocks, entities, and biomes**.

## 🔗 Project Origin 

`anvil-parser2` is a **fork** of **0xTiger's anvil-parser**, which itself was originally forked from [matcool's anvil-parser](https://github.com/matcool/anvil-parser). The initial fork by 0xTiger aimed to add support for Minecraft versions **1.18 and above**. Our current version continues this development as the core data layer for a larger project that includes a REST API and a web-based isometric viewer.

---

# 💡 Usage

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

## test patterns (a bit slow)

```python
import anvil
import pattern

# link to the world folder (the one in "/saves")
path = './testop2'

# retrieve the world
word = anvil.World(path)

# create a cube
cube = pattern.Cube(blocks = [anvil.Block('minecraft', 'diamond_block'), anvil.Block('minecraft', 'iron_block')], point = (200, 160, 200), size = (3,3,3))
# retrieve the coordinates for each block to place
dictblockcube = cube.filled()
# place these blocks in the world
word.apply(dictblockcube)

# pyramid
pyramid = pattern.Pyramid(blocks = [anvil.Block('minecraft', 'sandstone'), anvil.Block('minecraft', 'iron_block')], point = (300, 160, 200), size = (18, 9, 18))
dictblockpyramid = pyramid.filled()
word.apply(dictblockpyramid)

# spiral
spiral = pattern.Spiral(blocks = [anvil.Block('minecraft', 'oak_log'), anvil.Block('minecraft', 'iron_block')], point = (200, 160, 300), size = (18, 30, 18))
dictblockspiral = spiral.filled()
word.apply(dictblockspiral)
```

---

# Advanced World Features

The `World` class now includes powerful features for biome management, search, statistics, and area operations.

## Biome Management

```python
import anvil
from anvil import Biome

world = anvil.World('./my_world')

biome = world.get_biome(100, 64, 200)
print(biome.name())  # e.g., "minecraft:plains"

world.set_biome(Biome('desert'), 100, 64, 200)

count = world.replace_biomes(
    "minecraft:desert", 
    "minecraft:plains",
    bounds=(0, 60, 0, 100, 70, 100)
)
print(f"Replaced {count} biomes")
```

## Search and Scan

```python
positions = world.find_blocks("minecraft:diamond_ore", limit=10)
for x, y, z in positions:
    print(f"Diamond ore at ({x}, {y}, {z})")

result = world.find_nearest_block("minecraft:diamond_ore", 100, 64, 200, max_radius=50)
if result:
    x, y, z, distance = result
    print(f"Nearest diamond at ({x}, {y}, {z}), {distance:.2f} blocks away")
distribution = world.scan_area(0, 60, 0, 16, 70, 16)
for block_name, count in distribution.items():
    print(f"{block_name}: {count}")
```

## World Statistics

```python
info = world.get_world_info()
print(f"World folder: {info['world_folder']}")
print(f"Loaded regions: {info['loaded_regions']}")
print(f"World size: {info['size_x']} x {info['size_z']}")
   
top_blocks = world.get_block_distribution(top_n=10)
for block_name, count in top_blocks.items():
    print(f"{block_name}: {count:,}")

height = world.get_height_map(100, 200)
print(f"Surface at (100, 200): Y={height}")

stone_count = world.count_blocks("minecraft:stone", bounds=(0, 0, 0, 100, 100, 100))
print(f"Stone blocks: {stone_count:,}")
```

## 🏗️ Area Operations

```python
count = world.fill_area("minecraft:stone", 0, 64, 0, 10, 74, 10)
print(f"Placed {count} blocks")

count = world.copy_area(
    0, 64, 0, 10, 74, 10,  # Source (from)
    100, 64, 100            # Destination (to)
)
print(f"Copied {count} blocks")

count = world.clear_area(0, 64, 0, 10, 74, 10)
print(f"Cleared {count} blocks")
```

## Memory Management

```python
stats = world.get_memory_usage()
print(f"Loaded regions: {stats['loaded_regions']}")
print(f"Cached chunks: {stats['cached_chunks']}")

world.unload_region(0, 0, save=True)

count = world.unload_all_regions(save=True)
print(f"Unloaded {count} regions")
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
