"""
Demonstration of biome manipulation features in the World facade.

This script demonstrates:
1. Getting biome at specific coordinates
2. Setting biome for a single block position (4x4x4 volume)
3. Setting biome for an entire chunk
4. Setting biome for a section within a chunk
5. Setting biome for an entire region

Usage:
    python demo_biomes.py
"""

import _path
from anvil import World, Biome
import os


def demo_get_biome():
    """Demonstrate getting biome at coordinates."""
    print("\n=== Demo: Get Biome ===")
    # Example - you need to have a valid world path
    # world = World(r'C:\path\to\your\world')
    # biome = world.get_biome(100, 64, -50)
    # if biome:
    #     print(f"Biome at (100, 64, -50): {biome.name()}")
    print("Get biome at global coordinates (x, y, z)")
    print("Example: biome = world.get_biome(100, 64, -50)")


def demo_set_biome():
    """Demonstrate setting biome at coordinates."""
    print("\n=== Demo: Set Biome ===")
    print("Set biome at global coordinates (affects 4x4x4 volume)")
    print("Example:")
    print("  desert = Biome.from_name('minecraft:desert')")
    print("  world.set_biome(desert, 100, 64, -50)")


def demo_set_chunk_biome():
    """Demonstrate setting entire chunk to a biome."""
    print("\n=== Demo: Set Chunk Biome ===")
    print("Set entire chunk to a single biome (optimized)")
    print("Example:")
    print("  ice_spikes = Biome.from_name('minecraft:ice_spikes')")
    print("  world.set_chunk_biome(ice_spikes, chunk_x=5, chunk_z=-3)")


def demo_set_section_biome():
    """Demonstrate setting a section to a biome."""
    print("\n=== Demo: Set Section Biome ===")
    print("Set a specific section (16x16x16) within a chunk to a biome")
    print("Example:")
    print("  jungle = Biome.from_name('minecraft:jungle')")
    print("  world.set_section_biome(jungle, chunk_x=5, chunk_z=-3, section_y=4)")
    print("  # section_y typically ranges from -4 to 19 for standard world height")


def demo_set_region_biome():
    """Demonstrate setting entire region to a biome."""
    print("\n=== Demo: Set Region Biome ===")
    print("Set all chunks in a region (32x32 chunks) to a single biome")
    print("Example:")
    print("  plains = Biome.from_name('minecraft:plains')")
    print("  world.set_region_biome(plains, region_x=0, region_z=0)")


def demo_biome_names():
    """Show some common biome names."""
    print("\n=== Common Biome Names ===")
    common_biomes = [
        "minecraft:plains",
        "minecraft:desert",
        "minecraft:forest",
        "minecraft:taiga",
        "minecraft:jungle",
        "minecraft:swamp",
        "minecraft:savanna",
        "minecraft:ice_spikes",
        "minecraft:mushroom_fields",
        "minecraft:ocean",
        "minecraft:deep_ocean",
        "minecraft:warm_ocean",
        "minecraft:frozen_ocean",
        "minecraft:river",
        "minecraft:beach",
        "minecraft:snowy_beach",
        "minecraft:mountains",
        "minecraft:badlands",
        "minecraft:nether_wastes",
        "minecraft:crimson_forest",
        "minecraft:warped_forest",
        "minecraft:soul_sand_valley",
        "minecraft:basalt_deltas",
        "minecraft:the_end",
        "minecraft:small_end_islands",
        "minecraft:end_highlands",
    ]
    
    for biome_name in common_biomes:
        print(f"  - {biome_name}")


def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("Biome Manipulation Demonstrations")
    print("=" * 60)
    
    demo_biome_names()
    demo_get_biome()
    demo_set_biome()
    demo_set_chunk_biome()
    demo_set_section_biome()
    demo_set_region_biome()
    
    print("\n" + "=" * 60)
    print("Complete API Example:")
    print("=" * 60)
    print("""
from anvil import World, Biome

# Initialize world
world = World(r'C:\\path\\to\\your\\world')

# Get biome at coordinates
biome = world.get_biome(100, 64, -50)
print(f"Current biome: {biome.name()}")

# Set biome for a single position (4x4x4 volume)
desert = Biome.from_name('minecraft:desert')
world.set_biome(desert, 100, 64, -50)

# Set entire chunk to ice spikes
ice_spikes = Biome.from_name('minecraft:ice_spikes')
world.set_chunk_biome(ice_spikes, chunk_x=5, chunk_z=-3)

# Set a section to jungle
jungle = Biome.from_name('minecraft:jungle')
world.set_section_biome(jungle, chunk_x=5, chunk_z=-3, section_y=4)

# Set entire region to plains
plains = Biome.from_name('minecraft:plains')
world.set_region_biome(plains, region_x=0, region_z=0)

# Save changes
world.save()
    """)
    
    print("\n" + "=" * 60)
    print("Note: Replace 'C:\\path\\to\\your\\world' with your actual world path")
    print("=" * 60)


if __name__ == '__main__':
    main()
