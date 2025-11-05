import _path
import os
import anvil
import sys
import time

if len(sys.argv) < 2:
    print("Usage: python modify_existing_world.py <path_to_minecraft_world> [x y z]")
    print("Example: python modify_existing_world.py C:\\Users\\username\\AppData\\Roaming\\.minecraft\\saves\\MyWorld 0 100 0")
    print("If coordinates are not provided, a diamond block will be placed at (0, 100, 0)")
    sys.exit(1)

WORLD_FOLDER = sys.argv[1]

if not os.path.exists(WORLD_FOLDER):
    print(f"Error: The folder {WORLD_FOLDER} does not exist.")
    sys.exit(1)

region_folder = os.path.join(WORLD_FOLDER, "region")
if not os.path.exists(region_folder):
    print(f"Error: The folder {region_folder} does not exist. Is this a Minecraft world?")
    sys.exit(1)

print(f"Loading world from {WORLD_FOLDER}...")

try:
    world = anvil.World(WORLD_FOLDER)
    
    diamond_block = anvil.Block('minecraft', 'diamond_block')
    
    if len(sys.argv) >= 5:
        try:
            spawn_x = int(sys.argv[2])
            spawn_y = int(sys.argv[3])
            spawn_z = int(sys.argv[4])
        except ValueError:
            print("Error: Coordinates must be integers. Using default coordinates.")
            spawn_x, spawn_y, spawn_z = 0, 100, 0
    else:
        spawn_x, spawn_y, spawn_z = 0, 100, 0
    
    print(f"Placing a diamond block at coordinates ({spawn_x}, {spawn_y}, {spawn_z})...")
    start_time = time.time()
    world.set_block(diamond_block, spawn_x, spawn_y, spawn_z)

    print("Saving changes...")
    world.save()
    
    end_time = time.time()
    print(f"Changes applied successfully in {end_time - start_time:.2f} seconds!")
    print(f"A diamond block has been placed at coordinates ({spawn_x}, {spawn_y}, {spawn_z})")
    print("You can now open this world in Minecraft to see the changes.")
    
    region_x = spawn_x >> 9  
    region_z = spawn_z >> 9  
    region_file = os.path.join(region_folder, f"r.{region_x}.{region_z}.mca")
    
    if os.path.exists(region_file):
        print(f"Modified existing region file: {os.path.basename(region_file)}")
    else:
        print(f"Created new region file: {os.path.basename(region_file)}")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
