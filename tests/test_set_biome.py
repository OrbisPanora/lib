from anvil import Region, Biome

region_file = r"C:\Users\seger\AppData\Roaming\.minecraft\saves\lib\region\r.0.0.mca"

# Load region file
region = Region.from_file(region_file)
chunk = region.get_chunk(0, 0)

# Set entire chunk to ice spikes biome
print("Setting entire chunk (0, 0) to ice spikes biome...")
ice_spikes_biome = Biome.from_name("minecraft:ice_spikes")
chunk.set_chunk_biome(ice_spikes_biome)

print("Chunk (0, 0) set to ice spikes!")

# Save changes
region.save_chunk(chunk, region_file)
print("Region saved!")

print("\n" + "="*60)
print("Setting single block biome in chunk (0, 0)")
print("="*60)

# Set a single block position to jungle biome in the previous chunk

# This actually sets the entire 4x4x4 biome cell containing this position
print("\nSetting biome at position (8, 40, 8) to jungle...")
jungle_biome = Biome.from_name("minecraft:jungle")
chunk.set_biome(jungle_biome, 8, 40, 8)

# Verify the biome was set
actual_biome = chunk.get_biome(8, 40, 8)
print(f"Biome at (8, 40, 8): {actual_biome}")
print(f"Match: {'Passed' if actual_biome.name() == jungle_biome.name() else 'Failed'}")

# Save changes
region.save_chunk(chunk, region_file)
print("\nRegion saved!")
# ...existing code...
