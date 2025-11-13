import _path
import anvil

# Simple test to verify set_block
world_path = r'your_path'
print(f"Opening world: {world_path}")

word = anvil.World(world_path)

# Test coordinates
x, y, z = 160, 64, 160

print(f"\nTesting at coordinates ({x}, {y}, {z})")

# Calculate region and chunk coordinates
region_x = x >> 9
region_z = z >> 9
chunk_x = x >> 4
chunk_z = z >> 4
print(f"Region: ({region_x}, {region_z})")
print(f"Chunk: ({chunk_x}, {chunk_z})")

# Get the region
region = word.get_region(region_x, region_z)
print(f"Region type: {type(region).__name__}")
# Try to place a block
print(f"\nPlacing a glowstone block...")
block = anvil.Block('minecraft', 'glowstone')
word.set_block(block, x, y, z)
# Verify if the block was placed
print(f"\nVerifying placed block...")
placed_block = word.get_block(x, y, z)
if placed_block:
    print(f"Block found: {placed_block.name()}")
else:
    print(f"No block found!")
# Save
print(f"\nSaving world...")
word.save()
print(f"\nTest completed!")
