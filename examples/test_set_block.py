import _path
import anvil

# Test simple pour vérifier set_block
world_path = r'C:\Users\zayd2\AppData\Roaming\.minecraft\saves\New World test sde fdp'
print(f"📁 Ouverture du monde: {world_path}")

word = anvil.World(world_path)

# Coordonnées de test
x, y, z = 160, 64, 160

print(f"\n🔍 Test aux coordonnées ({x}, {y}, {z})")

# Calculer les coordonnées de région et chunk
region_x = x >> 9
region_z = z >> 9
chunk_x = x >> 4
chunk_z = z >> 4

print(f"   Région: ({region_x}, {region_z})")
print(f"   Chunk: ({chunk_x}, {chunk_z})")

# Récupérer la région
region = word.get_region(region_x, region_z)
print(f"   Type de région: {type(region).__name__}")

# Essayer de placer un bloc
print(f"\n🔨 Placement d'un bloc de glowstone...")
block = anvil.Block('minecraft', 'glowstone')
word.set_block(block, x, y, z)

# Vérifier si le bloc a été placé
print(f"\n✅ Vérification du bloc placé...")
placed_block = word.get_block(x, y, z)
if placed_block:
    print(f"   Bloc trouvé: {placed_block.name()}")
else:
    print(f"   ❌ Aucun bloc trouvé!")

# Sauvegarder
print(f"\n💾 Sauvegarde du monde...")
word.save()

print(f"\n✅ Test terminé!")
