# Orbis Panora library

A Python library designed to read, modify, and write **Minecraft world save files** (Anvil and NBT formats). It provides an object-oriented interface for easy access to **chunks, blocks, entities, and biomes**.

## 🔗 Project Origin 

`anvil-parser2` is a **fork** of **0xTiger's anvil-parser**, which itself was originally forked from [matcool's anvil-parser](https://github.com/matcool/anvil-parser). The initial fork by 0xTiger aimed to add support for Minecraft versions **1.18 and above**. Our current version continues this development as the core data layer for a larger project that includes a REST API and a web-based isometric viewer.

---

## 💡 Usage

### Reading Data

```python
import anvil

region = anvil.Region.from_file('tests/r.0.0.mca')

# Get a chunk at region coordinates 0, 0
chunk = anvil.Chunk.from_region(region, 0, 0)

# Get a block at local coordinates 0, 0, 0
# If `section` is not provided, it will be derived from the y-coordinate.
block = chunk.get_block(0, 0, 0)

print(block)  # <Block(minecraft:air)>
print(block.id)  # air
print(block.properties)  # {}
```

### Creating Regions
```python
import anvil
from random import choice

# Create a new EmptyRegion object at region coordinates (0, 0)
region = anvil.EmptyRegion(0, 0)

# Create Block objects used for setting blocks
stone = anvil.Block('minecraft', 'stone')
dirt = anvil.Block('minecraft', 'dirt')

# Fill a 16x16x16 cube with either stone or dirt blocks
for y in range(16):
    for z in range(16):
        for x in range(16):
            region.set_block(choice((stone, dirt)), x, y, z)

# Sa`e to a file
region.save('r.0.0.mca')
```