import _path
import anvil
import time

print("=== Region Cache Test (Standalone) ===\n")

# Load a region directly with cache enabled
print("1. Loading region with cache enabled (64 chunks)")
region_with_cache = anvil.Region.from_file(
    r'C:\Users\zayd2\AppData\Roaming\.minecraft\saves\New World test sde fdp\region\r.0.0.mca'
)
print(f"   Cache enabled: {region_with_cache._chunk_cache is not None}\n")

# Performance test with cache
print("2. Performance test - 1000 reads of the same chunk")
start = time.time()
for i in range(1000):
    chunk = region_with_cache.get_chunk(10, 10)
end = time.time()
print(f"   Total time: {(end - start) * 1000:.2f}ms")
print(f"   Average: {(end - start) * 1000 / 1000:.4f}ms per read\n")

# Cache statistics
print("3. Cache statistics")
stats = region_with_cache.get_cache_stats()
if stats:
    print(f"   Size: {stats['size']}/{stats['max_size']}")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit rate: {stats['hit_rate']}\n")

# Test without cache
print("4. Loading region WITHOUT cache")
region_no_cache = anvil.Region.from_file(
    r'C:\Users\zayd2\AppData\Roaming\.minecraft\saves\New World test sde fdp\region\r.0.0.mca',
    cache_size=None  # Disable cache
)
print(f"   Cache enabled: {region_no_cache._chunk_cache is not None}\n")

print("5. Performance test - 100 reads WITHOUT cache")
start = time.time()
for i in range(100):
    chunk = region_no_cache.get_chunk(10, 10)
end = time.time()
print(f"   Total time: {(end - start) * 1000:.2f}ms")
print(f"   Average: {(end - start) * 1000 / 100:.4f}ms per read\n")

# Comparison
print("6. Comparison")
region_with_cache.clear_cache()

start_cached = time.time()
for i in range(100):
    chunk = region_with_cache.get_chunk(10, 10)
end_cached = time.time()

start_no_cache = time.time()
for i in range(100):
    chunk = region_no_cache.get_chunk(10, 10)
end_no_cache = time.time()

time_cached = (end_cached - start_cached) * 1000
time_no_cache = (end_no_cache - start_no_cache) * 1000

print(f"   With cache: {time_cached:.2f}ms")
print(f"   Without cache: {time_no_cache:.2f}ms")
print(f"   Speedup: {(time_no_cache / time_cached):.1f}x faster\n")

print("=== End of tests ===")
