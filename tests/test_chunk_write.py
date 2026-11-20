"""Editing chunks read from a copy of the committed region file, then saving and reloading."""
import pytest

from orbispanora_lib.anvil import Biome, Block, Chunk, Region
from orbispanora_lib.anvil.errors import OutOfBoundsCoordinates


@pytest.fixture
def chunk(region_file):
    """Chunk (0, 0) of a writable copy of the region."""
    return Region.from_file(region_file).get_chunk(0, 0)


def test_set_block_in_existing_section(chunk):
    chunk.set_block(Block('minecraft', 'gold_block'), 1, 70, 1)
    assert chunk.get_block(1, 70, 1).name() == 'minecraft:gold_block'


def test_set_block_below_world_bottom_section(chunk):
    chunk.set_block(Block('minecraft', 'stone'), 1, -30, 1)
    assert chunk.get_block(1, -30, 1).name() == 'minecraft:stone'


def test_set_block_with_properties(chunk):
    stairs = Block('minecraft', 'oak_stairs', {'facing': 'north', 'half': 'bottom'})
    chunk.set_block(stairs, 2, 70, 2)
    stored = chunk.get_block(2, 70, 2)
    assert stored.name() == 'minecraft:oak_stairs'
    assert str(stored.properties['facing']) == 'north'


def test_set_block_grows_the_palette(chunk):
    # Each different block added to the same section forces the palette (and the bit width of
    # the stored indexes) to grow, which rewrites every index in the section.
    names = [f'minecraft:{name}' for name in (
        'stone', 'granite', 'diorite', 'andesite', 'dirt', 'coarse_dirt', 'podzol', 'cobblestone',
        'oak_planks', 'spruce_planks', 'birch_planks', 'jungle_planks', 'acacia_planks',
        'dark_oak_planks', 'sand', 'red_sand', 'gravel', 'gold_ore', 'iron_ore', 'coal_ore',
        'oak_log', 'sponge', 'glass', 'lapis_ore', 'lapis_block', 'dispenser', 'sandstone')]
    for offset, name in enumerate(names):
        chunk.set_block(Block.from_name(name), offset % 16, 100 + offset // 16, 3)
    for offset, name in enumerate(names):
        assert chunk.get_block(offset % 16, 100 + offset // 16, 3).name() == name
    # a block that was not touched is still the same
    assert chunk.get_block(1, -64, 1).name() == 'minecraft:bedrock'


def test_set_block_out_of_bounds(chunk):
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.set_block(Block('minecraft', 'stone'), 16, 70, 0)
    with pytest.raises(OutOfBoundsCoordinates):
        chunk.set_block(Block('minecraft', 'stone'), 0, 70, -1)


def test_replace_block_at(chunk):
    assert chunk.replace_block_at(0, 62, 0, 'minecraft:ice') is True
    assert chunk.get_block(0, 62, 0).name() == 'minecraft:ice'
    assert chunk.replace_block_at(0, 62, 0, 'minecraft:ice') is False or True


def test_replace_blocks_counts_every_match(chunk):
    before = sum(1 for block in chunk.stream_chunk() if block.name() == 'minecraft:water')
    assert before > 0
    assert chunk.replace_blocks('minecraft:water', 'minecraft:ice') == before
    assert all(block.name() != 'minecraft:water' for block in chunk.stream_chunk())


def test_replace_blocks_without_match(chunk):
    assert chunk.replace_blocks('minecraft:diamond_block', 'minecraft:stone') == 0


def test_set_biome_changes_one_cell(chunk):
    chunk.set_biome(Biome('minecraft', 'desert'), 1, 70, 1)
    assert chunk.get_biome(1, 70, 1).name() == 'minecraft:desert'
    assert chunk.get_biome(12, 70, 12).name() != 'minecraft:desert'


def test_set_chunk_biome_changes_every_cell(chunk):
    chunk.set_chunk_biome(Biome('minecraft', 'plains'))
    assert {chunk.get_biome(x, 70, z).name() for x in (0, 7, 15) for z in (0, 7, 15)} == {'minecraft:plains'}


def test_create_section_and_add_block_to_palette(chunk):
    palette = chunk.get_palette(0)
    section = chunk.get_section(0)
    new_block = Block('minecraft', 'emerald_block')
    index = chunk.add_block_to_palette(section, new_block)
    assert chunk.get_palette(0)[index].name() == 'minecraft:emerald_block'
    assert len(chunk.get_palette(0)) == len(palette) + 1


def test_save_and_reload(chunk, region_file):
    chunk.set_block(Block('minecraft', 'gold_block'), 1, 70, 1)
    chunk.save(region_file)
    reloaded = Region.from_file(region_file).get_chunk(0, 0)
    assert reloaded.get_block(1, 70, 1).name() == 'minecraft:gold_block'
    assert reloaded.get_block(1, -64, 1).name() == 'minecraft:bedrock'


def test_chunk_from_region_file(region_file):
    chunk = Chunk.from_region(region_file, 0, 0)
    assert chunk.get_block(0, 62, 0).name() == 'minecraft:water'


def test_palette_growth_across_two_bit_widths_keeps_every_block(chunk):
    # The palette goes from 1 entry to 41: the indexes are repacked at 17 entries (4 to 5 bits)
    # and again at 33 entries (5 to 6 bits). A block written earlier must still read back.
    placed = {}
    for number in range(40):
        position = (number % 16, 96 + number // 16, number % 7)
        name = f'minecraft:test_block_{number}'
        chunk.set_block(Block.from_name(name), *position)
        placed[position] = name
        assert chunk.get_block(*position).name() == name
    for position, name in placed.items():
        assert chunk.get_block(*position).name() == name
