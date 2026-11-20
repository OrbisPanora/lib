"""Helpers in `orbispanora_lib.anvil.utilities`."""
import pytest
from nbt import nbt

from orbispanora_lib.anvil import Block
from orbispanora_lib.anvil import utilities as util
from orbispanora_lib.anvil.versions import VERSION_17w47a


def test_bin_append_joins_bit_fields():
    assert util.bin_append(0b101, 0b11, length=2) == 0b10111
    assert util.bin_append(1, 0) == 0b1


def test_nibble_reads_half_bytes():
    data = [0x21, 0x43]
    assert [util.nibble(data, i) for i in range(4)] == [1, 2, 3, 4]


def test_calculate_states_count_has_whole_blocks_per_long():
    assert util.calculate_states_count(4) == 256
    assert util.calculate_states_count(5) == 342
    assert util.calculate_states_count(6) == 410


def test_calculate_blockstates_size_is_padded():
    assert util.calculate_blockstates_size(4) >= 256


def test_section_height_range_depends_on_version():
    assert util.section_height_range(VERSION_17w47a + 1) == range(-4, 20)
    assert util.section_height_range(VERSION_17w47a) == range(16)
    assert util.section_height_range(None) == range(16)


@pytest.mark.parametrize('bits', [4, 5, 6, 9, 12])
def test_read_packed_index_modern_layout(bits):
    per_long = 64 // bits
    values = [(i * 7) % (1 << bits) for i in range(4096)]
    states = [0] * util.calculate_states_count(bits)
    for i, value in enumerate(values):
        states[i // per_long] |= value << ((i % per_long) * bits)
    assert [util.read_packed_index(states, i, bits) for i in range(4096)] == values


@pytest.mark.parametrize('bits', [4, 5, 7])
def test_read_packed_index_stretched_layout(bits):
    values = [(i * 5) % (1 << bits) for i in range(4096)]
    states = [0] * ((4096 * bits + 63) // 64 + 1)
    for i, value in enumerate(values):
        start = i * bits
        long_index, offset = divmod(start, 64)
        states[long_index] |= (value << offset) & ((1 << 64) - 1)
        if offset + bits > 64:
            states[long_index + 1] |= value >> (64 - offset)
    assert [util.read_packed_index(states, i, bits, stretches=True) for i in range(4096)] == values


def make_palette(*names):
    palette = nbt.TAG_List(name='palette', type=nbt.TAG_Compound)
    for name in names:
        entry = nbt.TAG_Compound()
        entry.tags.append(nbt.TAG_String(name='Name', value=name))
        palette.tags.append(entry)
    return palette


def test_get_air_block_index_finds_air_or_falls_back():
    assert util.get_air_block_index(make_palette('minecraft:stone', 'minecraft:air')) == 1
    assert util.get_air_block_index(make_palette('minecraft:stone')) == 0


def test_is_block_in_palette():
    # Palette entries read from a chunk keep their properties as NBT tags; the block searched for
    # has plain strings.
    stairs = Block('minecraft', 'oak_stairs', {'facing': nbt.TAG_String(value='north')})
    blocks = [Block('minecraft', 'stone'), stairs]
    assert util.is_block_in_palette(blocks, Block('minecraft', 'stone'))
    assert util.is_block_in_palette(blocks, Block('minecraft', 'oak_stairs', {'facing': 'north'}))
    assert not util.is_block_in_palette(blocks, Block('minecraft', 'oak_stairs', {'facing': 'south'}))
    assert not util.is_block_in_palette(blocks, Block('minecraft', 'dirt'))


def test_props_match():
    props = nbt.TAG_Compound()
    props.tags.append(nbt.TAG_String(name='facing', value='north'))
    assert util.props_match(props, {'facing': 'north'})
    assert not util.props_match(props, {'facing': 'south'})
    assert util.props_match(None, {})
    assert not util.props_match(None, {'facing': 'north'})


def test_resize_biome_data_array_keeps_values():
    old_bits, new_bits = 1, 2
    values = [i % 2 for i in range(64)]
    packed = 0
    for i, value in enumerate(values):
        packed |= value << (i * old_bits)
    resized = util.resize_biome_data_array([packed], old_bits, new_bits)
    assert len(resized) >= 1
    out = [(resized[(i * new_bits) // 64] >> ((i * new_bits) % 64)) & 3 for i in range(64)]
    assert out == values
