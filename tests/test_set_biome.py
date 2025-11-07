import context as _
from anvil import Region, Biome
import shutil
import os

def test_set_entire_chunk_biome(tmp_path):
	original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
	test_file = tmp_path / "test_set_chunk_biome.mca"
	shutil.copy(original_file, test_file)

	# Load region file
	region = Region.from_file(str(test_file))
	chunk = region.get_chunk(0, 0)

	if chunk is None:
		print("Chunk (0, 0) doesn't exist, skipping test")
		return

	# Set entire chunk to ice spikes biome
	print("Setting entire chunk (0, 0) to ice spikes biome...")
	ice_spikes_biome = Biome.from_name("minecraft:ice_spikes")
	chunk.set_chunk_biome(ice_spikes_biome)

	print("Chunk (0, 0) set to ice spikes!")

	# Save changes
	region.save_chunk(chunk, str(test_file))

	# Verify several positions reflect the biome
	for x, y, z in [(0, 0, 0), (8, 40, 8), (15, 255, 15)]:
		assert chunk.get_biome(x, y, z).name() == ice_spikes_biome.name()


def test_set_single_block_biome(tmp_path):
	original_file = os.path.join(os.path.dirname(__file__), 'world_files', 'r.0.0.mca')
	test_file = tmp_path / "test_set_single_biome.mca"
	shutil.copy(original_file, test_file)

	# Load region file
	region = Region.from_file(str(test_file))
	chunk = region.get_chunk(0, 0)

	if chunk is None:
		print("Chunk (0, 0) doesn't exist, skipping test")
		return

	print("\n" + "="*60)
	print("Setting single block biome in chunk (0, 0)")
	print("="*60)

	# Set a single block position to jungle biome in the previous chunk

	# This actually sets the entire 4x4x4 biome cell containing this position
	print("\nSetting biome at position (8, 40, 8) to jungle...")
	jungle_biome = Biome.from_name("minecraft:jungle")
	chunk.set_biome(jungle_biome, 8, 40, 8)

	# Verify the biome was set
	actual_biome = chunk.get_biome(8, 40, 8)
	print(f"Biome at (8, 40, 8): {actual_biome}")
	print(f"Match: {'Passed' if actual_biome.name() == jungle_biome.name() else 'Failed'}")

	# Save changes
	region.save_chunk(chunk, str(test_file))
