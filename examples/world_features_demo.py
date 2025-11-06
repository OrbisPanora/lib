import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import anvil
from anvil import World, Block

def demonstrate_world_features():
    """Demonstrate all World class features."""
    
    world = World("demo_world")
    
    print("=== World Class Features Demonstration ===\n")
    
    print("1. Basic Block Operations:")
    diamond_block = Block.from_name("minecraft:diamond_block")
    world.set_block(diamond_block, 0, 100, 0)
    
    block = world.get_block(0, 100, 0)
    print(f"   Placed block at (0, 100, 0): {block.name()}")
    
    print("\n2. Block Replacement Operations:")
    stone = Block.from_name("minecraft:stone")
    dirt = Block.from_name("minecraft:dirt")
    
    for x in range(5):
        for z in range(5):
            world.set_block(stone, x, 64, z)
    
    print("   Created 5x5 stone area at Y=64")
    
    success = world.replace_block_at(2, 64, 2, "minecraft:gold_block")
    print(f"   Replaced center block with gold: {success}")
    
    count = world.replace_blocks_in_area("minecraft:stone", "minecraft:dirt", 0, 64, 0, 4, 64, 4)
    print(f"   Replaced {count} stone blocks with dirt")
    
    print("\n3. Streaming Operations:")
    
    print("   Streaming blocks in 3x3x3 area:")
    block_count = 0
    for x, y, z, block in world.stream_blocks(0, 63, 0, 2, 65, 2):
        if block is not None:
            print(f"     Found {block.name()} at ({x}, {y}, {z})")
            block_count += 1
    
    print(f"   Total blocks streamed: {block_count}")
    
    print("\n   Streaming chunks in area:")
    chunk_count = 0
    for chunk_x, chunk_z, chunk in world.stream_chunks(0, 0, 1, 1):
        if chunk:
            print(f"     Found chunk at ({chunk_x}, {chunk_z})")
            chunk_count += 1
    
    print(f"   Total chunks streamed: {chunk_count}")
    
    print("\n4. Utility Functions:")
    
    dirt_count = world.count_blocks("minecraft:dirt")
    print(f"   Total dirt blocks: {dirt_count}")
    
    gold_count = world.count_blocks("minecraft:gold_block")
    print(f"   Total gold blocks: {gold_count}")
    
    bounds = world.get_world_bounds()
    if bounds:
        print(f"   World bounds: {bounds}")
    
    regions = world.get_loaded_regions()
    print(f"   Loaded regions: {regions}")
    
    print("\n5. Advanced Example - Building Pattern:")
    
    black = Block.from_name("minecraft:black_wool")
    white = Block.from_name("minecraft:white_wool")
    
    print("   Creating 8x8 checkerboard pattern:")
    for x in range(8):
        for z in range(8):
            if (x + z) % 2 == 0:
                world.set_block(black, x + 10, 64, z + 10)
            else:
                world.set_block(white, x + 10, 64, z + 10)
    
    black_count = world.count_blocks("minecraft:black_wool", (10, 64, 10, 17, 64, 17))
    white_count = world.count_blocks("minecraft:white_wool", (10, 64, 10, 17, 64, 17))
    
    print(f"   Black wool blocks: {black_count}")
    print(f"   White wool blocks: {white_count}")
    
    glass_count = world.replace_blocks_in_area("minecraft:black_wool", "minecraft:glass", 
                                              10, 64, 10, 17, 64, 17)
    glass_count += world.replace_blocks_in_area("minecraft:white_wool", "minecraft:glass", 
                                               10, 64, 10, 17, 64, 17)
    print(f"   Replaced {glass_count} wool blocks with glass")
    
    print("\n6. Saving World:")
    world.save()
    print("   World saved successfully!")
    
    print("\n=== Demonstration Complete ===")
    print(f"Demo world created in: {os.path.abspath('demo_world')}")

def demonstrate_performance():
    """Demonstrate performance with larger operations."""
    
    print("\n=== Performance Demonstration ===\n")
    
    world = World("performance_demo")
    
    print("Creating large area (50x50)...")
    stone = Block.from_name("minecraft:stone")
    
    for x in range(50):
        for z in range(50):
            world.set_block(stone, x, 64, z)
    
    print("Large area created!")
    
    import time
    
    start_time = time.time()
    stone_count = world.count_blocks("minecraft:stone")
    end_time = time.time()
    
    print(f"Counted {stone_count} stone blocks in {end_time - start_time:.4f} seconds")
    
    start_time = time.time()
    diamond_count = world.replace_blocks_in_area("minecraft:stone", "minecraft:diamond_block", 
                                                0, 64, 0, 49, 64, 49)
    end_time = time.time()
    
    print(f"Replaced {diamond_count} blocks in {end_time - start_time:.4f} seconds")
    
    world.save()
    print("Performance demo saved!")

if __name__ == "__main__":
    demonstrate_world_features()
    demonstrate_performance()
