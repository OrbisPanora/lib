import _path
import anvil
import time
import random
import os
from config import WORLD_PATH, validate_world_path

def print_header(title):
    print("\n" + "=" * 70)
    print(f"=== {title}".ljust(68) + "===")
    print("=" * 70)

def print_section(title):
    print(f"\n{title}")
    print("-" * len(title))

# Validate configuration
is_valid, message = validate_world_path()
if not is_valid:
    print(f"\n⚠ Error: {message}")
    print("\nPlease configure WORLD_PATH in examples/config.py")
    print("Then run this script again.")
    exit(1)

print_header("CACHE MANAGEMENT DEMONSTRATION")
print(f"Using world: {WORLD_PATH}")

# ===========================================================================
# 1. Initialization with and without cache
# ===========================================================================
print_section("1. Initialization with different cache settings")

# Without cache
world_no_cache = anvil.World(
    WORLD_PATH,
    chunk_cache_size=None,  # Disable chunk cache
    region_cache_size=None  # Disable region cache
)

# With medium cache sizes
world_with_cache = anvil.World(
    WORLD_PATH,
    chunk_cache_size=256,   # Cache up to 256 chunks
    region_cache_size=16     # Cache up to 16 regions
)

print("Initialization completed successfully!")
print(" - Without cache: chunk_cache=None, region_cache=None")
print(" - With cache: chunk_cache=256, region_cache=16")

# ===========================================================================
# 2. Basic performance demonstration
# ===========================================================================
print_section("2. Baseline performance comparison")

# Read test without cache
print("Reading 100 blocks (no cache):")
start = time.time()
for _ in range(10):
    for x in range(160, 170):
        for z in range(160, 170):
            block = world_no_cache.get_block(x, 64, z)
time_no_cache = (time.time() - start) * 1000
print(f"  Total time: {time_no_cache:.2f}ms")
print(f"  Average per block: {time_no_cache / 1000:.4f}ms")

# Read test with cache
print("\nReading the same 100 blocks (with cache):")
start = time.time()
for _ in range(10):
    for x in range(160, 170):
        for z in range(160, 170):
            block = world_with_cache.get_block(x, 64, z)
time_with_cache = (time.time() - start) * 1000
print(f"  Total time: {time_with_cache:.2f}ms")
print(f"  Average per block: {time_with_cache / 1000:.4f}ms")

# Show performance difference
speedup = time_no_cache / time_with_cache if time_with_cache > 0 else 0
print(f"\nResult: {speedup:.1f}x faster with cache!")
print(f"  Time saved: {time_no_cache - time_with_cache:.2f}ms")

# ===========================================================================
# 3. Cache statistics
# ===========================================================================
print_section("3. Cache statistics")

# Fetch statistics
stats = world_with_cache.get_cache_stats()
chunk_stats = stats['chunk_cache']
region_stats = stats['region_cache']

print("Chunk cache stats:")
print(f"  Size: {chunk_stats['size']}/{chunk_stats['max_size']}")
print(f"  Hits: {chunk_stats['hits']}")
print(f"  Misses: {chunk_stats['misses']}")
print(f"  Hit rate: {chunk_stats['hit_rate']}")

print("\nRegion cache stats:")
print(f"  Size: {region_stats['size']}/{region_stats['max_size']}")
print(f"  Hits: {region_stats['hits']}")
print(f"  Misses: {region_stats['misses']}")
print(f"  Hit rate: {region_stats['hit_rate']}")

# ===========================================================================
# 4. Cache management (public API + direct access)
# ===========================================================================
print_section("4. Cache management operations")

# a. Resize cache
print("a. Resizing chunk cache to 512")
world_with_cache._chunk_cache.resize(512)
stats = world_with_cache.get_cache_stats()['chunk_cache']
print(f"  New size: {stats['size']}/{stats['max_size']}")

# b. Invalidation via public API
print("\nb. Invalidation through the World API")
chunk_key = (10, 10)
region_coords = (chunk_key[0] >> 5, chunk_key[1] >> 5)
print(f"  Invalidating chunk {chunk_key} via world.invalidate_chunk()")
world_with_cache.invalidate_chunk(*chunk_key)

print(f"  Invalidating region {region_coords} via world.invalidate_region()")
world_with_cache.invalidate_region(*region_coords)

# Verify cache entries were cleared
chunk = world_with_cache._chunk_cache.get(chunk_key)
print(f"  Chunk {chunk_key} is {'still cached' if chunk else 'evicted'}")

region = None if world_with_cache._region_cache is None else world_with_cache._region_cache.get(region_coords)
print(f"  Region {region_coords} is {'still cached' if region else 'evicted'}")

# c. Clear caches via clear_cache()
print("\nc. Clearing caches via world.clear_cache()")
world_with_cache.clear_cache()
memory_stats = world_with_cache.get_memory_usage()
print(f"  Chunk cache after clear: {memory_stats['cached_chunks']}")
print(f"  Region cache after clear: {memory_stats['cached_regions']}")

# Demonstrate cache is empty by probing a chunk
test_chunk = (5, 5)
print(f"\n  Checking chunk {test_chunk}:")
chunk = world_with_cache._chunk_cache.get(test_chunk) if world_with_cache._chunk_cache else None
print(f"  Chunk {test_chunk} is {'still cached' if chunk else 'absent as expected'}")

# ===========================================================================
# 5. Standalone Region cache usage
# ===========================================================================
print_section("5. Region-level cache (direct usage)")
region_dir = os.path.join(WORLD_PATH, 'region')
region_files = [f for f in os.listdir(region_dir) if f.endswith('.mca')] if os.path.isdir(region_dir) else []

if not region_files:
    print("No .mca region files found, skipping this section.")
else:
    region_path = os.path.join(region_dir, region_files[0])
    print(f"Using region: {region_path}")
    region = anvil.Region.from_file(region_path, cache_size=4)

    # Find a real chunk within the region (skip missing ones)
    valid_chunk = None
    for cz in range(32):
        for cx in range(32):
            if region.chunk_location(cx, cz) != (0, 0):
                valid_chunk = (cx, cz)
                break
        if valid_chunk:
            break

    if not valid_chunk:
        print("This region has no generated chunks; skipping direct region cache demo.")
    else:
        print(f"Using chunk {valid_chunk} to populate the local cache...")
        for i in range(3):
            chunk = region.get_chunk(*valid_chunk)
            print(f"  Read #{i+1}: {'hit' if i else 'miss'} (chunk {'found' if chunk else 'missing'})")

        region_stats = region.get_cache_stats()
        print("Region cache stats:")
        if region_stats:
            print(f"  Size: {region_stats['size']}/{region_stats['max_size']}")
            print(f"  Hits/Misses: {region_stats['hits']}/{region_stats['misses']}")
            print(f"  Hit rate: {region_stats['hit_rate']}")
        else:
            print("  Cache disabled on this region.")

        print(f"Invalidating chunk {valid_chunk} via Region.invalidate_chunk()...")
        region.invalidate_chunk(*valid_chunk)
        region_after_invalidation = region.get_cache_stats()
        if region_after_invalidation:
            print(f"  Size after invalidation: {region_after_invalidation['size']}/{region_after_invalidation['max_size']}")

        print("Clearing the Region cache...")
        region.clear_cache()
        region_stats_after = region.get_cache_stats()
        if region_stats_after:
            print(f"  Cache cleared: {region_stats_after['size']} items remaining.")

# ===========================================================================
# 6. Load test with cache
# ===========================================================================
print_section("6. Load test with cache")

# Create a new world instance with smaller caches for stress testing
world_test = anvil.World(
    WORLD_PATH,
    chunk_cache_size=64,   # Small chunk cache for the test
    region_cache_size=8     # Small region cache
)

# Randomly read 1000 blocks
coords = [(random.randint(0, 511), random.randint(0, 255), random.randint(0, 511)) for _ in range(1000)]

# First pass (cache warm-up)
print("First pass (filling the cache):")
start = time.time()
for x, y, z in coords:
    block = world_test.get_block(x, y, z)
time_first_pass = time.time() - start

# Second pass (cache hits)
print("\nSecond pass (leveraging the cache):")
start = time.time()
for x, y, z in coords:
    block = world_test.get_block(x, y, z)
time_second_pass = time.time() - start

# Show results
print(f"\nResults:")
print(f"  First pass: {time_first_pass:.4f} seconds")
print(f"  Second pass: {time_second_pass:.4f} seconds")
speedup = time_first_pass / time_second_pass if time_second_pass > 0 else 0
print(f"  Speedup: {speedup:.1f}x faster once cached!")

# Show final stats
stats = world_test.get_cache_stats()
chunk_stats = stats['chunk_cache']
region_stats = stats['region_cache']

print("\nFinal cache stats:")
print(f"  Chunks: {chunk_stats['size']}/{chunk_stats['max_size']} (hit rate: {chunk_stats['hit_rate']})")
print(f"  Regions: {region_stats['size']}/{region_stats['max_size']} (hit rate: {region_stats['hit_rate']})")

# ===========================================================================
# 7. Cleanup
# ===========================================================================
print_section("7. Cleanup")

# Dispose worlds
del world_no_cache
del world_with_cache
del world_test

print("Cleanup done. All resources have been released.")

print_header("END OF DEMONSTRATION")
end = time.time()
time_no_cache_multi = (end - start) * 1000
print(f"      Time: {time_no_cache_multi:.2f}ms\n")

print("   With cache:")
world_with_cache2 = anvil.World(
    WORLD_PATH,
    chunk_cache_size=1024
)
start = time.time()
for x in range(5):
    for z in range(5):
        chunk = world_with_cache2.get_chunk(x, z)
end = time.time()
time_with_cache_multi = (end - start) * 1000
print(f"      Time: {time_with_cache_multi:.2f}ms")
print(f"      Speedup: {time_no_cache_multi / time_with_cache_multi:.1f}x\n")

print("=" * 50)
print("Cache provides significant performance improvement!")
print("=" * 50)
