"""
Demonstration of advanced World class features
Shows all the new functionality added to the World class
"""
import _path
import anvil
from anvil import Block, Biome

print("=" * 60)
print("WORLD CLASS - ADVANCED FEATURES DEMO")
print("=" * 60)

world_path = r'yourpath'
world = anvil.World(world_path, chunk_cache_size=512, region_cache_size=32)

print("\n1. WORLD INFORMATION")
print("-" * 60)
info = world.get_world_info()
print(f"World folder: {info['world_folder']}")
print(f"Loaded regions: {info['loaded_regions']}")
print(f"Region coordinates: {info['region_coordinates'][:3]}...")  
print(f"World bounds: {info['bounds']}")
print(f"Size X: {info['size_x']} blocks")
print(f"Size Z: {info['size_z']} blocks")
print(f"Cache enabled: {info['cache_enabled']}")

print("\n2. BIOME MANAGEMENT")
print("-" * 60)
biome = world.get_biome(100, 64, 200)
if biome:
    print(f"Biome at (100, 64, 200): {biome.name()}")


print("\n3. SEARCH AND SCAN")
print("-" * 60)
print("Searching for diamond ore (limit 5)...")
positions = world.find_blocks("minecraft:diamond_ore", 
                              bounds=(0, -64, 0, 100, 20, 100), 
                              limit=5)
print(f"Found {len(positions)} diamond ore blocks:")
for x, y, z in positions[:3]:
    print(f"  - Position: ({x}, {y}, {z})")

print("\nSearching for nearest stone from (100, 64, 200)...")
result = world.find_nearest_block("minecraft:stone", 100, 64, 200, max_radius=50)
if result:
    x, y, z, distance = result
    print(f"  Found at ({x}, {y}, {z}), distance: {distance:.2f} blocks")

print("\nScanning area (100, 60, 100) to (116, 70, 116)...")
distribution = world.scan_area(100, 60, 100, 116, 70, 116)
print(f"Found {len(distribution)} different block types:")
for block_name, count in list(distribution.items())[:5]:
    print(f"  - {block_name}: {count}")

print("\n4. STATISTICS")
print("-" * 60)
print("Top 10 most common blocks in loaded world:")
top_blocks = world.get_block_distribution(top_n=10)
for i, (block_name, count) in enumerate(top_blocks.items(), 1):
    print(f"  {i}. {block_name}: {count:,} blocks")

stone_count = world.count_blocks("minecraft:stone", bounds=(0, 0, 0, 100, 100, 100))
print(f"\nStone blocks in (0,0,0) to (100,100,100): {stone_count:,}")

print("\nHeight map samples:")
for x, z in [(100, 100), (150, 150), (200, 200)]:
    height = world.get_height_map(x, z)
    if height:
        print(f"  Surface at ({x}, {z}): Y={height}")

print("\n5. MEMORY MANAGEMENT")
print("-" * 60)
memory_stats = world.get_memory_usage()
print(f"Loaded regions: {memory_stats['loaded_regions']}")
print(f"Cached chunks: {memory_stats['cached_chunks']}")
print(f"Cached regions: {memory_stats['cached_regions']}")

cache_stats = memory_stats['cache_stats']
if cache_stats['chunk_cache']:
    chunk_cache = cache_stats['chunk_cache']
    print(f"\nChunk cache:")
    print(f"  Size: {chunk_cache['size']}/{chunk_cache['max_size']}")
    print(f"  Hits: {chunk_cache['hits']}")
    print(f"  Misses: {chunk_cache['misses']}")
    print(f"  Hit rate: {chunk_cache['hit_rate']}")

success = world.unload_region(0, 0, save=True)
print(f"Unloaded region (0, 0): {success}")

print("\n6. AREA OPERATIONS")
print("-" * 60)
print("Area operations available:")
print("  - copy_area(): Copy blocks from one area to another")
print("  - fill_area(): Fill an area with a specific block")
print("  - clear_area(): Clear an area (fill with air)")


print("\n7. STREAMING OPERATIONS")
print("-" * 60)
print("Streaming blocks in area (100, 64, 100) to (105, 69, 105)...")
block_count = 0
for x, y, z, block in world.stream_blocks(100, 64, 100, 105, 69, 105):
    block_count += 1
print(f"Streamed {block_count} blocks")

print("\nStreaming chunks in area (0, 0) to (32, 32)...")
chunk_count = 0
for chunk_x, chunk_z, chunk in world.stream_chunks(0, 0, 32, 32):
    if chunk:
        chunk_count += 1
print(f"Streamed {chunk_count} chunks")

print("\n8. CACHE OPERATIONS")
print("-" * 60)
print("Cache operations available:")
print("  - clear_cache(): Clear all caches")
print("  - get_cache_stats(): Get cache statistics")
print("  - invalidate_chunk(): Invalidate specific chunk")
print("  - invalidate_region(): Invalidate specific region")

stats = world.get_cache_stats()
print(f"\nCurrent cache stats:")
print(f"  Chunk cache: {stats['chunk_cache']}")
print(f"  Region cache: {stats['region_cache']}")

print("\n" + "=" * 60)
print("DEMO COMPLETE - All features demonstrated!")
print("=" * 60)
print("\nTips:")
print("  - Use bounds parameter to limit operations to specific areas")
print("  - Use limit parameter in searches to avoid long operations")
print("  - Monitor memory usage with get_memory_usage()")
print("  - Unload regions when done to free memory")
print("  - Always save before unloading if you made changes")
