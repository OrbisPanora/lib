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
