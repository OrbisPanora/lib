"""Building regions, chunks and sections from scratch."""
import io
import zlib

import pytest
from nbt import nbt

from orbispanora_lib.anvil import (Biome, Block, EmptyChunk, EmptyRegion, EmptySection, RawSection, World)
from orbispanora_lib.anvil.errors import EmptySectionAlreadyExists, OutOfBoundsCoordinates


def name_of(block):
    """Name of a block that must exist."""
    assert block is not None
    return block.name()


def chunk_of(region, x, z):
    """Chunk of a region that must exist."""
    chunk = region.get_chunk(x, z)
    assert chunk is not None
    return chunk


def read_first_chunk(region_bytes):
    """Decode the first stored chunk of a saved region."""
    offset = int.from_bytes(region_bytes[0:3], 'big') * 4096
    length = int.from_bytes(region_bytes[offset:offset + 4], 'big')
    return nbt.NBTFile(buffer=io.BytesIO(zlib.decompress(region_bytes[offset + 5:offset + 4 + length])))


class TestEmptySection:

    def test_blocks_default_to_air(self):
        section = EmptySection(0)
        assert section.get_block(0, 0, 0).name() == 'minecraft:air'

    def test_set_and_get_block(self):
        section = EmptySection(0)
        section.set_block(Block('minecraft', 'stone'), 1, 2, 3)
        assert section.get_block(1, 2, 3).name() == 'minecraft:stone'

    def test_palette_and_blockstates(self):
        section = EmptySection(0)
        section.set_block(Block('minecraft', 'stone'), 1, 1, 1)
        assert {block.name() for block in section.palette()} == {'minecraft:air', 'minecraft:stone'}
        assert len(section.blockstates()) == 256

    def test_to_dict(self):
        section = EmptySection(2)
        section.set_block(Block('minecraft', 'stone'), 1, 1, 1)
        info = section.to_dict()
        assert info['y'] == 2 and info['block_count'] == 1
        assert 'minecraft:stone' in info['palette']

    def test_save_has_block_states(self):
        section = EmptySection(0)
        section.set_block(Block('minecraft', 'stone'), 1, 1, 1)
        assert section.save()['Y'].value == 0

    @pytest.mark.parametrize('position', [(16, 0, 0), (0, -1, 0), (0, 0, 16)])
    def test_out_of_bounds(self, position):
        section = EmptySection(0)
        with pytest.raises(OutOfBoundsCoordinates):
            section.set_block(Block('minecraft', 'stone'), *position)
        with pytest.raises(OutOfBoundsCoordinates):
            section.get_block(*position)

    def test_inside(self):
        assert EmptySection.inside(0, 0, 0)
        assert not EmptySection.inside(16, 0, 0)


class TestRawSection:

    def test_palette_and_blockstates(self):
        palette = [Block('minecraft', 'air'), Block('minecraft', 'stone')]
        section = RawSection(0, [i % 2 for i in range(4096)], palette)
        assert section.palette() == palette
        assert len(section.blockstates()) == 256
        assert section.save()['Y'].value == 0


class TestEmptyChunk:

    def test_set_and_get_block(self):
        chunk = EmptyChunk(0, 0)
        assert chunk.get_block(1, 1, 1) is None
        chunk.set_block(Block('minecraft', 'stone'), 1, 1, 1)
        assert name_of(chunk.get_block(1, 1, 1)) == 'minecraft:stone'

    def test_replace_block_at_and_replace_blocks(self):
        chunk = EmptyChunk(0, 0)
        chunk.set_block(Block('minecraft', 'stone'), 1, 1, 1)
        chunk.set_block(Block('minecraft', 'stone'), 2, 1, 1)
        assert chunk.replace_block_at(1, 1, 1, 'minecraft:dirt') is True
        assert chunk.replace_blocks('minecraft:stone', 'minecraft:sand') == 1
        assert name_of(chunk.get_block(2, 1, 1)) == 'minecraft:sand'

    def test_add_section_twice(self):
        chunk = EmptyChunk(0, 0)
        chunk.add_section(EmptySection(0))
        with pytest.raises(EmptySectionAlreadyExists):
            chunk.add_section(EmptySection(0), replace=False)
        chunk.add_section(EmptySection(0), replace=True)

    def test_get_block_on_raw_section_is_refused(self):
        chunk = EmptyChunk(0, 0)
        chunk.add_section(RawSection(0, [0] * 4096, [Block('minecraft', 'air')]))
        with pytest.raises(TypeError):
            chunk.get_block(0, 0, 0)
        with pytest.raises(TypeError):
            chunk.set_block(Block('minecraft', 'stone'), 0, 0, 0)

    def test_set_biome_and_save(self):
        chunk = EmptyChunk(0, 0)
        chunk.set_block(Block('minecraft', 'stone'), 1, 1, 1)
        chunk.set_biome(Biome('minecraft', 'plains'), 1, 1)
        saved = chunk.save()
        assert saved['DataVersion'].value == chunk.version
        assert saved['xPos'].value == 0
        assert saved['Status'].value == 'minecraft:full'
        assert 'Level' not in [tag.name for tag in saved.tags]

    @pytest.mark.parametrize('position', [(16, 0, 0), (0, 0, -1), (0, 100000, 0)])
    def test_out_of_bounds(self, position):
        with pytest.raises(OutOfBoundsCoordinates):
            EmptyChunk(0, 0).set_block(Block('minecraft', 'stone'), *position)


class TestEmptyRegion:

    def test_set_block_creates_the_chunk(self):
        region = EmptyRegion(0, 0)
        region.set_block(Block('minecraft', 'stone'), 1, 64, 1)
        assert name_of(chunk_of(region, 0, 0).get_block(1, 64, 1)) == 'minecraft:stone'
        assert region.get_chunk(5, 5) is None

    def test_inside(self):
        region = EmptyRegion(0, 0)
        assert region.inside(1, 64, 1)
        assert not region.inside(600, 64, 1)
        assert region.inside(31, 0, 31, chunk=True)
        assert not region.inside(32, 0, 0, chunk=True)

    def test_fill_and_fill_biome(self):
        region = EmptyRegion(0, 0)
        region.fill(Block('minecraft', 'dirt'), 0, 60, 0, 17, 62, 3)
        assert name_of(chunk_of(region, 1, 0).get_block(1, 61, 1)) == 'minecraft:dirt'
        region.fill_biome(Biome('minecraft', 'desert'), 0, 0, 3, 3)

    def test_fill_outside_the_region(self):
        region = EmptyRegion(0, 0)
        with pytest.raises(OutOfBoundsCoordinates):
            region.fill(Block('minecraft', 'dirt'), 0, 60, 0, 600, 62, 3)
        region.fill(Block('minecraft', 'dirt'), 0, 60, 0, 600, 62, 3, ignore_outside=True)

    def test_set_if_inside_ignores_other_regions(self):
        region = EmptyRegion(0, 0)
        region.set_if_inside(Block('minecraft', 'stone'), 900, 64, 900)
        region.set_biome_if_inside(Biome('minecraft', 'plains'), 900, 900)
        assert all(chunk is None for chunk in region.chunks)

    def test_set_block_outside_is_an_error(self):
        with pytest.raises(OutOfBoundsCoordinates):
            EmptyRegion(0, 0).set_block(Block('minecraft', 'stone'), 900, 64, 900)

    def test_add_chunk_and_section(self):
        region = EmptyRegion(0, 0)
        region.add_chunk(EmptyChunk(2, 3))
        region.add_section(EmptySection(1), 2, 3)
        assert chunk_of(region, 2, 3).sections[1] is not None
        with pytest.raises(OutOfBoundsCoordinates):
            region.add_chunk(EmptyChunk(40, 0))

    def test_save_to_bytes_path_and_file_object(self, tmp_path):
        region = EmptyRegion(0, 0)
        region.set_block(Block('minecraft', 'stone'), 1, 64, 1)
        data = region.save()
        assert len(data) % 4096 == 0
        path = tmp_path / 'r.0.0.mca'
        region.save(str(path))
        assert path.read_bytes() == data
        buffer = io.BytesIO()
        region.save(buffer)
        assert buffer.getvalue() == data

    def test_saved_chunk_is_zlib_nbt_with_a_block_section(self):
        region = EmptyRegion(0, 0)
        region.set_block(Block('minecraft', 'stone'), 1, 64, 1)
        chunk = read_first_chunk(region.save())
        assert chunk['xPos'].value == 0
        section = next(section for section in chunk['sections'] if section['Y'].value == 4)
        assert 'palette' in section['block_states']
        assert 'palette' in section['biomes']


class TestWorldOnGeneratedRegion:

    @pytest.fixture
    def world(self, tmp_path):
        folder = tmp_path / 'world'
        (folder / 'region').mkdir(parents=True)
        return World(str(folder))

    def test_set_block_in_a_new_world(self, world):
        world.set_block(Block('minecraft', 'stone'), 5, 64, 5)
        assert world.get_block(5, 64, 5).name() == 'minecraft:stone'

    def test_unbounded_replace_blocks_and_count(self, world):
        for x in range(4):
            world.set_block(Block('minecraft', 'stone'), x, 64, 0)
        assert world.replace_blocks('minecraft:stone', 'minecraft:dirt') == 4
        # Without bounds, count_blocks scans the region files on disk, so the region is saved first.
        world.save()
        assert world.count_blocks('minecraft:dirt') == 4

    def test_get_block_distribution_and_info(self, world):
        world.set_block(Block('minecraft', 'stone'), 0, 64, 0)
        world.set_block(Block('minecraft', 'stone'), 1, 64, 0)
        world.set_block(Block('minecraft', 'dirt'), 2, 64, 0)
        distribution = world.get_block_distribution((0, 64, 0, 2, 64, 0))
        assert distribution == {'minecraft:stone': 2, 'minecraft:dirt': 1}
        assert world.get_world_info()['size_x'] >= 512

    def test_set_biome_and_chunk_data_on_generated_chunk(self, world):
        world.set_block(Block('minecraft', 'stone'), 5, 64, 5)
        assert world.get_chunk_data(0, 0, 'heightmap') is None
        with pytest.raises(TypeError):
            world.set_chunk_biome(Biome('minecraft', 'plains'), 0, 0)
        assert world.replace_block_at(5, 64, 5, 'minecraft:dirt') is False
