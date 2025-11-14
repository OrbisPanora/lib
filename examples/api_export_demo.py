"""
Demonstration of API-friendly export methods for the isometric viewer.
This example shows how to use the new methods added to the library
for exporting Minecraft world data in formats optimized for web APIs.

Target: Minecraft 1.21.1
Purpose: Isometric 2.5D viewer with Angular frontend
"""

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from anvil import World, Region, Block

def demo_block_serialization():
    """Demo: Block to_dict() method"""
    print("=" * 60)
    print("1. BLOCK SERIALIZATION")
    print("=" * 60)
    
    grass = Block.from_name("minecraft:grass_block")
    stone = Block.from_name("minecraft:stone")
    water = Block.from_name("minecraft:water", properties={"level": "0"})
    
    print("\nGrass block:")
    print(json.dumps(grass.to_dict(), indent=2))
    
    print("\nWater block with properties:")
    print(json.dumps(water.to_dict(), indent=2))
    print()


def demo_chunk_methods(world_path: str):
    """Demo: Chunk export methods"""
    print("=" * 60)
    print("2. CHUNK EXPORT METHODS")
    print("=" * 60)
    
    world = World(world_path)
    chunk = world.get_chunk(0, 0)
    
    if chunk is None:
        print("Chunk (0, 0) not found!")
        return
    
    print("\n2.1 Heightmap (16x16 grid):")
    heightmap = chunk.to_heightmap()
    print(f"Size: {len(heightmap)}x{len(heightmap[0])}")
    print(f"Sample heights: {heightmap[0][:5]}")
    print(f"JSON size: ~{len(json.dumps(heightmap))} bytes")
    
    print("\n2.2 Surface blocks (visible blocks only):")
    surface = chunk.get_surface_blocks(include_biome=True)
    print(f"Number of surface blocks: {len(surface)}")
    if surface:
        print(f"First block: {json.dumps(surface[0], indent=2)}")
    print(f"JSON size: ~{len(json.dumps(surface))} bytes")
    
    print("\n2.3 Simplified chunk data (palette only):")
    simplified = chunk.to_dict(simplify=True)
    print(f"Sections: {len(simplified['sections'])}")
    if simplified['sections']:
        print(f"First section palette: {simplified['sections'][0]['palette'][:3]}...")
    print(f"JSON size: ~{len(json.dumps(simplified))} bytes")
    
    print()


def demo_world_api_methods(world_path: str):
    """Demo: World API export methods"""
    print("=" * 60)
    print("3. WORLD API METHODS")
    print("=" * 60)
    
    world = World(world_path)
    
    print("\n3.1 World Info:")
    info = world.get_world_info()
    print(json.dumps(info, indent=2, default=str))
    
    print("\n3.2 Chunk Data (heightmap mode):")
    chunk_data = world.get_chunk_data(0, 0, mode='heightmap')
    if chunk_data:
        print(f"Chunk coordinates: ({chunk_data['chunk_x']}, {chunk_data['chunk_z']})")
        print(f"Heightmap size: {len(chunk_data['heightmap'])}x{len(chunk_data['heightmap'][0])}")
        print(f"JSON size: ~{len(json.dumps(chunk_data))} bytes")
    
    print("\n3.3 Chunk Data (surface mode):")
    chunk_data = world.get_chunk_data(0, 0, mode='surface')
    if chunk_data:
        print(f"Surface blocks: {len(chunk_data['surface_blocks'])}")
        print(f"JSON size: ~{len(json.dumps(chunk_data))} bytes")
    
    print("\n3.4 Area Heightmap (64x64 blocks):")
    area = world.get_area_heightmap(0, 0, 63, 63)
    print(f"Area: ({area['x1']}, {area['z1']}) to ({area['x2']}, {area['z2']})")
    print(f"Dimensions: {area['width']}x{area['height']}")
    print(f"JSON size: ~{len(json.dumps(area))} bytes")
    
    print("\n3.5 Tile Data (16x16 chunks):")
    tile = world.get_tile_data(0, 0, tile_size=4)  # Smaller tile for demo
    print(f"Tile: ({tile['tile_x']}, {tile['tile_z']})")
    print(f"Chunks in tile: {tile['chunk_count']}")
    print(f"JSON size: ~{len(json.dumps(tile))} bytes")
    
    print()


def demo_api_response_formats(world_path: str):
    """Demo: Typical API response formats"""
    print("=" * 60)
    print("4. TYPICAL API RESPONSE FORMATS")
    print("=" * 60)
    
    world = World(world_path)
    
    print("\n4.1 GET /api/world/info")
    response = {
        "status": "success",
        "data": world.get_world_info()
    }
    print(json.dumps(response, indent=2, default=str))
    
    print("\n4.2 GET /api/chunk/0/0?mode=heightmap")
    chunk_data = world.get_chunk_data(0, 0, mode='heightmap')
    if chunk_data:
        response = {
            "status": "success",
            "data": chunk_data
        }
        print(f"Response size: ~{len(json.dumps(response))} bytes")
        print("Sample response:")
        print(json.dumps({
            "status": "success",
            "data": {
                "chunk_x": chunk_data['chunk_x'],
                "chunk_z": chunk_data['chunk_z'],
                "heightmap": [chunk_data['heightmap'][0][:5], "..."]
            }
        }, indent=2))
    
    print("\n4.3 GET /api/heightmap/area?x1=0&z1=0&x2=32&z2=32")
    area = world.get_area_heightmap(0, 0, 32, 32)
    response = {
        "status": "success",
        "data": {
            "bounds": {
                "x1": area['x1'],
                "z1": area['z1'],
                "x2": area['x2'],
                "z2": area['z2']
            },
            "dimensions": {
                "width": area['width'],
                "height": area['height']
            },
            "heightmap": "..." # Truncated for display
        }
    }
    print(json.dumps(response, indent=2))
    print(f"Full response size: ~{len(json.dumps(area))} bytes")
    
    print()


def demo_performance_comparison(world_path: str):
    """Demo: Performance comparison of different modes"""
    print("=" * 60)
    print("5. PERFORMANCE COMPARISON")
    print("=" * 60)
    
    world = World(world_path)
    
    modes = ['heightmap', 'surface', 'simplified']
    
    print("\nJSON size comparison for chunk (0, 0):")
    print("-" * 40)
    
    for mode in modes:
        chunk_data = world.get_chunk_data(0, 0, mode=mode)
        if chunk_data:
            size = len(json.dumps(chunk_data))
            print(f"{mode:12} : {size:6} bytes (~{size/1024:.1f} KB)")
    
    print("\nRecommendations:")
    print("- heightmap  : Best for initial load and minimap")
    print("- surface    : Best for isometric rendering")
    print("- simplified : Best for palette/metadata")
    print("- full       : Avoid unless absolutely necessary")
    
    print()


def main():
    """Main demo function"""
    print("\n" + "=" * 60)
    print("API EXPORT DEMO - Minecraft 1.21.1")
    print("For Isometric Viewer (Angular + Three.js)")
    print("=" * 60 + "\n")
    
    if len(sys.argv) < 2:
        print("Usage: python api_export_demo.py <world_path>")
        print("\nRunning basic demos without world data...")
        demo_block_serialization()
        print("\n Provide a world path to see full demos:")
        print("   python api_export_demo.py /path/to/minecraft/world")
        return
    
    world_path = sys.argv[1]
    
    if not os.path.exists(world_path):
        print(f"Error: World path '{world_path}' does not exist!")
        return
    
    demo_block_serialization()
    demo_chunk_methods(world_path)
    demo_world_api_methods(world_path)
    demo_api_response_formats(world_path)
    demo_performance_comparison(world_path)
    
    print("=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Create FastAPI backend using these methods")
    print("2. Build Angular frontend with Three.js")
    print("3. Implement tile-based progressive loading")
    print("4. Add texture mapping from assets/minecraft/textures/block/")
    print()


if __name__ == "__main__":
    main()
