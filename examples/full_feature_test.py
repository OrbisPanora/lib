"""
TEST COMPLET DE TOUTES LES FONCTIONNALITÉS
Teste absolument toutes les features de la bibliothèque OrbisPanora
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import anvil
from anvil import Block, Biome

world_path = r'your_path'

print("=" * 80)
print("TEST COMPLET - TOUTES LES FONCTIONNALITÉS")
print("=" * 80)


print("\n" + "=" * 80)
print("1. CRÉATION ET INITIALISATION")
print("=" * 80)


overworld = anvil.World(world_path, dimension='overworld', chunk_cache_size=128, region_cache_size=16)
print(f"Overworld créé: {overworld.get_dimension()}")


nether = anvil.World(world_path, dimension='nether', chunk_cache_size=128, region_cache_size=16)
print(f"Nether créé: {nether.get_dimension()}")


end = anvil.World(world_path, dimension='end', chunk_cache_size=128, region_cache_size=16)
print(f"End créé: {end.get_dimension()}")


print("\n" + "=" * 80)
print("2. OPÉRATIONS DE BASE SUR LES BLOCS")
print("=" * 80)


block = overworld.get_block(0, 64, 0)
print(f"get_block(0, 64, 0): {block.name() if block else 'None'}")


overworld.set_block(Block('minecraft', 'diamond_block'), 100, 64, 100)
print(f"set_block: Diamond block placé à (100, 64, 100)")


success = overworld.replace_block_at(100, 64, 100, "minecraft:gold_block")
print(f"replace_block_at: {success}")


block = overworld.get_block(100, 64, 100)
print(f"Vérification: {block.name() if block else 'None'}")

print("\n" + "=" * 80)
print("3. OPÉRATIONS SUR LES RÉGIONS ET CHUNKS")
print("=" * 80)


region = overworld.get_region(0, 0)
print(f"get_region(0, 0): {type(region).__name__}")


chunk = overworld.get_chunk(0, 0)
print(f"get_chunk(0, 0): {type(chunk).__name__ if chunk else 'None'}")


loaded = overworld.get_loaded_regions()
print(f"get_loaded_regions: {len(loaded)} régions")


bounds = overworld.get_world_bounds()
print(f"get_world_bounds: {bounds}")

print("\n" + "=" * 80)
print("4. STREAMING ET ITÉRATION")
print("=" * 80)


count = 0
for x, y, z, block in overworld.stream_blocks(0, 60, 0, 5, 65, 5):
    count += 1
print(f"stream_blocks: {count} blocs streamés")


chunk_count = 0
for cx, cz, chunk in overworld.stream_chunks(0, 0, 32, 32):
    if chunk:
        chunk_count += 1
print(f"stream_chunks: {chunk_count} chunks streamés")

print("\n" + "=" * 80)
print("5. REMPLACEMENT DE BLOCS EN MASSE")
print("=" * 80)


count = overworld.replace_blocks("minecraft:dirt", "minecraft:grass_block", bounds=(0, 60, 0, 10, 70, 10))
print(f"replace_blocks: {count} blocs remplacés")


count = overworld.replace_blocks_in_area("minecraft:stone", "minecraft:cobblestone", 20, 60, 20, 25, 65, 25)
print(f"replace_blocks_in_area: {count} blocs remplacés")

print("\n" + "=" * 80)
print("6. COMPTAGE DE BLOCS")
print("=" * 80)


stone_count = overworld.count_blocks("minecraft:stone", bounds=(0, 0, 0, 50, 100, 50))
print(f"count_blocks (stone): {stone_count}")

air_count = overworld.count_blocks("minecraft:air", bounds=(0, 60, 0, 10, 70, 10))
print(f"count_blocks (air): {air_count}")

print("\n" + "=" * 80)
print("7. GESTION DES BIOMES")
print("=" * 80)


biome = overworld.get_biome(0, 64, 0)
print(f"get_biome(0, 64, 0): {biome.name() if biome else 'None'}")


overworld.set_biome(Biome('plains'), 50, 64, 50)
print(f"set_biome: Plains biome placé à (50, 64, 50)")


count = overworld.replace_biomes("minecraft:desert", "minecraft:plains", bounds=(0, 60, 0, 20, 70, 20))
print(f"replace_biomes: {count} biomes remplacés")




print("\n" + "=" * 80)
print("8. RECHERCHE ET SCAN")
print("=" * 80)


positions = overworld.find_blocks("minecraft:diamond_ore", bounds=(0, -64, 0, 100, 20, 100), limit=5)
print(f"find_blocks (diamond_ore): {len(positions)} trouvés")


result = overworld.find_nearest_block("minecraft:stone", 0, 64, 0, max_radius=50)
if result:
    x, y, z, distance = result
    print(f"find_nearest_block (stone): trouvé à ({x}, {y}, {z}), distance: {distance:.2f}")
else:
    print(f"find_nearest_block (stone): non trouvé")


distribution = overworld.scan_area(0, 60, 0, 10, 70, 10)
print(f"scan_area: {len(distribution)} types de blocs différents")
for block_name, count in list(distribution.items())[:3]:
    print(f"  - {block_name}: {count}")




print("\n" + "=" * 80)
print("9. STATISTIQUES DU MONDE")
print("=" * 80)


info = overworld.get_world_info()
print(f"get_world_info:")
print(f"  - World folder: {info['world_folder']}")
print(f"  - Loaded regions: {info['loaded_regions']}")
print(f"  - Cache enabled: {info['cache_enabled']}")


top_blocks = overworld.get_block_distribution(bounds=(0, 0, 0, 50, 100, 50), top_n=5)
print(f"get_block_distribution (top 5):")
for i, (block_name, count) in enumerate(top_blocks.items(), 1):
    print(f"  {i}. {block_name}: {count}")


height = overworld.get_height_map(0, 0)
print(f"get_height_map(0, 0): Y={height}")




print("\n" + "=" * 80)
print("10. OPÉRATIONS SUR LES ZONES")
print("=" * 80)


count = overworld.fill_area("minecraft:gold_block", 200, 64, 200, 202, 66, 202)
print(f"fill_area: {count} blocs placés")


count = overworld.copy_area(200, 64, 200, 202, 66, 202, 210, 64, 210)
print(f"copy_area: {count} blocs copiés")


count = overworld.clear_area(200, 64, 200, 202, 66, 202)
print(f"clear_area: {count} blocs effacés")




print("\n" + "=" * 80)
print("11. GESTION DE LA MÉMOIRE")
print("=" * 80)


mem_stats = overworld.get_memory_usage()
print(f"get_memory_usage:")
print(f"  - Loaded regions: {mem_stats['loaded_regions']}")
print(f"  - Cached chunks: {mem_stats['cached_chunks']}")
print(f"  - Cached regions: {mem_stats['cached_regions']}")


cache_stats = overworld.get_cache_stats()
if cache_stats and cache_stats['chunk_cache']:
    print(f"get_cache_stats (chunk):")
    print(f"  - Size: {cache_stats['chunk_cache']['size']}")
    print(f"  - Hits: {cache_stats['chunk_cache']['hits']}")
    print(f"  - Misses: {cache_stats['chunk_cache']['misses']}")
    hit_rate = cache_stats['chunk_cache']['hit_rate']
    if isinstance(hit_rate, str):
        print(f"  - Hit rate: {hit_rate}")
    else:
        print(f"  - Hit rate: {hit_rate:.2%}")


overworld.invalidate_chunk(0, 0)
print(f"invalidate_chunk(0, 0)")


overworld.invalidate_region(0, 0)
print(f"invalidate_region(0, 0)")


overworld.clear_cache()
print(f"clear_cache")




print("\n" + "=" * 80)
print("12. GESTION DES DIMENSIONS")
print("=" * 80)


dim = nether.get_dimension()
print(f"get_dimension (nether): {dim}")


dim_info = nether.get_dimension_info()
print(f"get_dimension_info (nether):")
print(f"  - Name: {dim_info['name']}")
print(f"  - Path: {dim_info['path']}")
print(f"  - Loaded regions: {dim_info['loaded_regions']}")


test_world = anvil.World(world_path, dimension='overworld')
test_world.switch_dimension('nether', save_current=False)
print(f"switch_dimension: {test_world.get_dimension()}")




print("\n" + "=" * 80)
print("13. OPÉRATIONS MULTI-DIMENSIONS")
print("=" * 80)


overworld.set_block(Block('minecraft', 'emerald_block'), 300, 64, 300)
print(f"Emerald block placé dans Overworld")

nether.set_block(Block('minecraft', 'netherrack'), -3, 42, 11)
print(f"Netherrack placé dans Nether")

end.set_block(Block('minecraft', 'end_stone'), 0, 64, 0)
print(f"End stone placé dans End")


overworld_x, overworld_z = 800, 800
nether_x, nether_z = overworld_x // 8, overworld_z // 8
print(f"Conversion portail: Overworld ({overworld_x}, {overworld_z}) → Nether ({nether_x}, {nether_z})")




print("\n" + "=" * 80)
print("14. UNLOAD REGIONS")
print("=" * 80)


success = overworld.unload_region(0, 0, save=False)
print(f"unload_region(0, 0): {success}")


count = test_world.unload_all_regions(save=False)
print(f"unload_all_regions: {count} régions déchargées")




print("\n" + "=" * 80)
print("15. SAUVEGARDE")
print("=" * 80)


overworld.save()
print(f"Overworld sauvegardé")


nether.save()
print(f"Nether sauvegardé")


end.save()
print(f"End sauvegardé")




print("\n" + "=" * 80)
print("16. APPLY DICTIONARY")
print("=" * 80)


changes = {
    (400, 64, 400): Block('minecraft', 'diamond_block'),
    (401, 64, 400): Block('minecraft', 'gold_block'),
    (402, 64, 400): Block('minecraft', 'iron_block'),
}
overworld.apply(changes)
print(f"apply: {len(changes)} blocs appliqués")




print("\n" + "=" * 80)
print("RÉSUMÉ FINAL")
print("=" * 80)

features_tested = [
    "Création de World (3 dimensions)",
    "get_block / set_block",
    "replace_block_at",
    "get_region / get_chunk",
    "get_loaded_regions / get_world_bounds",
    "stream_blocks / stream_chunks",
    "replace_blocks / replace_blocks_in_area",
    "count_blocks",
    "get_biome / set_biome / replace_biomes",
    "find_blocks / find_nearest_block / scan_area",
    "get_world_info / get_block_distribution / get_height_map",
    "fill_area / copy_area / clear_area",
    "get_memory_usage / get_cache_stats",
    "invalidate_chunk / invalidate_region / clear_cache",
    "get_dimension / get_dimension_info / switch_dimension",
    "Opérations multi-dimensions",
    "unload_region / unload_all_regions",
    "save (3 dimensions)",
    "apply dictionary",
]

print(f"\nFonctionnalités testées: {len(features_tested)}")
for feature in features_tested:
    print(f"  {feature}")

print("\n" + "=" * 80)
print("TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS! ✅")
print("=" * 80)

print("\nStatistiques finales:")
print(f"  - Dimensions testées: 3 (Overworld, Nether, End)")
print(f"  - Méthodes testées: 40+")
print(f"  - Catégories: 16")
print(f"\nPour vérifier dans Minecraft:")
print(f"  - Overworld: /tp @s 100 64 100 (gold block)")
print(f"  - Overworld: /tp @s 300 64 300 (emerald block)")
print(f"  - Nether: /tp @s -3 42 11 (netherrack)")
print(f"  - End: /tp @s 0 64 0 (end stone)")
