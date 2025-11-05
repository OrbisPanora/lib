from anvil import Region, Block

# Charger une région
region = Region.from_file('r.0.0.mca')

# Obtenir un chunk
chunk = region.get_chunk(0, 0)

# Test 1: Remplacer un seul bloc
print("Test 1: Remplacer un bloc à (5, 64, 10)")
success = chunk.replace_block_at(5, 64, 10, "minecraft:diamond_block")
print(f"Succès: {success}")
block = chunk.get_block(5, 64, 10)
print(f"Bloc après remplacement: {block}")

# Test 2: Remplacer toute la terre par des blocs de diamant
print("\nTest 2: Remplacer toute la terre par des blocs de diamant")
count = chunk.replace_blocks("minecraft:dirt", "minecraft:diamond_block")
print(f"Nombre de blocs remplacés: {count}")

# Sauvegarder les modifications
print("\nSauvegarde du chunk...")
region.save_chunk(chunk, 'r.0.0_modified.mca')
print("\nChunk sauvegardé dans r.0.0_modified.mca!")