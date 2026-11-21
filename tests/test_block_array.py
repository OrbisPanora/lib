"""Chunk.block_array decodes a whole chunk at once and must agree with Chunk.get_block."""
import sys

import numpy as np
import pytest
from nbt import nbt

from orbispanora_lib.anvil import Block, Chunk, ChunkBlocks, EmptyRegion, Region
from orbispanora_lib.anvil.utilities import pack_indices

from conftest import REGION_FIXTURE

AIR = 'minecraft:air'


def signed(value: int) -> int:
    """An unsigned 64-bit value as the signed value that NBT stores."""
    return value - 2 ** 64 if value >= 2 ** 63 else value


def pack_stretched(indices, bits):
    """Pack indices the way versions before 20w17a did: a block may span two longs."""
    stream = 0
    for position, index in enumerate(indices):
        stream |= index << (position * bits)
    count = -(-len(indices) * bits // 64)
    return [(stream >> (64 * i)) & (2 ** 64 - 1) for i in range(count)]


def long_array(values) -> nbt.TAG_Long_Array:
    """A long array tag holding unsigned values."""
    tag = nbt.TAG_Long_Array()
    tag.value = [signed(value) for value in values]
    return tag


def palette_tag(names) -> nbt.TAG_List:
    """A palette list with one compound per block name."""
    palette = nbt.TAG_List(type=nbt.TAG_Compound)
    for name in names:
        entry = nbt.TAG_Compound()
        entry['Name'] = nbt.TAG_String(name)
        palette.append(entry)
    return palette


def modern_section(y: int, names, indices=None) -> nbt.TAG_Compound:
    """A 20w17a or later section. Without ``indices`` the section has no data array."""
    section = nbt.TAG_Compound()
    section['Y'] = nbt.TAG_Byte(y)
    states = nbt.TAG_Compound()
    states['palette'] = palette_tag(names)
    if indices is not None:
        bits = max((len(names) - 1).bit_length(), 4)
        states['data'] = long_array(pack_indices(indices, bits))
    section['block_states'] = states
    return section


def modern_chunk(sections, version=3955) -> Chunk:
    """A chunk with the 1.18 layout (flat root) built from section tags."""
    root = nbt.NBTFile()
    root['DataVersion'] = nbt.TAG_Int(version)
    root['xPos'] = nbt.TAG_Int(0)
    root['zPos'] = nbt.TAG_Int(0)
    listing = nbt.TAG_List(type=nbt.TAG_Compound)
    for section in sections:
        listing.append(section)
    root['sections'] = listing
    root['block_entities'] = nbt.TAG_List(type=nbt.TAG_Compound)
    return Chunk(root)


def stretched_chunk(names, indices, version=2500) -> Chunk:
    """A 1.16 chunk (``Level`` compound, ``Palette`` and ``BlockStates``, blocks that span longs)."""
    bits = max((len(names) - 1).bit_length(), 4)
    section = nbt.TAG_Compound()
    section['Y'] = nbt.TAG_Byte(2)
    section['Palette'] = palette_tag(names)
    section['BlockStates'] = long_array(pack_stretched(indices, bits))
    level = nbt.TAG_Compound()
    level['xPos'] = nbt.TAG_Int(0)
    level['zPos'] = nbt.TAG_Int(0)
    level['Sections'] = nbt.TAG_List(type=nbt.TAG_Compound)
    level['Sections'].append(section)
    level['TileEntities'] = nbt.TAG_List(type=nbt.TAG_Compound)
    root = nbt.NBTFile()
    root['DataVersion'] = nbt.TAG_Int(version)
    root['Level'] = level
    return Chunk(root)


def legacy_chunk(blocks: dict) -> Chunk:
    """A chunk from before 1.13 (no data version). ``blocks`` maps (x, y, z) to a numeric block id."""
    section = nbt.TAG_Compound()
    section['Y'] = nbt.TAG_Byte(0)
    ids = bytearray(4096)
    for (x, y, z), block_id in blocks.items():
        ids[y * 256 + z * 16 + x] = block_id
    section['Blocks'] = nbt.TAG_Byte_Array()
    section['Blocks'].value = bytearray(ids)
    section['Data'] = nbt.TAG_Byte_Array()
    section['Data'].value = bytearray(2048)
    level = nbt.TAG_Compound()
    level['xPos'] = nbt.TAG_Int(0)
    level['zPos'] = nbt.TAG_Int(0)
    level['Sections'] = nbt.TAG_List(type=nbt.TAG_Compound)
    level['Sections'].append(section)
    level['TileEntities'] = nbt.TAG_List(type=nbt.TAG_Compound)
    root = nbt.NBTFile()
    root['Level'] = level
    return Chunk(root)


def assert_same_as_get_block(chunk: Chunk, blocks: ChunkBlocks, sections) -> None:
    """Every position of the given sections holds the block that get_block returns."""
    for section_y in sections:
        section = chunk.get_section(section_y)
        for y in range(16):
            for z in range(16):
                for x in range(16):
                    expected = chunk.get_block(x, y, z, section, force_new=True).name()
                    assert blocks.name_at(x, section_y * 16 + y, z) == expected, (x, section_y * 16 + y, z)


@pytest.fixture(scope='module')
def region() -> Region:
    return Region.from_file(str(REGION_FIXTURE))


@pytest.fixture(scope='module')
def stored_chunks(region):
    """Coordinates of the chunks that the region file holds."""
    return [(x, z) for z in range(32) for x in range(32) if region.chunk_location(x, z) != (0, 0)]


class TestTestRegionFile:

    def test_layout(self, region):
        blocks = region.get_chunk(0, 0).block_array()
        assert isinstance(blocks, ChunkBlocks)
        assert blocks.names[0] == AIR
        assert blocks.min_y == -64
        assert blocks.height == 384
        assert blocks.indices.shape == (384, 16, 16)
        assert blocks.indices.dtype == np.uint16
        assert int(blocks.indices.max()) < len(blocks.names)

    def test_same_as_get_block_everywhere_in_three_chunks(self, region, stored_chunks):
        # Chunks that hold terrain, taken from the ones with the most non-air blocks.
        scored = []
        for x, z in stored_chunks:
            blocks = region.get_chunk(x, z).block_array()
            scored.append((int((blocks.indices != 0).sum()), (x, z)))
        for _, (x, z) in sorted(scored)[-3:]:
            chunk = region.get_chunk(x, z)
            blocks = chunk.block_array()
            assert_same_as_get_block(chunk, blocks, range(-4, 20))

    def test_same_as_the_section_indices_in_every_chunk(self, region, stored_chunks):
        for x, z in stored_chunks:
            chunk = region.get_chunk(x, z)
            blocks = chunk.block_array()
            for section_y in range(-4, 20):
                section = chunk.get_section(section_y)
                layer = blocks.indices[(section_y + 4) * 16:(section_y + 5) * 16]
                if section is None:
                    assert not layer.any()
                    continue
                palette = [entry['Name'].value for entry in section['block_states']['palette']]
                expected = [palette[i] for i in chunk._section_indices(section)]  # pylint: disable=protected-access
                actual = [blocks.names[i] for i in layer.ravel()]
                assert actual == expected


class TestBuiltChunks:

    @pytest.mark.parametrize('kinds', [2, 3, 16, 17, 33, 65])
    def test_palette_sizes_that_need_4_to_7_bits(self, kinds):
        region = EmptyRegion(0, 0)
        for i in range(kinds):
            region.set_block(Block('minecraft', f'block_{i}'), i % 16, 64 + (i // 16) % 16, (i // 7) % 16)
        chunk = Region(region.save()).get_chunk(0, 0)
        blocks = chunk.block_array()
        assert_same_as_get_block(chunk, blocks, [4])
        assert len(set(blocks.names) - {AIR}) == kinds

    def test_section_without_data_is_filled_with_its_one_block(self):
        chunk = modern_chunk([modern_section(0, ['minecraft:stone']), modern_section(1, [AIR])])
        blocks = chunk.block_array()
        assert (blocks.indices[64:80] == blocks.names.index('minecraft:stone')).all()
        assert not blocks.indices[80:96].any()

    def test_missing_sections_and_empty_palettes_are_air(self):
        chunk = modern_chunk([modern_section(3, [])])
        blocks = chunk.block_array()
        assert blocks.names == (AIR,)
        assert not blocks.indices.any()

    def test_blocks_with_other_properties_share_an_index(self):
        # Two palette entries with the same name, as for two stair directions.
        indices = [0] * 2048 + [1] * 2048
        chunk = modern_chunk([modern_section(0, ['minecraft:oak_stairs', 'minecraft:oak_stairs'], indices)])
        blocks = chunk.block_array()
        assert blocks.names == (AIR, 'minecraft:oak_stairs')
        assert (blocks.indices[64:80] == 1).all()

    def test_air_is_index_zero_even_when_a_section_lists_it_later(self):
        indices = [0] * 4096
        indices[5] = 1
        chunk = modern_chunk([modern_section(0, ['minecraft:dirt', AIR], indices)])
        blocks = chunk.block_array()
        assert blocks.names == (AIR, 'minecraft:dirt')
        assert blocks.name_at(5, 0, 0) == AIR
        assert blocks.name_at(6, 0, 0) == 'minecraft:dirt'

    def test_longs_that_are_stored_as_negative_numbers(self):
        # Sixteen kinds need 4 bits, so index 15 in the top slot sets the sign bit of the long.
        names = [f'minecraft:block_{i}' for i in range(16)]
        chunk = modern_chunk([modern_section(0, names, [15] * 4096)])
        section = chunk.get_section(0)
        assert section is not None
        assert min(section['block_states']['data'].value) < 0
        blocks = chunk.block_array()
        assert {blocks.names[i] for i in blocks.indices[64:80].ravel()} == {'minecraft:block_15'}

    def test_section_without_a_palette_is_air(self):
        section = nbt.TAG_Compound()
        section['Y'] = nbt.TAG_Byte(0)
        section['block_states'] = nbt.TAG_Compound()
        blocks = modern_chunk([section]).block_array()
        assert blocks.names == (AIR,)
        assert not blocks.indices.any()

    def test_blocks_that_span_two_longs_before_20w17a(self):
        names = [f'minecraft:block_{i}' for i in range(20)]
        indices = [(i * 7) % 20 for i in range(4096)]
        chunk = stretched_chunk(names, indices)
        blocks = chunk.block_array()
        assert blocks.min_y == -64
        assert_same_as_get_block(chunk, blocks, [2])

    def test_world_from_before_1_13(self):
        chunk = legacy_chunk({(1, 2, 3): 1, (15, 15, 15): 1})
        blocks = chunk.block_array()
        assert blocks.min_y == 0
        assert blocks.height == 256
        assert blocks.name_at(1, 2, 3) == 'minecraft:stone'
        assert blocks.name_at(15, 15, 15) == 'minecraft:stone'
        assert blocks.name_at(0, 0, 0) == AIR


def test_clear_error_without_numpy(monkeypatch):
    monkeypatch.setitem(sys.modules, 'numpy', None)
    chunk = modern_chunk([])
    with pytest.raises(ImportError, match=r'orbispanora-lib\[fast\]'):
        chunk.block_array()
