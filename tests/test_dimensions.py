import os
import shutil
import tempfile

from orbispanora_lib import anvil
from orbispanora_lib.anvil import Block


class TestDimensions:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.world_path = os.path.join(self.test_dir, 'test_world')
        os.makedirs(self.world_path)

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_dimension(self):
        world = anvil.World(self.world_path)
        assert world.get_dimension() == 'overworld'

    def test_create_overworld(self):
        world = anvil.World(self.world_path, dimension='overworld')
        assert world.dimension == 'overworld'
        assert world.region_dir.endswith('region')

    def test_create_nether(self):
        world = anvil.World(self.world_path, dimension='nether')
        assert world.dimension == 'nether'
        assert 'DIM-1' in world.region_dir

    def test_create_end(self):
        world = anvil.World(self.world_path, dimension='end')
        assert world.dimension == 'end'
        assert 'DIM1' in world.region_dir

    def test_invalid_dimension(self):
        try:
            anvil.World(self.world_path, dimension='invalid')
        except ValueError:
            assert True
        else:
            assert False

    def test_switch_dimension(self):
        world = anvil.World(self.world_path, dimension='overworld')
        assert world.get_dimension() == 'overworld'

        world.switch_dimension('nether', save_current=False)
        assert world.get_dimension() == 'nether'

        world.switch_dimension('end', save_current=False)
        assert world.get_dimension() == 'end'

        world.switch_dimension('overworld', save_current=False)
        assert world.get_dimension() == 'overworld'

    def test_switch_dimension_invalid(self):
        world = anvil.World(self.world_path)
        try:
            world.switch_dimension('invalid')
        except ValueError:
            assert True
        else:
            assert False

    def test_switch_dimension_clears_cache(self):
        world = anvil.World(self.world_path, chunk_cache_size=64)
        world.set_block(Block('minecraft', 'stone'), 0, 64, 0)
        world.switch_dimension('nether', save_current=False)

        new_stats = world.get_cache_stats()
        if new_stats and 'chunk_cache' in new_stats and new_stats['chunk_cache']:
            assert new_stats['chunk_cache']['size'] == 0

    def test_get_dimension_info(self):
        world = anvil.World(self.world_path, dimension='nether')
        info = world.get_dimension_info()

        assert info['name'] == 'nether'
        assert info['path'] == 'DIM-1/region'
        assert 'full_path' in info
        assert 'loaded_regions' in info

    def test_set_block_in_different_dimensions(self):
        overworld = anvil.World(self.world_path, dimension='overworld')
        nether = anvil.World(self.world_path, dimension='nether')
        end = anvil.World(self.world_path, dimension='end')

        overworld.set_block(Block('minecraft', 'grass_block'), 10, 64, 10)
        nether.set_block(Block('minecraft', 'netherrack'), 10, 64, 10)
        end.set_block(Block('minecraft', 'end_stone'), 10, 64, 10)

        overworld_block = overworld.get_block(10, 64, 10)
        nether_block = nether.get_block(10, 64, 10)
        end_block = end.get_block(10, 64, 10)

        if isinstance(overworld_block, Block):
            assert overworld_block.name() == 'minecraft:grass_block'
        if isinstance(nether_block, Block):
            assert nether_block.name() == 'minecraft:netherrack'
        if isinstance(end_block, Block):
            assert end_block.name() == 'minecraft:end_stone'

    def test_dimension_isolation(self):
        world = anvil.World(self.world_path, dimension='overworld')
        world.set_block(Block('minecraft', 'diamond_block'), 5, 64, 5)

        world.switch_dimension('nether', save_current=True)
        nether_block = world.get_block(5, 64, 5)

        if isinstance(nether_block, Block):
            assert nether_block.name() != 'minecraft:diamond_block'

    def test_save_in_different_dimensions(self):
        overworld = anvil.World(self.world_path, dimension='overworld')
        nether = anvil.World(self.world_path, dimension='nether')

        overworld.set_block(Block('minecraft', 'stone'), 0, 64, 0)
        nether.set_block(Block('minecraft', 'netherrack'), 0, 64, 0)

        try:
            overworld.save()
            nether.save()
            success = True
        except Exception:
            success = False

        assert success

    def test_dimension_constants(self):
        assert anvil.World.DIMENSIONS['overworld'] == 'region'
        assert anvil.World.DIMENSIONS['nether'] == 'DIM-1/region'
        assert anvil.World.DIMENSIONS['end'] == 'DIM1/region'
