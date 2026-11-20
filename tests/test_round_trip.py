"""Regions written with EmptyRegion are read back by Region and World."""
import pytest

from orbispanora_lib.anvil import Biome, Block, EmptyRegion, Region, World
from orbispanora_lib.anvil.empty_section import EmptySection
from orbispanora_lib.anvil.utilities import pack_indices, read_packed_index

# Names of block types, in numbers that need 4, 5, 6 and 7 bits per block in a section.
BLOCK_NAMES = [f'block_{i}' for i in range(70)]
BIOME_NAMES = ['plains', 'desert', 'forest', 'taiga', 'swamp', 'jungle', 'savanna', 'badlands']


def name_of(block) -> str:
    """The name of a block that has to exist."""
    assert block is not None
    return block.name()


def saved_chunk(region: EmptyRegion, x: int, z: int):
    """Save the region and read the chunk back with Region."""
    return Region(region.save()).get_chunk(x, z)


@pytest.mark.parametrize('bits, wanted', [(1, 2), (2, 4), (3, 8), (5, 32), (6, 64), (7, 100)])
def test_pack_indices_round_trip(bits, wanted):
    indices = [i % wanted for i in range(4096)]
    longs = pack_indices(indices, bits)
    assert len(longs) == -(-4096 // (64 // bits))
    assert all(0 <= value < 2 ** 64 for value in longs)
    assert [read_packed_index(longs, i, bits) for i in range(4096)] == indices


def test_a_block_never_spans_two_longs():
    # 5 bits: 12 blocks per long, 4 bits unused.
    longs = pack_indices([31] * 24, 5)
    assert longs == [sum(31 << (5 * slot) for slot in range(12))] * 2


def test_section_palette_keeps_the_order_of_first_appearance():
    section = EmptySection(0)
    section.set_block(Block('minecraft', 'stone'), 1, 0, 0)
    section.set_block(Block('minecraft', 'dirt'), 2, 0, 0)
    assert [block.name() for block in section.palette()] == ['minecraft:air', 'minecraft:stone', 'minecraft:dirt']


@pytest.mark.parametrize('kinds', [1, 2, 3, 16, 17, 33, 65])
def test_blocks_survive_the_round_trip(kinds):
    region = EmptyRegion(0, 0)
    expected = {}
    for i in range(kinds):
        block = Block('minecraft', BLOCK_NAMES[i])
        position = (i % 16, 64 + (i // 16) % 16, (i // 7) % 16)
        region.set_block(block, *position)
        expected[position] = block.name()
    chunk = saved_chunk(region, 0, 0)
    for position, name in expected.items():
        assert chunk.get_block(*position, force_new=True).name() == name
    assert chunk.get_block(15, 70, 15, force_new=True).name() in ('minecraft:air', *expected.values())


def test_a_section_with_one_block_type_has_no_data_array():
    region = EmptyRegion(0, 0)
    for x in range(16):
        for y in range(16):
            for z in range(16):
                region.set_block(Block('minecraft', 'stone'), x, 32 + y, z)
    chunk = saved_chunk(region, 0, 0)
    section = chunk.get_section(2)
    assert 'data' not in section['block_states']
    assert chunk.get_block(5, 40, 5, force_new=True).name() == 'minecraft:stone'


def test_block_properties_survive():
    region = EmptyRegion(0, 0)
    region.set_block(Block('minecraft', 'oak_stairs', {'facing': 'north', 'waterlogged': False, 'level': 3}), 3, 64, 3)
    block = saved_chunk(region, 0, 0).get_block(3, 64, 3)
    assert block.name() == 'minecraft:oak_stairs'
    assert str(block.properties['facing']) == 'north'
    assert str(block.properties['waterlogged']) == 'false'
    assert str(block.properties['level']) == '3'


def test_chunk_at_another_position_keeps_its_coordinates():
    region = EmptyRegion(0, 0)
    region.set_block(Block('minecraft', 'stone'), 16 * 3 + 1, 64, 16 * 5 + 2)
    chunk = saved_chunk(region, 3, 5)
    assert (chunk.x, chunk.z) == (3, 5)
    assert chunk.get_block(1, 64, 2, force_new=True).name() == 'minecraft:stone'


@pytest.mark.parametrize('count', [1, 2, 4, 5, 8])
def test_biomes_survive_the_round_trip(count):
    region = EmptyRegion(0, 0)
    region.set_block(Block('minecraft', 'stone'), 0, 64, 0)
    chunk = region.get_chunk(0, 0)
    assert chunk is not None
    # One biome per 4x4 column cell, so every cell gets one of `count` biomes.
    expected = {}
    for cell in range(16):
        name = BIOME_NAMES[cell % count]
        cell_x, cell_z = cell % 4, cell // 4
        for x in range(cell_x * 4, cell_x * 4 + 4):
            for z in range(cell_z * 4, cell_z * 4 + 4):
                chunk.set_biome(Biome('minecraft', name), x, z)
        expected[(cell_x * 4, cell_z * 4)] = f'minecraft:{name}'
    read = saved_chunk(region, 0, 0)
    for (x, z), name in expected.items():
        assert read.get_biome(x, 64, z).name() == name
        assert read.get_biome(x + 3, 70, z + 3).name() == name


def test_world_reloads_what_it_saved(tmp_path):
    folder = tmp_path / 'world'
    (folder / 'region').mkdir(parents=True)
    world = World(str(folder))
    world.set_block(Block('minecraft', 'stone'), 5, 64, 5)
    world.set_block(Block('minecraft', 'dirt'), 6, 64, 5)
    world.save()
    reloaded = World(str(folder))
    assert name_of(reloaded.get_block(5, 64, 5)) == 'minecraft:stone'
    assert name_of(reloaded.get_block(6, 64, 5)) == 'minecraft:dirt'
    assert name_of(reloaded.get_block(7, 64, 5)) == 'minecraft:air'


def test_stream_blocks_of_a_section_without_data_gives_its_block():
    region = EmptyRegion(0, 0)
    for x in range(16):
        for y in range(16):
            for z in range(16):
                region.set_block(Block('minecraft', 'stone'), x, 32 + y, z)
    chunk = saved_chunk(region, 0, 0)
    blocks = list(chunk.stream_blocks(section=2))
    assert len(blocks) == 4096
    assert all(block.name() == 'minecraft:stone' for block in blocks)


def test_changes_to_more_chunks_than_the_cache_holds_are_saved(tmp_path):
    region = EmptyRegion(0, 0)
    for chunk_x in range(6):
        region.set_block(Block('minecraft', 'stone'), chunk_x * 16, 64, 0)
    path = tmp_path / 'r.0.0.mca'
    region.save(str(path))

    loaded = Region(path.read_bytes(), cache_size=2, file_path=str(path))
    for chunk_x in range(6):
        loaded.get_chunk(chunk_x, 0).set_block(Block('minecraft', 'dirt'), 0, 64, 0)
    assert loaded.save() == 6

    reread = Region(path.read_bytes())
    for chunk_x in range(6):
        assert reread.get_chunk(chunk_x, 0).get_block(0, 64, 0, force_new=True).name() == 'minecraft:dirt'


def test_a_saved_region_has_no_modified_chunks_left(tmp_path):
    region = EmptyRegion(0, 0)
    region.set_block(Block('minecraft', 'stone'), 0, 64, 0)
    path = tmp_path / 'r.0.0.mca'
    region.save(str(path))
    loaded = Region(path.read_bytes(), file_path=str(path))
    chunk = loaded.get_chunk(0, 0)
    chunk.set_block(Block('minecraft', 'dirt'), 0, 64, 0)
    assert chunk.modified
    loaded.save()
    assert not chunk.modified


def test_unbounded_replace_reaches_every_region_file_and_is_saved(tmp_path):
    folder = tmp_path / 'world'
    (folder / 'region').mkdir(parents=True)
    for region_x in (0, 1):
        region = EmptyRegion(region_x, 0)
        region.set_block(Block('minecraft', 'stone'), region_x * 512 + 3, 64, 3)
        region.save(str(folder / 'region' / f'r.{region_x}.0.mca'))

    world = World(str(folder))
    assert world.replace_blocks('minecraft:stone', 'minecraft:dirt') == 2
    world.save()

    reloaded = World(str(folder))
    assert name_of(reloaded.get_block(3, 64, 3)) == 'minecraft:dirt'
    assert name_of(reloaded.get_block(515, 64, 3)) == 'minecraft:dirt'


def test_replace_blocks_in_a_section_without_a_data_array(tmp_path):
    region = EmptyRegion(0, 0)
    for x in range(16):
        for y in range(16):
            for z in range(16):
                region.set_block(Block('minecraft', 'stone'), x, 32 + y, z)
    path = tmp_path / 'r.0.0.mca'
    region.save(str(path))
    chunk = Region(path.read_bytes()).get_chunk(0, 0)
    assert chunk.replace_blocks('minecraft:stone', 'minecraft:dirt') == 4096
    assert chunk.get_block(7, 40, 7, force_new=True).name() == 'minecraft:dirt'


def test_chunk_replace_blocks_stays_inside_the_bounds():
    region = EmptyRegion(0, 0)
    for x in range(4):
        region.set_block(Block('minecraft', 'stone'), x, 64, 0)
    chunk = Region(region.save()).get_chunk(0, 0)
    assert chunk.replace_blocks('minecraft:stone', 'minecraft:dirt', (1, 64, 0, 2, 64, 0)) == 2
    assert [chunk.get_block(x, 64, 0, force_new=True).name() for x in range(4)] == [
        'minecraft:stone', 'minecraft:dirt', 'minecraft:dirt', 'minecraft:stone']


def test_replace_blocks_with_properties_only_changes_matching_blocks():
    region = EmptyRegion(0, 0)
    region.set_block(Block('minecraft', 'oak_stairs', {'facing': 'north'}), 0, 64, 0)
    region.set_block(Block('minecraft', 'oak_stairs', {'facing': 'south'}), 1, 64, 0)
    chunk = Region(region.save()).get_chunk(0, 0)
    old = chunk.get_block(0, 64, 0, force_new=True)
    assert chunk.replace_blocks(old, 'minecraft:stone') == 1
    assert chunk.get_block(0, 64, 0, force_new=True).name() == 'minecraft:stone'
    assert chunk.get_block(1, 64, 0, force_new=True).name() == 'minecraft:oak_stairs'


def test_surface_height_skips_air_sections():
    region = EmptyRegion(0, 0)
    region.set_block(Block('minecraft', 'stone'), 2, 100, 3)
    chunk = Region(region.save()).get_chunk(0, 0)
    assert chunk.get_surface_height(2, 3) == 100
    assert chunk.get_surface_height(0, 0) == -64
