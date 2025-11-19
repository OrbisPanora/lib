import shutil
import os
from anvil import Region, Block, Biome


class TestBiomeAndBlockOperations:

    def test_set_chunk_biome(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "r.0.0.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        chunk = region.get_chunk(0, 0)

        if chunk is None:
            print("Chunk (0, 0) does not exist, test skipped")
            return

        ice_spikes = Biome.from_name("minecraft:ice_spikes")
        chunk.set_chunk_biome(ice_spikes)

        region.save_chunk(chunk, str(test_file))
        region_reloaded = Region.from_file(str(test_file))
        chunk_reloaded = region_reloaded.get_chunk(0, 0)

        if chunk_reloaded:
            actual = chunk_reloaded.get_biome(8, 64, 8)
            assert actual.name() == "minecraft:ice_spikes"

    def test_set_single_biome_cell(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "r.0.0.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        chunk = region.get_chunk(0, 0)

        if chunk is None:
            print("Chunk (0, 0) does not exist, test skipped")
            return

        jungle = Biome.from_name("minecraft:jungle")
        chunk.set_biome(jungle, 8, 40, 8)

        region.save_chunk(chunk, str(test_file))
        region_reloaded = Region.from_file(str(test_file))
        chunk_reloaded = region_reloaded.get_chunk(0, 0)

        if chunk_reloaded:
            actual = chunk_reloaded.get_biome(8, 40, 8)
            assert actual.name() == "minecraft:jungle"
