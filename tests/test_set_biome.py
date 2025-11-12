import context as _
from anvil import Region, Biome
import shutil
import os


def test_set_chunk_biome(tmp_path):
    # copie du fichier de test
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_set_chunk_biome.mca"
    shutil.copy(original_file, test_file)

    # chargement et obtention du chunk
    region = Region.from_file(str(test_file))
    chunk = region.get_chunk(0, 0)

    if chunk is None:
        print("Chunk (0, 0) n'existe pas, test ignoré")
        return

    # définir tout le chunk au biome ice_spikes
    ice_spikes = Biome.from_name("minecraft:ice_spikes")
    chunk.set_chunk_biome(ice_spikes)

    # sauvegarder et recharger pour vérifier
    region.save_chunk(chunk, str(test_file))
    region_reloaded = Region.from_file(str(test_file))
    chunk_reloaded = region_reloaded.get_chunk(0, 0)

    if chunk_reloaded:
        actual = chunk_reloaded.get_biome(8, 64, 8)
        assert actual.name() == "minecraft:ice_spikes", "Le biome du chunk doit être ice_spikes"


def test_set_single_biome_cell(tmp_path):
    # copie du fichier de test
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_set_single_biome_cell.mca"
    shutil.copy(original_file, test_file)

    # chargement et obtention du chunk
    region = Region.from_file(str(test_file))
    chunk = region.get_chunk(0, 0)

    if chunk is None:
        print("Chunk (0, 0) n'existe pas, test ignoré")
        return

    # définir la cellule de biome contenant la position (8, 40, 8) en jungle
    jungle = Biome.from_name("minecraft:jungle")
    chunk.set_biome(jungle, 8, 40, 8)

    # sauvegarder et recharger pour vérifier
    region.save_chunk(chunk, str(test_file))
    region_reloaded = Region.from_file(str(test_file))
    chunk_reloaded = region_reloaded.get_chunk(0, 0)

    if chunk_reloaded:
        actual = chunk_reloaded.get_biome(8, 40, 8)
        assert actual.name() == "minecraft:jungle", "La cellule de biome doit être jungle"
