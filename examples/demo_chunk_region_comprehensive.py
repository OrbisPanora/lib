#!/usr/bin/env python3
"""
Comprehensive demo for testing all Chunk and Region functionality.

This script demonstrates and tests every method available in the Chunk and Region classes,
providing a complete overview of the anvil library's capabilities for reading and modifying
Minecraft world data.

Usage:
    python demo_chunk_region_comprehensive.py [path_to_world_folder]

If no path is provided, the script will create a temporary empty world for demonstration.
"""

import os
import sys
import tempfile
import shutil
from typing import Optional

# Add the lib directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anvil import Region, Chunk, Block, Biome, EmptyRegion, EmptyChunk
from anvil.errors import OutOfBoundsCoordinates, ChunkNotFound


def create_test_world() -> str:
    """Create a temporary empty world for testing."""
    temp_dir = tempfile.mkdtemp(prefix="minecraft_test_")
    print(f"Created temporary world at: {temp_dir}")
    return temp_dir


def demo_region_functionality(world_path: str):
    """Demonstrate all Region class methods."""
    print("\n" + "="*60)
    print("REGION FUNCTIONALITY DEMO")
    print("="*60)

    # Get region file path
    region_x, region_z = 0, 0
    region_file = os.path.join(world_path, "region", f"r.{region_x}.{region_z}.mca")
    print(f"\n1. Loading region at ({region_x}, {region_z}) from {region_file}")

    # Try to load existing region or create empty region
    if os.path.exists(region_file):
        try:
            region = Region.from_file(region_file)
            print(f"   Region type: {type(region).__name__}")
        except Exception as e:
            print(f"   Error loading region: {e}")
            region = EmptyRegion(region_x, region_z)
            print(f"   Created EmptyRegion instead: {type(region).__name__}")
    else:
        region = EmptyRegion(region_x, region_z)
        print(f"   Region file doesn't exist, created EmptyRegion: {type(region).__name__}")

    if isinstance(region, Region):
        print("\n2. Testing Region-specific methods:")

        # chunk_location
        print("   - chunk_location(0, 0):", region.chunk_location(0, 0))

        # get_chunk
        print("   - Getting chunk (0, 0)...")
        chunk = region.get_chunk(0, 0)
        if chunk:
            print(f"      Chunk type: {type(chunk).__name__}")
            print(f"      Chunk coordinates: ({chunk.x}, {chunk.z})")

        # Cache stats
        print("   - Cache stats:", region.get_cache_stats())

        # set_block and save_chunk
        print("   - Setting block and saving chunk...")
        test_block = Block.from_name("minecraft:stone")
        try:
            region.set_block(test_block, 100, 64, 100, region_file)
            print("      Block set successfully")
        except Exception as e:
            print(f"      Error setting block: {e}")

        # replace_block_at
        print("   - Replacing block at specific coordinates...")
        replaced = region.replace_block_at(100, 64, 100, "minecraft:dirt", region_file)
        print(f"      Block replaced: {replaced}")

        # replace_blocks
        print("   - Replacing blocks in region...")
        count = region.replace_blocks("minecraft:dirt", "minecraft:grass_block", region_file)
        print(f"      Blocks replaced: {count}")

        # to_dict
        print("   - Converting region to dict...")
        region_dict = region.to_dict(include_chunks=True)
        print(f"      Region dict keys: {list(region_dict.keys())}")

        # save
        print("   - Saving region...")
        region.save(region_file)
        print("      Region saved")

    elif isinstance(region, EmptyRegion):
        print("\n2. Testing EmptyRegion-specific methods:")

        # EmptyRegion methods
        chunk = region.get_chunk(0, 0)
        print(f"   - get_chunk(0, 0): {type(chunk).__name__ if chunk else None}")

        try:
            region.set_block(Block.from_name("minecraft:stone"), 100, 64, 100)
            print("   - set_block: Block set in EmptyRegion")
        except Exception as e:
            print(f"   - set_block error: {e}")

    # Cache operations (only for Region objects)
    print("\n3. Cache operations:")
    if isinstance(region, Region):
        region.clear_cache()
        print("   - Cache cleared")
        region.invalidate_chunk(0, 0)
        print("   - Chunk (0, 0) invalidated")
    else:
        print("   - EmptyRegion has no cache operations")


def demo_chunk_functionality(world_path: str):
    """Demonstrate all Chunk class methods."""
    print("\n" + "="*60)
    print("CHUNK FUNCTIONALITY DEMO")
    print("="*60)

    # Get region first
    region_x, region_z = 0, 0
    region_file = os.path.join(world_path, "region", f"r.{region_x}.{region_z}.mca")
    if os.path.exists(region_file):
        try:
            region = Region.from_file(region_file)
        except Exception:
            region = EmptyRegion(region_x, region_z)
    else:
        region = EmptyRegion(region_x, region_z)

    # Get a chunk
    chunk_x, chunk_z = 0, 0
    print(f"\n1. Getting chunk at ({chunk_x}, {chunk_z}) from region")
    chunk = region.get_chunk(chunk_x, chunk_z)

    if chunk is None:
        print("   No chunk found, creating EmptyChunk for demonstration")
        chunk = EmptyChunk(chunk_x, chunk_z)

    print(f"   Chunk type: {type(chunk).__name__}")

    if isinstance(chunk, Chunk):
        print("\n2. Testing Chunk-specific methods:")

        # Basic properties
        print(f"   - Coordinates: ({chunk.x}, {chunk.z})")
        print(f"   - Version: {chunk.version}")

        # get_section
        print("   - Getting sections...")
        for y in range(-4, 20):  # Full height range
            section = chunk.get_section(y)
            if section:
                print(f"      Section {y}: Found")
                break
        else:
            print("      No sections found")

        # get_palette
        section = chunk.get_section(4)  # Try section 4 (around sea level)
        if section:
            palette = chunk.get_palette(section)
            print(f"   - Palette length: {len(palette) if palette else 0}")
            if palette and len(palette) > 0:
                print(f"   - First palette block: {palette[0].name()}")

        # get_block
        print("   - Getting blocks...")
        for y in [60, 64, 70]:  # Test different heights
            try:
                block = chunk.get_block(8, y, 8)  # Center of chunk
                print(f"      Block at (8, {y}, 8): {block.name() if block else 'None'}")
            except Exception as e:
                print(f"      Error getting block at y={y}: {e}")

        # get_biome
        print("   - Getting biomes...")
        try:
            biome = chunk.get_biome(8, 64, 8)
            print(f"      Biome at (8, 64, 8): {biome.name() if biome else 'None'}")
        except Exception as e:
            print(f"      Error getting biome: {e}")

        # stream_blocks
        print("   - Streaming blocks from section...")
        if section:
            block_count = 0
            for block in chunk.stream_blocks(section=section):
                block_count += 1
                if block_count >= 10:  # Just sample first 10
                    break
            print(f"      Sampled {block_count} blocks from section")

        # stream_chunk
        print("   - Streaming entire chunk...")
        total_blocks = 0
        unique_blocks = set()
        for block in chunk.stream_chunk():
            total_blocks += 1
            unique_blocks.add(block.name() if hasattr(block, 'name') else str(block))
            if total_blocks >= 1000:  # Sample limit
                break
        print(f"      Sampled {total_blocks} blocks, {len(unique_blocks)} unique types")

        # to_dict
        print("   - Converting chunk to dict...")
        chunk_dict = chunk.to_dict(simplify=True, include_blocks=False)
        print(f"      Chunk dict keys: {list(chunk_dict.keys())}")

        chunk_dict_full = chunk.to_dict(simplify=False, include_blocks=True)
        print(f"      Full chunk dict keys: {list(chunk_dict_full.keys())}")

    elif isinstance(chunk, EmptyChunk):
        print("\n2. Testing EmptyChunk-specific methods:")

        print(f"   - Coordinates: ({chunk.x}, {chunk.z})")

        # EmptyChunk methods
        try:
            block = chunk.get_block(8, 64, 8)
            print(f"   - get_block(8, 64, 8): {block.name() if block else 'None'}")
        except Exception as e:
            print(f"   - get_block error: {e}")

        try:
            biome = chunk.get_biome(8, 64)
            print(f"   - get_biome(8, 64): {biome.name() if biome else 'None'}")
        except Exception as e:
            print(f"   - get_biome error: {e}")

        # set_block
        print("   - Setting blocks in EmptyChunk...")
        chunk.set_block(Block.from_name("minecraft:stone"), 8, 64, 8)
        chunk.set_block(Block.from_name("minecraft:dirt"), 8, 65, 8)
        print("      Blocks set")

        # set_biome
        print("   - Setting biome in EmptyChunk...")
        chunk.set_biome(Biome.from_name("minecraft:plains"), 8, 8)
        print("      Biome set")

        # replace_blocks
        count = chunk.replace_blocks("minecraft:stone", "minecraft:cobblestone")
        print(f"   - replace_blocks: {count} blocks replaced")


def demo_world_integration(world_path: str):
    """Demonstrate direct Region and Chunk operations."""
    print("\n" + "="*60)
    print("DIRECT REGION & CHUNK OPERATIONS DEMO")
    print("="*60)

    # Get region
    region_x, region_z = 0, 0
    region_file = os.path.join(world_path, "region", f"r.{region_x}.{region_z}.mca")
    if os.path.exists(region_file):
        try:
            region = Region.from_file(region_file)
        except Exception:
            region = EmptyRegion(region_x, region_z)
    else:
        region = EmptyRegion(region_x, region_z)

    print("\n1. Direct region and chunk operations:")

    # set_block via region
    print("   - Setting block via Region.set_block...")
    test_block = Block.from_name("minecraft:diamond_block")
    try:
        region.set_block(test_block, 100, 64, 100, region_file)
        print("      Block set")
    except Exception as e:
        print(f"      Error: {e}")

    # get_block via chunk
    print("   - Getting block via Chunk.get_block...")
    chunk = region.get_chunk(0, 0) or EmptyChunk(0, 0)
    try:
        block = chunk.get_block(4, 64, 4)  # Convert global coords to chunk local
        print(f"      Retrieved block: {block.name() if block else 'None'}")
    except Exception as e:
        print(f"      Error: {e}")

    # set_biome via chunk
    print("   - Setting biome via Chunk.set_biome...")
    try:
        chunk.set_biome(Biome.from_name("minecraft:desert"), 4, 4)
        print("      Biome set")
    except Exception as e:
        print(f"      Error: {e}")

    # get_biome via chunk
    print("   - Getting biome via Chunk.get_biome...")
    try:
        biome = chunk.get_biome(4, 64)
        print(f"      Retrieved biome: {biome.name() if biome else 'None'}")
    except Exception as e:
        print(f"      Error: {e}")

    # Save region
    print("   - Saving region...")
    try:
        region.save(region_file)
        print("      Region saved")
    except Exception as e:
        print(f"      Error: {e}")

    # Cache operations on region
    print("   - Region cache operations...")
    if isinstance(region, Region):
        region.clear_cache()
        print("      Cache cleared")
        print(f"      Cache stats: {region.get_cache_stats()}")
    else:
        print("      EmptyRegion has no cache")


def demo_error_handling(world_path: str):
    """Demonstrate error handling in Chunk and Region operations."""
    print("\n" + "="*60)
    print("ERROR HANDLING DEMO")
    print("="*60)

    # Get region
    region_x, region_z = 0, 0
    region_file = os.path.join(world_path, "region", f"r.{region_x}.{region_z}.mca")
    if os.path.exists(region_file):
        try:
            region = Region.from_file(region_file)
        except Exception:
            region = EmptyRegion(region_x, region_z)
    else:
        region = EmptyRegion(region_x, region_z)

    print("\n1. Testing out-of-bounds coordinates:")

    chunk = region.get_chunk(0, 0) or EmptyChunk(0, 0)

    # Test invalid coordinates
    test_cases = [
        ("chunk.get_block(-1, 64, 8)", lambda: chunk.get_block(-1, 64, 8)),
        ("chunk.get_block(16, 64, 8)", lambda: chunk.get_block(16, 64, 8)),
        ("chunk.get_block(8, -1000, 8)", lambda: chunk.get_block(8, -1000, 8)),
        ("chunk.get_block(8, 64, -1)", lambda: chunk.get_block(8, 64, -1)),
        ("chunk.get_block(8, 64, 16)", lambda: chunk.get_block(8, 64, 16)),
    ]

    for test_name, test_func in test_cases:
        try:
            result = test_func()
            print(f"   - {test_name}: Unexpected success - {result}")
        except OutOfBoundsCoordinates as e:
            print(f"   - {test_name}: Correctly raised OutOfBoundsCoordinates")
        except Exception as e:
            print(f"   - {test_name}: Unexpected error - {type(e).__name__}: {e}")

    print("\n2. Testing invalid region operations:")

    # Try to access non-existent region file
    try:
        region = Region.from_file("nonexistent.mca")
        print("   - Loading non-existent region: Unexpected success")
    except FileNotFoundError:
        print("   - Loading non-existent region: Correctly raised FileNotFoundError")
    except Exception as e:
        print(f"   - Loading non-existent region: Unexpected error - {type(e).__name__}: {e}")


def demo_performance_aspects(world_path: str):
    """Demonstrate performance-related features."""
    print("\n" + "="*60)
    print("PERFORMANCE FEATURES DEMO")
    print("="*60)

    # Get region
    region_x, region_z = 0, 0
    region_file = os.path.join(world_path, "region", f"r.{region_x}.{region_z}.mca")
    if os.path.exists(region_file):
        try:
            region = Region.from_file(region_file)
        except Exception:
            region = EmptyRegion(region_x, region_z)
    else:
        region = EmptyRegion(region_x, region_z)

    print("\n1. Region cache performance:")

    if isinstance(region, Region):
        # Load several chunks to test caching
        print("   - Loading chunks to test caching...")
        chunks_loaded = 0
        for cx in range(5):
            for cz in range(5):
                chunk = region.get_chunk(cx, cz)
                if chunk:
                    chunks_loaded += 1
        print(f"      Loaded {chunks_loaded} chunks")

        # Check cache stats
        stats = region.get_cache_stats()
        print(f"      Cache stats: {stats}")

        print("\n2. Chunk streaming operations:")

        # Test streaming blocks from a chunk
        chunk = region.get_chunk(0, 0)
        if chunk and isinstance(chunk, Chunk):
            print("   - Streaming blocks from chunk...")
            block_count = 0
            unique_blocks = set()
            for block in chunk.stream_chunk():
                block_count += 1
                unique_blocks.add(block.name() if hasattr(block, 'name') else str(block))
                if block_count >= 1000:  # Limit for demo
                    break
            print(f"      Streamed {block_count} blocks, {len(unique_blocks)} unique types")
        else:
            print("   - No chunk available for streaming")
    else:
        print("   - EmptyRegion has no performance features to demonstrate")


def demo_replace_diamond_ore(world_path: str):
    """Demonstrate replacing diamond ore with gold blocks."""
    print("\n" + "="*60)
    print("DIAMOND ORE REPLACEMENT DEMO")
    print("="*60)

    # Get region
    region_x, region_z = 0, 0
    region_file = os.path.join(world_path, "region", f"r.{region_x}.{region_z}.mca")
    if os.path.exists(region_file):
        try:
            region = Region.from_file(region_file)
        except Exception as e:
            print(f"Error loading region: {e}")
            region = EmptyRegion(region_x, region_z)
    else:
        print(f"Region file {region_file} does not exist. Creating EmptyRegion.")
        region = EmptyRegion(region_x, region_z)

    if isinstance(region, Region):
        print("\n1. Replacing diamond ore with gold blocks:")

        # Count diamond ore blocks before replacement
        print("   - Counting diamond ore blocks...")
        diamond_ore_count = 0
        for cx in range(32):  # All chunks in region
            for cz in range(32):
                chunk = region.get_chunk(cx, cz)
                if chunk and isinstance(chunk, Chunk):
                    for block in chunk.stream_chunk():
                        if hasattr(block, 'name') and block.name() == "minecraft:diamond_ore":
                            diamond_ore_count += 1
        print(f"      Found {diamond_ore_count} diamond ore blocks")

        # Replace diamond ore with gold blocks
        print("   - Replacing diamond ore with gold blocks...")
        replaced_count = region.replace_blocks("minecraft:diamond_ore", "minecraft:gold_block", region_file)
        print(f"      Replaced {replaced_count} blocks")

        # Save the region
        print("   - Saving region...")
        region.save(region_file)
        print("      Region saved with gold blocks instead of diamond ore")
    else:
        print("   - EmptyRegion: No blocks to replace")


def main():
    """Main demonstration function."""
    print("Minecraft Anvil Library - Comprehensive Chunk & Region Demo")
    print("="*70)

    # Use the specified world path
    world_path = r"C:\Users\zayd2\AppData\Roaming\.minecraft\saves\testlib"
    if not os.path.exists(world_path):
        print(f"Warning: World path {world_path} does not exist. Creating...")
        os.makedirs(world_path, exist_ok=True)

    try:
        # Run all demos
        demo_region_functionality(world_path)
        demo_chunk_functionality(world_path)
        demo_world_integration(world_path)
        demo_error_handling(world_path)
        demo_performance_aspects(world_path)
        demo_replace_diamond_ore(world_path)

        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Test world location: {world_path}")

    except Exception as e:
        print(f"\nDemo failed with error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
