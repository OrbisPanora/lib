#!/usr/bin/env python3

import sys
import os
import shutil
import _path
import anvil

if len(sys.argv) < 4:
    print("Usage: python test_diamond_cube.py <region_file.mca> <chunk_x> <chunk_z>")
    print("Example: python test_diamond_cube.py r.0.0.mca 0 0")
    sys.exit(1)

region_file = sys.argv[1]
chunk_x = int(sys.argv[2])
chunk_z = int(sys.argv[3])

output_file = f"diamond_cube_{os.path.basename(region_file)}"
shutil.copy2(region_file, output_file)
print(f"Copy created: {output_file}")

chunk = anvil.Chunk.from_region(output_file, chunk_x, chunk_z)
print(f"Chunk loaded: ({chunk.x}, {chunk.z})")

diamond = anvil.Block('minecraft', 'diamond_block')

print("Spawning 9x9 diamond cube...")
count = 0
for y in range(100, 109):
    for x in range(3, 12):
        for z in range(3, 12):
            chunk.set_block(diamond, x, y, z)
            count += 1

print(f"{count} diamond blocks placed.")

chunk.save(output_file)
print(f"Saved to {output_file}")

print(f"\nSuccess! File generated: {output_file}")
print(f"Cube position: chunk ({chunk_x},{chunk_z}), x=3-11, y=100-108, z=3-11")
print(f"{count} diamond blocks placed in the 9x9x9 cube.")
