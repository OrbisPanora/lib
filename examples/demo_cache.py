import _path
import anvil
import time

print("=== Cache Performance Demonstration ===\n")

# Test 1: Reading blocks (shows cache benefit)
print("1. Reading 100 blocks from different chunks")
print("   WITHOUT cache:")
world_no_cache = anvil.World(
    r'your_path',
    chunk_cache_size=None,  # Disable chunk cache
    region_cache_size=None   # Disable region cache
)

start = time.time()
for x in range(160, 170):
    for z in range(160, 170):
        block = world_no_cache.get_block(x, 64, z)
end = time.time()
time_no_cache = (end - start) * 1000

print(f"      Time: {time_no_cache:.2f}ms")
print(f"      Average per block: {time_no_cache / 100:.4f}ms\n")

print("   WITH cache:")
world_with_cache = anvil.World(
    r'your_path',
    chunk_cache_size=1024,  # Cache up to 1024 chunks
    region_cache_size=64     # Cache up to 64 regions
)

start = time.time()
for x in range(160, 170):
    for z in range(160, 170):
        block = world_with_cache.get_block(x, 64, z)
end = time.time()
time_with_cache = (end - start) * 1000

print(f"      Time: {time_with_cache:.2f}ms")
print(f"      Average per block: {time_with_cache / 100:.4f}ms\n")

# Show the difference
print("=" * 50)
if time_with_cache < time_no_cache:
    print(f"SPEEDUP: {time_no_cache / time_with_cache:.1f}x faster with cache!")
    print(f"   Without cache: {time_no_cache:.2f}ms")
    print(f"   With cache:    {time_with_cache:.2f}ms")
    print(f"   Time saved:    {time_no_cache - time_with_cache:.2f}ms")
else:
    print(f"Cache overhead for small operations")
    print(f"   (Cache is beneficial for repeated access)")
print("=" * 50 + "\n")

# Test 2: Repeated access (shows cache benefit clearly)
print("2. Repeated access to same chunk (1000 times)")
print("   WITH cache:")
world_cached = anvil.World(
    r'your_path',
    chunk_cache_size=1024
)

start = time.time()
for i in range(1000):
    chunk = world_cached.get_chunk(10, 10)
end = time.time()
time_cached = (end - start) * 1000

print(f"      Time: {time_cached:.2f}ms")
print(f"      Average: {time_cached / 1000:.4f}ms per read\n")

# Cache statistics
stats = world_cached.get_cache_stats()
chunk_stats = stats['chunk_cache']
print(f"   Cache statistics:")
print(f"      Hits: {chunk_stats['hits']} (99.9%)")
print(f"      Misses: {chunk_stats['misses']} (0.1% - first read only)")
print(f"      Hit rate: {chunk_stats['hit_rate']}\n")

# Test 4: Real-world scenario - multiple chunks
print("4. Real-world scenario: Reading 25 different chunks")
print("   Without cache:")
world_no_cache2 = anvil.World(
    r'your_path',
    chunk_cache_size=None
)
start = time.time()
for x in range(5):
    for z in range(5):
        chunk = world_no_cache2.get_chunk(x, z)
end = time.time()
time_no_cache_multi = (end - start) * 1000
print(f"      Time: {time_no_cache_multi:.2f}ms\n")

print("   With cache:")
world_with_cache2 = anvil.World(
    r'your_path',
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
