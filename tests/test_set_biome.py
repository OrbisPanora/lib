from anvil import Region, Biome

region_file = r"C:\Users\seger\AppData\Roaming\.minecraft\saves\lib\region\r.0.0.mca"

# Load region file
region = Region.from_file(region_file)
chunk = region.get_chunk(0, 0)

# Get original biome
original_biome = chunk.get_biome(8, 64, 8)
print(f"Original biome at (8, 64, 8): {original_biome}")

# Set entire chunk to ice spikes biome
print("\nSetting entire chunk to ice spikes biome...")
ice_spikes_biome = Biome.from_name("minecraft:ice_spikes")

# Set ice spikes biome for all positions in the chunk
for x in range(16):
    for y in range(-64, 320):
        for z in range(16):
            chunk.set_biome(ice_spikes_biome, x, y, z)

print("Entire chunk set to ice spikes!")

# Verify by checking several positions
test_positions = [
    (0, 64, 0),
    (7, 64, 7),
    (15, 64, 15),
    (8, 0, 8),
    (8, 100, 8),
]

print("\nVerifying biome at various positions:")
for x, y, z in test_positions:
    actual = chunk.get_biome(x, y, z)
    print(f"  Position ({x}, {y}, {z}): {actual}")

# Save changes
region.save_chunk(chunk, region_file)
print("\nRegion saved!")