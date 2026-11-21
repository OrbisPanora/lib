"""Regions that read their file when asked, and a World that keeps a bounded number of them."""
import shutil
import tracemalloc

import pytest

from orbispanora_lib.anvil import Block, Region, World
from orbispanora_lib.anvil.region import FileBytes

from conftest import REGION_FIXTURE

CONTENT = REGION_FIXTURE.read_bytes()


def loaded_region(world: World, coords) -> Region:
    """A region of the world that is loaded from a file."""
    region = world.regions[coords]
    assert isinstance(region, Region)
    return region


def chunk_cache_of(world: World):
    """The chunk cache of a world that has one."""
    cache = world._chunk_cache  # pylint: disable=protected-access
    assert cache is not None
    return cache


def stored_chunks(region):
    """Coordinates of the chunks a region file holds."""
    return [(x, z) for z in range(32) for x in range(32) if region.chunk_location(x, z) != (0, 0)]


@pytest.fixture
def many_regions(tmp_path):
    """A world folder with the test region file copied under five region coordinates."""
    folder = tmp_path / 'world' / 'region'
    folder.mkdir(parents=True)
    for region_x in range(5):
        shutil.copy(REGION_FIXTURE, folder / f'r.{region_x}.0.mca')
    return tmp_path / 'world'


class TestFileBytes:

    def test_gives_what_the_bytes_of_the_file_give(self):
        view = FileBytes(str(REGION_FIXTURE))
        assert len(view) == len(CONTENT)
        assert view[0] == CONTENT[0] and view[5000] == CONTENT[5000] and view[-1] == CONTENT[-1]
        assert view[3:9] == CONTENT[3:9]
        assert view[8000:9000] == CONTENT[8000:9000]      # across the end of the header
        assert view[10_000:20_000] == CONTENT[10_000:20_000]
        assert view[len(CONTENT) - 3:len(CONTENT) + 100] == CONTENT[-3:]
        assert view[len(CONTENT):] == b''

    def test_refuses_what_bytes_would_refuse(self):
        view = FileBytes(str(REGION_FIXTURE))
        with pytest.raises(IndexError):
            view[len(CONTENT)]
        with pytest.raises(ValueError):
            view[0:10:2]

    def test_is_usable_after_close_and_read_all_gives_the_file(self):
        view = FileBytes(str(REGION_FIXTURE))
        view.close()
        assert view[100] == CONTENT[100]
        assert view.read_all() == CONTENT
        assert view[100] == CONTENT[100]

    def test_an_empty_file(self, tmp_path):
        empty = tmp_path / 'r.0.0.mca'
        empty.write_bytes(b'')
        view = FileBytes(str(empty))
        assert len(view) == 0 and view[0:10] == b''
        with pytest.raises(IndexError):
            view[0]


class TestLazyRegion:

    def test_every_chunk_equals_the_eager_one(self):
        eager = Region.from_file(str(REGION_FIXTURE), cache_size=None)
        lazy = Region.from_file(str(REGION_FIXTURE), cache_size=None, lazy=True)
        assert isinstance(lazy.data, FileBytes) and isinstance(eager.data, bytes)
        chunks = stored_chunks(eager)
        assert chunks and stored_chunks(lazy) == chunks
        for x, z in chunks:
            assert lazy.chunk_location(x, z) == eager.chunk_location(x, z)
            assert lazy.chunk_data(x, z).write_file is not None
            assert lazy.get_chunk(x, z).block_array().names == eager.get_chunk(x, z).block_array().names

    def test_does_not_hold_the_file_in_memory(self):
        tracemalloc.start()
        try:
            region = Region.from_file(str(REGION_FIXTURE), cache_size=None, lazy=True)
            region.chunk_location(0, 0)
            held, _ = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert held < len(CONTENT) // 20

    def test_can_be_closed_and_read_again(self):
        region = Region.from_file(str(REGION_FIXTURE), cache_size=None, lazy=True)
        before = region.get_chunk(0, 0).x
        region.close()
        assert region.get_chunk(0, 0).x == before

    def test_close_does_not_touch_a_region_that_holds_its_bytes(self):
        region = Region.from_file(str(REGION_FIXTURE), cache_size=None)
        region.close()
        assert region.data == CONTENT

    def test_a_change_is_saved_and_read_back(self, tmp_path):
        target = tmp_path / 'r.0.0.mca'
        shutil.copy(REGION_FIXTURE, target)
        region = Region.from_file(str(target), cache_size=None, lazy=True)
        region.set_block(Block('minecraft', 'diamond_block'), 3, 64, 3, str(target))
        assert isinstance(region.data, bytes)
        again = Region.from_file(str(target), lazy=True)
        assert again.get_chunk(0, 0).get_block(3, 64, 3, force_new=True).name() == 'minecraft:diamond_block'

    def test_an_empty_file_has_no_chunks(self, tmp_path):
        empty = tmp_path / 'r.0.0.mca'
        empty.write_bytes(b'')
        region = Region.from_file(str(empty), lazy=True)
        with pytest.raises(Exception):
            region.get_chunk(0, 0)


class TestWorldKeepsFewRegions:

    def test_only_the_recent_regions_stay_open(self, many_regions):
        world = World(str(many_regions), region_cache_size=2)
        for region_x in range(5):
            assert world.get_chunk(region_x * 32, 0) is not None
        assert sorted(world.regions) == [(3, 0), (4, 0)]

    def test_a_dropped_region_is_read_again(self, many_regions):
        world = World(str(many_regions), region_cache_size=2)
        for region_x in range(5):
            world.get_chunk(region_x * 32, 0)
        chunk_cache_of(world).clear()
        assert world.get_chunk(0, 0) is not None
        assert (0, 0) in world.regions

    def test_a_region_with_a_change_is_kept_until_it_is_saved(self, many_regions):
        world = World(str(many_regions), region_cache_size=2)
        chunk = world.get_chunk(32, 0)
        assert chunk is not None
        chunk.set_block(Block('minecraft', 'diamond_block'), 3, 64, 3)
        for region_x in (0, 2, 3, 4):
            world.get_chunk(region_x * 32, 0)
        assert (1, 0) in world.regions
        world.save()
        chunk_cache_of(world).clear()
        for region_x in (0, 2, 3):
            world.get_chunk(region_x * 32, 0)
        assert (1, 0) not in world.regions
        again = World(str(many_regions))
        block = again.get_block(32 * 16 + 3, 64, 3)
        assert block is not None and block.name() == 'minecraft:diamond_block'  # ty: ignore[missing-union-attribute]

    def test_without_a_limit_every_region_stays(self, many_regions):
        for size in (0, None):
            world = World(str(many_regions), region_cache_size=size)
            for region_x in range(5):
                world.get_chunk(region_x * 32, 0)
            assert len(world.regions) == 5

    def test_empty_placeholders_do_not_pile_up(self, many_regions):
        world = World(str(many_regions), region_cache_size=2)
        for region_x in range(10, 40):
            assert world.get_chunk(region_x * 32, 0) is None
        assert len(world.regions) <= 2

    def test_a_new_region_with_blocks_is_kept(self, many_regions):
        world = World(str(many_regions), region_cache_size=2)
        world.set_block(Block('minecraft', 'stone'), 20 * 512 + 1, 64, 1)
        for region_x in range(5):
            world.get_chunk(region_x * 32, 0)
        assert (20, 0) in world.regions

    def test_the_whole_file_is_read_when_regions_are_not_lazy(self, many_regions):
        world = World(str(many_regions), lazy_regions=False)
        world.get_chunk(0, 0)
        assert isinstance(loaded_region(world, (0, 0)).data, bytes)
        lazy = World(str(many_regions))
        lazy.get_chunk(0, 0)
        assert isinstance(loaded_region(lazy, (0, 0)).data, FileBytes)

    def test_close_releases_everything_and_the_world_still_works(self, many_regions):
        world = World(str(many_regions))
        world.get_chunk(0, 0)
        world.close()
        assert not world.regions
        assert world.get_chunk(0, 0) is not None

    def test_unload_region_closes_it(self, many_regions):
        world = World(str(many_regions))
        world.get_chunk(0, 0)
        region = loaded_region(world, (0, 0))
        assert world.unload_region(0, 0, save=False)
        view = region._data  # pylint: disable=protected-access
        assert isinstance(view, FileBytes) and view._fd is None  # pylint: disable=protected-access

    def test_the_default_chunk_cache_is_smaller_than_before(self, many_regions):
        assert chunk_cache_of(World(str(many_regions))).max_size == 128
        assert chunk_cache_of(World(str(many_regions), chunk_cache_size=7)).max_size == 7
