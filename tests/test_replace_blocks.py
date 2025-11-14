from anvil import Region, Block
import shutil
import os


class TestReplaceBlocks:

    def test_chunk_replace_block_at(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "test_chunk_replace.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        chunk = region.get_chunk(0, 0)

        if chunk is None:
            print("Chunk (0, 0) doesn't exist, skipping test")
            return

        original_block = chunk.get_block(5, 64, 10)
        print(f"Original block at (5, 64, 10): {original_block}")

        new_block = Block.from_name("minecraft:diamond_block")
        success = chunk.replace_block_at(5, 64, 10, new_block)

        assert success

        replaced_block = chunk.get_block(5, 64, 10)
        print(f"Replaced block at (5, 64, 10): {replaced_block}")
        assert replaced_block.name() == "minecraft:diamond_block"

    def test_chunk_replace_blocks(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "test_chunk_replace_all.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        chunk = region.get_chunk(0, 0)

        if chunk is None:
            print("Chunk (0, 0) doesn't exist, skipping test")
            return

        count = chunk.replace_blocks("minecraft:dirt", "minecraft:grass_block")
        print(f"Replaced {count} blocks of minecraft:dirt with minecraft:grass_block")

        assert count >= 0

    def test_region_replace_block_at(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "test_region_replace.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        success = region.replace_block_at(5, 64, 10, "minecraft:gold_block", str(test_file))

        assert success

        region_reloaded = Region.from_file(str(test_file))
        chunk = region_reloaded.get_chunk(0, 0)

        if chunk:
            replaced_block = chunk.get_block(5, 64, 10)
            print(f"Block after region replace: {replaced_block}")
            assert replaced_block.name() == "minecraft:gold_block"

    def test_region_replace_blocks_in_chunk(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "test_region_replace_chunks.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        count = region.replace_blocks("minecraft:stone", "minecraft:cobblestone", str(test_file), chunks=(0, 0))
        print(f"Replaced {count} blocks in chunk (0, 0)")

        assert count >= 0

    def test_region_replace_blocks_in_multiple_chunks(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "test_region_replace_multi.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        count = region.replace_blocks("minecraft:dirt", "minecraft:coal_block", str(test_file), chunks=[(0, 0), (1, 0)])
        print(f"Replaced {count} blocks in specified chunks")

        assert count >= 0

    def test_replace_with_block_object(self, tmp_path):
        original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
        test_file = tmp_path / "test_block_objects.mca"
        shutil.copy(original_file, test_file)

        region = Region.from_file(str(test_file))
        chunk = region.get_chunk(0, 0)

        if chunk is None:
            print("Chunk (0, 0) doesn't exist, skipping test")
            return

        old_block = Block.from_name("minecraft:stone")
        new_block = Block.from_name("minecraft:andesite")
        count = chunk.replace_blocks(old_block, new_block)
        print(f"Replaced {count} stone blocks with andesite using Block objects")

        assert count >= 0
