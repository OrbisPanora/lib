import _path
import sys
import os

import anvil
from anvil import Block
from config import WORLD_PATH, validate_world_path

# Validate configuration
is_valid, message = validate_world_path()
if not is_valid:
    print(f"\n⚠ Error: {message}")
    print("\nPlease configure WORLD_PATH in examples/config.py")
    print("Then run this script again.")
    exit(1)

# Path to your Minecraft save
world_path = WORLD_PATH

print("=" * 60)
print("TEST: Nether Modification")
print("=" * 60)

# Create a World instance for the Nether
nether = anvil.World(world_path, dimension='nether')

# Target coordinates
x, y, z = -3, 42, 11

print(f"\nTarget coordinates: X={x}, Y={y}, Z={z}")
print(f"Dimension: {nether.get_dimension()}")
print(f"Region dir: {nether.region_dir}")

# 1. Read the current block
print(f"\n1. Reading current block at ({x}, {y}, {z})...")
current_block = nether.get_block(x, y, z)
if current_block:
    print(f"Current block: {current_block.name()}")
else:
    print("No block found (chunk may not be generated)")

# 2. Place a diamond block
print(f"\n2. Placing a diamond block at ({x}, {y}, {z})...")
nether.set_block(Block('minecraft', 'diamond_block'), x, y, z)
print("Block placed")

# 3. Verify the placement
print(f"\n3. Verifying placement...")
new_block = nether.get_block(x, y, z)
if new_block:
    print(f"New block: {new_block.name()}")
    if new_block.name() == 'minecraft:diamond_block':
        print("Success!")
    else:
        print("Warning: Block is not the expected one")
else:
    print("Warning: Cannot read block")

# 4. Place some blocks around for testing
print(f"\n4. Placing blocks around...")
blocks_to_place = [
    (x+1, y, z, 'gold_block'),
    (x-1, y, z, 'iron_block'),
    (x, y+1, z, 'emerald_block'),
    (x, y-1, z, 'netherrack'),
    (x, y, z+1, 'glowstone'),
    (x, y, z-1, 'soul_sand'),
]

for bx, by, bz, block_type in blocks_to_place:
    nether.set_block(Block('minecraft', block_type), bx, by, bz)
    print(f"Placed {block_type} at ({bx}, {by}, {bz})")

# 5. Save
print(f"\n5. Saving world...")
nether.save()
print("World saved")

# 6. Display information
print(f"\n6. Dimension information:")
info = nether.get_dimension_info()
print(f"Name: {info['name']}")
print(f"Path: {info['path']}")
print(f"Loaded regions: {info['loaded_regions']}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
print("\nInstructions:")
print("1. Launch Minecraft")
print("2. Load the world 'New World test sde fdp'")
print("3. Go to the Nether")
print("4. Teleport to coordinates: /tp @s -3 42 11")
print("5. You should see a diamond block and colored blocks around it!")
print("\nTeleport command:")
print(f"/tp @s {x} {y} {z}")
