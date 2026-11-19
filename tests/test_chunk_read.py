"""Reading chunks from the committed region file (a 1.21 world, data version 3955)."""
from pathlib import Path

import pytest

from orbispanora_lib.anvil import Biome, Block, Chunk, Region
from orbispanora_lib.anvil.errors import OutOfBoundsCoordinates

REGION_FIXTURE = Path(__file__).parent / 'world_files' / 'r.0.0.mca'


@pytest.fixture(scope='module')
def chunk():
    """Chunk (0, 0) of the committed region."""
    return Region.from_file(str(REGION_FIXTURE)).get_chunk(0, 0)


def test_chunk_metadata(chunk):
    assert (chunk.x, chunk.z) == (0, 0)
    assert chunk.version == 3955


def test_get_section_range(chunk):
    assert chunk.get_section(0)["Y"].value == 0
    assert chunk.get_section(-4)["Y"].value == -4
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.get_section(99)


def test_get_palette(chunk):
    palette = chunk.get_palette(0)
    assert palette is not None
    assert all(isinstance(block, Block) for block in palette)
    assert chunk.get_palette(chunk.get_section(0)) == palette


def test_get_block_and_bounds(chunk):
    assert chunk.get_block(1, -64, 1).name() == 'minecraft:bedrock'
    assert chunk.get_block(0, 62, 0, force_new=True).name() == 'minecraft:water'
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.get_block(16, 0, 0)
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.get_block(0, 0, -1)
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.get_block(0, 10000, 0)


def test_get_biome(chunk):
    biome = chunk.get_biome(0, 64, 0)
    assert isinstance(biome, Biome)
    assert biome.name() == 'minecraft:river'
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.get_biome(16, 0, 0)


def test_stream_blocks_section_has_4096_blocks(chunk):
    assert sum(1 for _ in chunk.stream_blocks(section=0)) == 4096
    assert sum(1 for _ in chunk.stream_blocks(index=4000, section=0)) == 96


def test_stream_blocks_rejects_bad_section(chunk):
    with pytest.raises(OutOfBoundsCoordinates):
        list(chunk.stream_blocks(section=99))


def test_stream_chunk_has_every_block(chunk):
    assert sum(1 for _ in chunk.stream_chunk()) == 24 * 4096


def test_to_dict(chunk):
    simple = chunk.to_dict()
    assert simple['x'] == 0 and simple['z'] == 0 and simple['version'] == 3955
    assert isinstance(simple['sections'], list)
    full = chunk.to_dict(simplify=False)
    assert isinstance(full['sections'], list)
    with_blocks = chunk.to_dict(simplify=False, include_blocks=True)
    assert with_blocks['x'] == 0


def test_heightmap_matches_surface_height(chunk):
    heightmap = chunk.to_heightmap()
    assert len(heightmap) == 16 and all(len(row) == 16 for row in heightmap)
    assert heightmap[0][0] == chunk.get_surface_height(0, 0) == 62


def test_surface_blocks(chunk):
    blocks = chunk.get_surface_blocks()
    assert len(blocks) == 256
    assert set(blocks[0]) == {'x', 'y', 'z', 'block'}
    assert blocks[0]['block'] == 'minecraft:water'
    with_biome = chunk.get_surface_blocks(include_biome=True)
    assert with_biome[0]['biome'] == 'minecraft:river'


def test_tile_entity_absent(chunk):
    assert chunk.get_tile_entity(0, 0, 0) is None


def test_from_region_accepts_path_and_region():
    path = str(REGION_FIXTURE)
    from_path = Chunk.from_region(path, 0, 0)
    from_region = Chunk.from_region(Region.from_file(path), 0, 0)
    assert from_path.version == from_region.version == 3955
