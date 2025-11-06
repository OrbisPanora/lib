import sys
import os
import shutil
import _path
import anvil
from nbt import nbt

if len(sys.argv) != 5:
    print("Usage: python test_structure.py <region_file.mca> <chunk_x> <chunk_z> <structure.nbt>")
    print("Example: python test_structure.py r.0.0.mca 0 0 plains_small_house.nbt")
    sys.exit(1)

region_file = sys.argv[1]
chunk_x = int(sys.argv[2])
chunk_z = int(sys.argv[3])
structure_file = sys.argv[4]

output_file = f"structure_{os.path.basename(region_file)}"
shutil.copy2(region_file, output_file)

chunk = anvil.Chunk.from_region(output_file, chunk_x, chunk_z)
print(f"Chunk loaded: ({chunk.x}, {chunk.z})")

structure = anvil.Structure.from_file(structure_file)
chunk = structure.generate(chunk, 100)

chunk.save(output_file)