from anvil import Region, Block

# Load region file
region = Region.from_file('r.0.0.mca')
chunk = region.get_chunk(0, 0)

# Test 1: Replace single block via chunk
print("Test 1: Replace single block at (5, 64, 10) via chunk")
success = chunk.replace_block_at(5, 64, 10, "minecraft:diamond_block")
print(f"Success: {success}")
print(f"Block after: {chunk.get_block(5, 64, 10)}")

# Test 2: Replace all dirt with diamond blocks via chunk
print("\nTest 2: Replace all dirt with diamond blocks via chunk")
count = chunk.replace_blocks("minecraft:dirt", "minecraft:diamond_block")
print(f"Blocks replaced: {count}")

# Test 3: Replace single block via region (NEW)
print("\nTest 3: Replace single block at global (100, 64, 200) via region")
success = region.replace_block_at(100, 64, 200, "minecraft:gold_block", 'r.0.0_modified.mca')
print(f"Success: {success}")

# Verify the block was replaced - reload the region from the modified file
modified_region = Region.from_file('r.0.0_modified.mca')
chunk_x = 100 >> 4
chunk_z = 200 >> 4
local_x = 100 & 15
local_z = 200 & 15
test_chunk = modified_region.get_chunk(chunk_x % 32, chunk_z % 32)
print(f"Block after: {test_chunk.get_block(local_x, 64, local_z)}")

# Test 4: Replace block with Block object
print("\nTest 4: Replace block using Block object")
diamond_block = Block.from_name("minecraft:diamond_block")
success = modified_region.replace_block_at(105, 65, 205, diamond_block, 'r.0.0_modified.mca')
print(f"Success: {success}")

# Reload to verify Test 4
final_region = Region.from_file('r.0.0_modified.mca')
chunk_x2 = 105 >> 4
chunk_z2 = 205 >> 4
local_x2 = 105 & 15
local_z2 = 205 & 15
test_chunk2 = final_region.get_chunk(chunk_x2 % 32, chunk_z2 % 32)
print(f"Block after Test 4: {test_chunk2.get_block(local_x2, 65, local_z2)}")

print("\nAll tests completed!")
