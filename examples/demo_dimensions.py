import anvil
from anvil import Block

world_path = r'yourpath'

print("=" * 60)
print("DIMENSION SUPPORT DEMO")
print("=" * 60)

print("\n1. OVERWORLD (Default Dimension)")
print("-" * 60)
world = anvil.World(world_path, dimension='overworld')
info = world.get_dimension_info()
print(f"Dimension: {info['name']}")
print(f"Path: {info['path']}")
print(f"Full path: {info['full_path']}")
print(f"Loaded regions: {info['loaded_regions']}")

block = world.get_block(0, 64, 0)
if block:
    print(f"Block at (0, 64, 0): {block.name()}")

world.set_block(Block('minecraft', 'diamond_block'), 100, 64, 100)
print("Set diamond block at (100, 64, 100) in Overworld")

print("\n2. NETHER (DIM-1)")
print("-" * 60)
world.switch_dimension('nether', save_current=True)
info = world.get_dimension_info()
print(f"Dimension: {info['name']}")
print(f"Path: {info['path']}")
print(f"Full path: {info['full_path']}")

block = world.get_block(0, 64, 0)
if block:
    print(f"Block at (0, 64, 0): {block.name()}")
else:
    print("No block found at (0, 64, 0) - chunk may not be generated")

world.set_block(Block('minecraft', 'netherrack'), 50, 64, 50)
print("Set netherrack at (50, 64, 50) in Nether")

print("\n3. THE END (DIM1)")
print("-" * 60)
world.switch_dimension('end', save_current=True)
info = world.get_dimension_info()
print(f"Dimension: {info['name']}")
print(f"Path: {info['path']}")
print(f"Full path: {info['full_path']}")

block = world.get_block(0, 64, 0)
if block:
    print(f"Block at (0, 64, 0): {block.name()}")
else:
    print("No block found at (0, 64, 0) - chunk may not be generated")

world.set_block(Block('minecraft', 'end_stone'), 25, 64, 25)
print("Set end_stone at (25, 64, 25) in The End")

print("\n4. CREATING SEPARATE WORLD INSTANCES")
print("-" * 60)
overworld = anvil.World(world_path, dimension='overworld')
nether = anvil.World(world_path, dimension='nether')
end = anvil.World(world_path, dimension='end')

print(f"Overworld dimension: {overworld.get_dimension()}")
print(f"Nether dimension: {nether.get_dimension()}")
print(f"End dimension: {end.get_dimension()}")

overworld.set_block(Block('minecraft', 'grass_block'), 10, 64, 10)
nether.set_block(Block('minecraft', 'soul_sand'), 10, 64, 10)
end.set_block(Block('minecraft', 'end_stone'), 10, 64, 10)

print("\nSet blocks in all three dimensions simultaneously")

print("\n5. WORKING WITH NETHER PORTALS")
print("-" * 60)
overworld_coords = (800, 64, 800)
nether_coords = (overworld_coords[0] // 8, overworld_coords[1], overworld_coords[2] // 8)

print(f"Overworld coordinates: {overworld_coords}")
print(f"Corresponding Nether coordinates: {nether_coords}")

overworld.set_block(Block('minecraft', 'obsidian'), *overworld_coords)
nether.set_block(Block('minecraft', 'obsidian'), *nether_coords)
print("Created portal markers in both dimensions")

print("\n6. SAVING ALL DIMENSIONS")
print("-" * 60)
overworld.save()
print("Saved Overworld")
nether.save()
print("Saved Nether")
end.save()
print("Saved The End")

print("\n" + "=" * 60)
print("DEMO COMPLETE")
print("=" * 60)
print("\nTips:")
print("  - Use dimension parameter when creating World instance")
print("  - Use switch_dimension() to change dimensions on existing instance")
print("  - Nether coordinates are 1/8 of Overworld coordinates (X and Z)")
print("  - Each dimension has its own region files")
print("  - Remember to save() before switching dimensions")
