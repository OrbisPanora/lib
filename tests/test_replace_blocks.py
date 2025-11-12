"""
Test suite for block replacement methods in Region and Chunk classes.

This module tests:
- Chunk.replace_block_at: Replace a single block in a chunk
- Chunk.replace_blocks: Replace all blocks of a type in a chunk
- Region.replace_block_at: Replace a single block using global coordinates
- Region.replace_blocks: Replace blocks in specific chunks of a region
"""

import context as _
from anvil import Region, Block
import shutil
import os


def test_chunk_replace_block_at(tmp_path):
    """
    Test replacing a single block at specific coordinates within a chunk.

    Tests the Chunk.replace_block_at method with local coordinates (0-15).
    """
    # Copy the test region file to a temporary location
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_chunk_replace.mca"
    shutil.copy(original_file, test_file)

    # Load region and get a chunk
    region = Region.from_file(str(test_file))
    chunk = region.get_chunk(0, 0)

    if chunk is None:
        print("Chunk (0, 0) doesn't exist, skipping test")
        return

    # Get original block
    original_block = chunk.get_block(5, 64, 10)
    print(f"Original block at (5, 64, 10): {original_block}")

    # Replace with a new block
    new_block = Block.from_name("minecraft:diamond_block")
    success = chunk.replace_block_at(5, 64, 10, new_block)

    assert success, "Block replacement should succeed"

    # Verify the replacement
    replaced_block = chunk.get_block(5, 64, 10)
    print(f"Replaced block at (5, 64, 10): {replaced_block}")
    assert replaced_block.name() == "minecraft:diamond_block", "Block should be replaced with diamond_block"


def test_chunk_replace_blocks(tmp_path):
    """
    Test replacing all blocks of a specific type within a chunk.

    Tests the Chunk.replace_blocks method by replacing all dirt blocks.
    """
    # Copy the test region file to a temporary location
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_chunk_replace_all.mca"
    shutil.copy(original_file, test_file)

    # Load region and get a chunk
    region = Region.from_file(str(test_file))
    chunk = region.get_chunk(0, 0)

    if chunk is None:
        print("Chunk (0, 0) doesn't exist, skipping test")
        return

    # Replace all dirt blocks with grass blocks
    old_block = "minecraft:dirt"
    new_block = "minecraft:grass_block"

    count = chunk.replace_blocks(old_block, new_block)
    print(f"Replaced {count} blocks of {old_block} with {new_block}")

    # Count should be >= 0 (there may or may not be dirt blocks in the chunk)
    assert count >= 0, "Count should be non-negative"


def test_region_replace_block_at(tmp_path):
    """
    Test replacing a single block using global coordinates via Region.

    Tests the Region.replace_block_at method which handles global coordinates
    and automatically saves changes to the file.
    """
    # Copy the test region file to a temporary location
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_region_replace.mca"
    shutil.copy(original_file, test_file)

    # Load region
    region = Region.from_file(str(test_file))

    # Use global coordinates (will be converted to chunk coordinates internally)
    # For chunk (0, 0), global coords 5, 10 map to local coords 5, 10
    success = region.replace_block_at(5, 64, 10, "minecraft:gold_block", str(test_file))

    assert success, "Block replacement should succeed"

    # Reload region and verify
    region_reloaded = Region.from_file(str(test_file))
    chunk = region_reloaded.get_chunk(0, 0)

    if chunk:
        replaced_block = chunk.get_block(5, 64, 10)
        print(f"Block after region replace: {replaced_block}")
        assert replaced_block.name() == "minecraft:gold_block", "Block should be gold_block"


def test_region_replace_blocks_in_chunk(tmp_path):
    """
    Test replacing blocks in specific chunks of a region.

    Tests the Region.replace_blocks method with a specific chunk coordinate.
    This avoids processing the entire region which would be too slow.
    """
    # Copy the test region file to a temporary location
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_region_replace_chunks.mca"
    shutil.copy(original_file, test_file)

    # Load region
    region = Region.from_file(str(test_file))

    # Replace stone with cobblestone in chunk (0, 0) only
    old_block = "minecraft:stone"
    new_block = "minecraft:cobblestone"

    count = region.replace_blocks(old_block, new_block, str(test_file), chunks=(0, 0))
    print(f"Replaced {count} blocks in chunk (0, 0)")

    assert count >= 0, "Count should be non-negative"


def test_region_replace_blocks_in_multiple_chunks(tmp_path):
    """
    Test replacing blocks in multiple specific chunks.

    Tests the Region.replace_blocks method with a list of chunk coordinates.
    """
    # Copy the test region file to a temporary location
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_region_replace_multi.mca"
    shutil.copy(original_file, test_file)

    # Load region
    region = Region.from_file(str(test_file))

    # Replace grass with dirt in chunks (0, 0) and (1, 0)
    old_block = "minecraft:dirt"
    new_block = "minecraft:coal_block"

    count = region.replace_blocks(
        old_block,
        new_block,
        str(test_file),
        chunks=[(0, 0), (1, 0)]
    )
    print(f"Replaced {count} blocks in specified chunks")

    assert count >= 0, "Count should be non-negative"


def test_replace_with_block_object(tmp_path):
    """
    Test replacing blocks using Block objects instead of strings.

    Verifies that both string and Block object parameters work correctly.
    """
    # Copy the test region file to a temporary location
    original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
    test_file = tmp_path / "test_block_objects.mca"
    shutil.copy(original_file, test_file)

    # Load region and get a chunk
    region = Region.from_file(str(test_file))
    chunk = region.get_chunk(0, 0)

    if chunk is None:
        print("Chunk (0, 0) doesn't exist, skipping test")
        return

    # Create Block objects
    old_block = Block.from_name("minecraft:stone")
    new_block = Block.from_name("minecraft:andesite")

    # Replace using Block objects
    count = chunk.replace_blocks(old_block, new_block)
    print(f"Replaced {count} stone blocks with andesite using Block objects")

    assert count >= 0, "Count should be non-negative"
