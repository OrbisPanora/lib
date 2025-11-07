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