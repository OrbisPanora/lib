import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import anvil
from anvil import Block

# Chemin vers ta save Minecraft
world_path = r'your_path'

print("=" * 60)
print("TEST: Modification du Nether")
print("=" * 60)

# Créer une instance World pour le Nether
nether = anvil.World(world_path, dimension='nether')

# Coordonnées du screenshot
x, y, z = -3, 42, 11

print(f"\nCoordonnées cibles: X={x}, Y={y}, Z={z}")
print(f"Dimension: {nether.get_dimension()}")
print(f"Region dir: {nether.region_dir}")

# 1. Lire le bloc actuel
print(f"\n1. Lecture du bloc actuel à ({x}, {y}, {z})...")
current_block = nether.get_block(x, y, z)
if current_block:
    print(f"   Bloc actuel: {current_block.name()}")
else:
    print("   Aucun bloc trouvé (chunk peut-être non généré)")

# 2. Placer un bloc de diamant
print(f"\n2. Placement d'un bloc de diamant à ({x}, {y}, {z})...")
nether.set_block(Block('minecraft', 'diamond_block'), x, y, z)
print("   ✓ Bloc placé")

# 3. Vérifier le placement
print(f"\n3. Vérification du placement...")
new_block = nether.get_block(x, y, z)
if new_block:
    print(f"   Nouveau bloc: {new_block.name()}")
    if new_block.name() == 'minecraft:diamond_block':
        print("   ✓ Succès!")
    else:
        print("   ⚠ Le bloc n'est pas celui attendu")
else:
    print("   ⚠ Impossible de lire le bloc")

# 4. Placer quelques blocs autour pour tester
print(f"\n4. Placement de blocs autour...")
blocks_to_place = [
    (x+1, y, z, 'gold_block'),
    (x-1, y, z, 'iron_block'),
    (x, y+1, z, 'emerald_block'),
    (x, y-1, z, 'netherrack'),
    (x, y, z+1, 'glowstone'),
    (x, y, z-1, 'soul_sand'),
]

for bx, by, bz, block_type in blocks_to_place:
    nether.set_block(Block('minecraft', block_type), bx, by, bz)
    print(f"   Placé {block_type} à ({bx}, {by}, {bz})")

# 5. Sauvegarder
print(f"\n5. Sauvegarde du monde...")
nether.save()
print("   ✓ Monde sauvegardé")

# 6. Afficher les infos
print(f"\n6. Informations sur la dimension:")
info = nether.get_dimension_info()
print(f"   Nom: {info['name']}")
print(f"   Chemin: {info['path']}")
print(f"   Régions chargées: {info['loaded_regions']}")

print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)
print("\nInstructions:")
print("1. Lance Minecraft")
print("2. Charge le monde 'New World test sde fdp'")
print("3. Va dans le Nether")
print("4. Téléporte-toi aux coordonnées: /tp @s -3 42 11")
print("5. Tu devrais voir un bloc de diamant et des blocs colorés autour!")
print("\nCommande de téléportation:")
print(f"  /tp @s {x} {y} {z}")
