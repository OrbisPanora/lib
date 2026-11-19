"""Reading and saving a region file."""
import pytest

from orbispanora_lib.anvil import Biome, Block, Region
from orbispanora_lib.anvil.errors import ChunkNotFound


@pytest.fixture
def region(region_file):
    """A region loaded from a writable copy of the committed file."""
    return Region.from_file(region_file)


def test_region_coordinates_come_from_the_file_name(region):
    assert (region.region_x, region.region_z) == (0, 0)


def test_chunk_location_and_missing_chunks(region):
    offset, sectors = region.chunk_location(0, 0)
    assert offset > 0 and sectors > 0
    assert region.chunk_location(31, 31) == (0, 0) or region.get_chunk(31, 31) is None
    assert Region.header_offset(0, 0) == 0
    assert Region.header_offset(1, 0) == 4


def test_chunk_not_generated(region):
    missing = next((x, z) for x in range(32) for z in range(32) if region.chunk_location(x, z) == (0, 0))
    with pytest.raises(ChunkNotFound):
        region.get_chunk(*missing)
    assert region.chunk_data(*missing) is None


def test_chunk_cache_counts_hits(region):
    region.get_chunk(0, 0)
    region.get_chunk(0, 0)
    stats = region.get_cache_stats()
    assert stats['hits'] >= 1 and stats['size'] == 1
    region.invalidate_chunk(0, 0)
    assert region.get_cache_stats()['size'] == 0
    region.get_chunk(0, 1)
    region.clear_cache()
    assert region.get_cache_stats()['size'] == 0


def test_region_without_cache_has_no_stats(region_file):
    assert Region.from_file(region_file, cache_size=None).get_cache_stats() is None


def test_to_dict(region):
    simple = region.to_dict()
    assert simple['region_x'] == 0 and simple['region_z'] == 0
    with_chunks = region.to_dict(include_chunks=True)
    assert [0, 0] in with_chunks['chunks']
    assert len(with_chunks['chunks']) == 287


def test_set_block_saves_to_file(region, region_file):
    region.set_block(Block('minecraft', 'emerald_block'), 3, 70, 3, region_file)
    reloaded = Region.from_file(region_file)
    assert reloaded.get_chunk(0, 0).get_block(3, 70, 3).name() == 'minecraft:emerald_block'


def test_replace_block_at(region, region_file):
    assert region.replace_block_at(0, 62, 0, 'minecraft:ice', region_file) is True
    assert Region.from_file(region_file).get_chunk(0, 0).get_block(0, 62, 0).name() == 'minecraft:ice'


def test_replace_block_at_in_missing_chunk_returns_false(region, region_file):
    missing = next((x, z) for x in range(32) for z in range(32) if region.chunk_location(x, z) == (0, 0))
    assert region.replace_block_at(missing[0] * 16, 62, missing[1] * 16, 'minecraft:ice', region_file) is False


def test_replace_blocks_in_one_chunk(region, region_file):
    count = region.replace_blocks('minecraft:water', 'minecraft:ice', region_file, chunks=(0, 0))
    assert count > 0
    chunk = Region.from_file(region_file).get_chunk(0, 0)
    assert chunk.get_block(0, 62, 0).name() == 'minecraft:ice'


def test_replace_blocks_in_a_list_of_chunks(region, region_file):
    count = region.replace_blocks('minecraft:water', 'minecraft:ice', region_file, chunks=[(0, 0), (0, 1)])
    assert count > 0


def test_replace_blocks_rejects_bad_chunks_argument(region, region_file):
    with pytest.raises(ValueError):
        region.replace_blocks('minecraft:water', 'minecraft:ice', region_file, chunks='all')


def test_set_region_biome(region, region_file):
    region.set_region_biome(Biome('minecraft', 'plains'), region_file)
    chunk = Region.from_file(region_file).get_chunk(0, 0)
    assert chunk.get_biome(0, 70, 0).name() == 'minecraft:plains'


def test_save_roundtrip_keeps_every_chunk(region, region_file):
    region.save(region_file)
    reloaded = Region.from_file(region_file)
    assert reloaded.to_dict(include_chunks=True)['chunks'] == region.to_dict(include_chunks=True)['chunks']


def test_save_chunk_rewrites_only_that_chunk(region, region_file):
    chunk = region.get_chunk(0, 0)
    chunk.set_block(Block('minecraft', 'gold_block'), 1, 70, 1)
    region.save_chunk(chunk, region_file)
    reloaded = Region.from_file(region_file)
    assert reloaded.get_chunk(0, 0).get_block(1, 70, 1).name() == 'minecraft:gold_block'
    assert reloaded.get_chunk(0, 1).get_block(0, -64, 0).name() == 'minecraft:bedrock'


def test_from_file_rejects_an_unnamed_region(tmp_path):
    path = tmp_path / 'not_a_region.mca'
    path.write_bytes(b'\x00' * 8192)
    with pytest.raises(ValueError):
        Region.from_file(str(path))
