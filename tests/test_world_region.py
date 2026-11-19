"""World operations on a copy of the committed region file."""
import pytest

from orbispanora_lib.anvil import Biome, Block, Chunk, World
from orbispanora_lib.patterns import Cube


@pytest.fixture
def world(world_dir):
    """A World over a folder holding a writable copy of `r.0.0.mca`."""
    return World(str(world_dir))


def test_world_info_and_bounds(world):
    info = world.get_world_info()
    assert info['size_x'] == 512 and info['size_z'] == 512
    assert world.get_world_bounds() == (0, -64, 0, 511, 320, 511)
    assert world.get_dimension() == 'overworld'
    assert world.get_dimension_info()['name'] == 'overworld'


def test_get_chunk_and_missing_chunk(world):
    assert isinstance(world.get_chunk(0, 0), Chunk)
    assert world.get_chunk(100, 100) is None


def test_get_block_and_biome(world):
    assert world.get_block(0, 62, 0).name() == 'minecraft:water'
    assert world.get_block(0, 62, 5000) is None
    assert world.get_biome(0, 62, 0).name() == 'minecraft:river'
    assert world.get_biome(0, 62, 5000) is None


def test_get_height_map(world):
    assert world.get_height_map(0, 0) == 62


@pytest.mark.parametrize('mode, keys', [
    ('heightmap', {'chunk_x', 'chunk_z', 'heightmap'}),
    ('surface', {'chunk_x', 'chunk_z', 'heightmap', 'surface_blocks'}),
    ('simplified', {'chunk_x', 'chunk_z', 'x', 'z', 'version', 'sections'}),
])
def test_get_chunk_data_modes(world, mode, keys):
    assert set(world.get_chunk_data(0, 0, mode)) == keys


def test_get_chunk_data_full_mode_and_errors(world):
    assert world.get_chunk_data(0, 0, 'full')['chunk_x'] == 0
    assert world.get_chunk_data(100, 100) is None
    with pytest.raises(ValueError):
        world.get_chunk_data(0, 0, 'unknown')


def test_get_tile_data(world):
    tile = world.get_tile_data(0, 0, tile_size=1)
    assert tile['tile_size'] == 1 and tile['chunk_count'] == 1


def test_area_heightmap(world):
    area = world.get_area_heightmap(0, 0, 3, 3)
    assert (area['width'], area['height']) == (4, 4)
    assert area['heightmap'][0][0] == 62


def test_scan_count_find_and_distribution(world):
    assert world.scan_area(0, 60, 0, 3, 63, 3) == {'minecraft:water': 48, 'minecraft:air': 16}
    assert world.count_blocks('minecraft:water', (0, 62, 0, 3, 62, 3)) == 16
    assert world.find_blocks('minecraft:water', (0, 62, 0, 3, 62, 3), limit=3) == [(0, 62, 0), (0, 62, 1), (0, 62, 2)]
    assert world.get_block_distribution((0, 60, 0, 3, 62, 3), top_n=2) == {'minecraft:water': 48}
    assert world.find_nearest_block('minecraft:water', 0, 70, 0, max_radius=10) == (0, 62, 0, 8.0)
    assert world.find_nearest_block('minecraft:diamond_block', 0, 70, 0, max_radius=2) is None


def test_stream_blocks_and_chunks(world):
    assert sum(1 for _ in world.stream_blocks(0, 60, 0, 1, 61, 1)) == 8
    assert len(list(world.stream_chunks(0, 0, 1, 1))) == 1


def test_fill_copy_and_clear(world):
    assert world.fill_area('minecraft:glass', 0, 100, 0, 3, 101, 3) == 32
    assert world.count_blocks('minecraft:glass', (0, 100, 0, 3, 101, 3)) == 32
    assert world.copy_area(0, 100, 0, 3, 101, 3, 8, 100, 8) == 32
    assert world.get_block(9, 100, 9).name() == 'minecraft:glass'
    assert world.clear_area(0, 100, 0, 3, 101, 3) == 32
    assert world.get_block(1, 100, 1).name() == 'minecraft:air'


def test_replace_blocks_variants(world):
    world.fill_area('minecraft:glass', 8, 100, 8, 11, 101, 11)
    assert world.replace_blocks_in_area('minecraft:glass', 'minecraft:stone', 8, 100, 8, 9, 101, 9) == 8
    assert world.replace_blocks('minecraft:stone', 'minecraft:dirt', (8, 100, 8, 11, 101, 11)) == 8
    assert world.replace_blocks('minecraft:dirt', 'minecraft:coal_block', (8, 100, 8, 11, 101, 11)) == 8
    assert world.get_block(8, 100, 8).name() == 'minecraft:coal_block'
    assert world.replace_block_at(8, 100, 8, 'minecraft:gold_block') is True
    assert world.get_block(8, 100, 8).name() == 'minecraft:gold_block'


def test_set_block_and_save_reload(world, world_dir):
    world.set_block(Block('minecraft', 'diamond_block'), 5, 70, 5)
    world.save()
    block = World(str(world_dir)).get_block(5, 70, 5)
    assert isinstance(block, Block)
    assert block.name() == 'minecraft:diamond_block'


def test_palette_helpers(world):
    world.set_block(Block('minecraft', 'sponge'), 8, 100, 8)
    assert world.is_in_palette_section(Block('minecraft', 'sponge'), 8, 100, 8)
    assert not world.is_in_palette_section(Block('minecraft', 'bookshelf'), 8, 100, 8)
    index = world.add_block_to_palette(Block('minecraft', 'bookshelf'), 8, 100, 8)
    assert index >= 1
    assert world.is_in_palette_section(Block('minecraft', 'bookshelf'), 8, 100, 8)


def test_biome_setters(world):
    world.set_biome(Biome('minecraft', 'desert'), 1, 70, 1)
    assert world.get_biome(1, 70, 1).name() == 'minecraft:desert'
    world.set_chunk_biome(Biome('minecraft', 'plains'), 0, 0)
    assert world.get_biome(5, 70, 5).name() == 'minecraft:plains'
    world.set_region_biome(Biome('minecraft', 'taiga'), 0, 0)
    assert world.get_biome(5, 70, 5).name() == 'minecraft:taiga'


def test_apply_figure(world):
    world.apply_figure(Cube, [Block('minecraft', 'sandstone')], (0, 100, 0), (2, 2, 2))
    assert world.count_blocks('minecraft:sandstone', (0, 100, 0, 1, 101, 1)) == 8


def test_cache_and_region_management(world):
    world.get_block(0, 62, 0)
    assert world.get_memory_usage()['loaded_regions'] >= 1
    assert world.get_cache_stats() is not None
    assert (0, 0) in world.get_loaded_regions()
    world.invalidate_chunk(0, 0)
    world.invalidate_region(0, 0)
    assert world.unload_region(0, 0, save=False) in (True, False)
    assert world.unload_all_regions(save=False) >= 0
    world.clear_cache()


def test_switch_dimension(world):
    world.switch_dimension('nether', save_current=False)
    assert world.get_dimension() == 'nether'
    with pytest.raises(ValueError):
        world.switch_dimension('moon')


def test_world_rejects_unknown_dimension(world_dir):
    with pytest.raises(ValueError):
        World(str(world_dir), dimension='moon')
