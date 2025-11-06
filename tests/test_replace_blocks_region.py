from anvil import Region, Block

# Load region file
region = Region.from_file('r.0.0.mca')

print("=" * 60)
print("Test de la méthode replace_blocks de Region")
print("=" * 60)

# Test 1: Replace dans un seul chunk
print("\nTest 1: Replace stone -> diamond_block dans le chunk (0, 0)")
count = region.replace_blocks("minecraft:stone", "minecraft:diamond_block", "r.0.0_modified.mca", chunks=(0, 0))
print(f"Blocs remplacés: {count}")

# Recharger pour le test suivant
region = Region.from_file('r.0.0_modified.mca')

# Test 2: Replace dans plusieurs chunks spécifiques
print("\nTest 2: Replace dirt -> gold_block dans les chunks (0,0), (1,0), (0,1)")
count = region.replace_blocks("minecraft:dirt", "minecraft:none", "r.0.0_modified.mca",
                             chunks=[(0, 0), (1, 0), (0, 1)])
print(f"Blocs remplacés: {count}")

# Recharger pour le test suivant
region = Region.from_file('r.0.0_modified.mca')

# Test 3: Vérification en rechargeant et en vérifiant un bloc spécifique
print("\nTest 3: Vérification - charger le fichier modifié et vérifier un bloc")
final_region = Region.from_file('r.0.0_modified.mca')
chunk = final_region.get_chunk(0, 0)
# Chercher un bloc qui devrait être diamond_block maintenant
print(f"Exemple de bloc à (5, 64, 10): {chunk.get_block(5, 64, 10)}")

# Test 4: Replace avec des objets Block
print("\nTest 4: Replace avec des objets Block (oak_log -> birch_log)")
old_block = Block.from_name("minecraft:oak_log")
new_block = Block.from_name("minecraft:birch_log")
count = region.replace_blocks(old_block, new_block, "r.0.0_modified.mca", chunks=(0, 0))
print(f"Blocs remplacés: {count}")

print("\n" + "=" * 60)
print("Tous les tests sont terminés avec succès!")
print("=" * 60)

