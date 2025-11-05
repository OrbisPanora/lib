from anvil import Region, Block

# Load region file
region = Region.from_file('r.0.0.mca')
chunk = region.get_chunk(0, 0)

# Replace single block
print("Test 1: Replace single block at (5, 64, 10)")
success = chunk.replace_block_at(5, 64, 10, "minecraft:diamond_block")
print(f"Success: {success}")
print(f"Block after: {chunk.get_block(5, 64, 10)}")

# Replace all dirt with diamond blocks
print("\nTest 2: Replace all dirt with diamond blocks")
count = chunk.replace_blocks("minecraft:dirt", "minecraft:diamond_block")
print(f"Blocks replaced: {count}")

# Save changes
print("\nSaving chunk...")
region.save_chunk(chunk, 'r.0.0_modified.mca')
print("Chunk saved to r.0.0_modified.mca!")