from anvil import Region, Biome

region_file = r"C:\Users\seger\AppData\Roaming\.minecraft\saves\lib\region\r.0.0.mca"

# ============================================================
# Test 1: Single biome for entire chunk
# ============================================================

# Load region file
region = Region.from_file(region_file)
chunk = region.get_chunk(0, 0)

# Set entire chunk to ice spikes biome
print("Setting entire chunk (0, 0) to ice spikes biome...")
ice_spikes_biome = Biome.from_name("minecraft:ice_spikes")

for x in range(16):
    for y in range(-64, 320):
        for z in range(16):
            chunk.set_biome(ice_spikes_biome, x, y, z)

print("Chunk (0, 0) set to ice spikes!")

# Save changes
region.save_chunk(chunk, region_file)
print("Region saved!")

# ============================================================
# Test 2: 50/50 biome split in adjacent chunk
# ============================================================

print("\n" + "="*60)
print("TEST 2: Setting 50/50 biome split in chunk (1, 0)")
print("="*60)

chunk2 = region.get_chunk(1, 0)

# Set 50/50 split with 2 biomes
print("\nSetting chunk to 50/50 split: Desert (x=0-7) and Jungle (x=8-15)...")
desert_biome = Biome.from_name("minecraft:desert")
jungle_biome = Biome.from_name("minecraft:jungle")

# Set left half (x=0-7) to desert
for x in range(0, 8):
    for y in range(-64, 320):
        for z in range(16):
            chunk2.set_biome(desert_biome, x, y, z)

# Set right half (x=8-15) to jungle
for x in range(8, 16):
    for y in range(-64, 320):
        for z in range(16):
            chunk2.set_biome(jungle_biome, x, y, z)

print("Chunk split complete!")

# Verify by checking positions in both halves
test_positions2 = [
    (0, 64, 0),    # Desert side
    (7, 64, 15),   # Desert side
    (8, 64, 0),    # Jungle side
    (15, 64, 15),  # Jungle side
]

# TODO : Débug ça demain ;p
print("\nVerifying biome at various positions:")
for x, y, z in test_positions2:
    actual = chunk2.get_biome(x, y, z)
    expected = desert_biome if x < 8 else jungle_biome
    status = "✓" if actual.name() == expected.name() else "✗"
    print(f"  {status} Position ({x}, {y}, {z}): {actual}")

# Save changes
region.save_chunk(chunk2, region_file)
print("\nRegion saved!")
