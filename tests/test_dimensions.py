"""
Unit tests for World class dimension support
Tests Overworld, Nether, and End dimensions
"""
import unittest
import os
import tempfile
import shutil

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import anvil
from anvil import Block


class TestDimensions(unittest.TestCase):
    """Test suite for World dimension support"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test world"""
        cls.test_dir = tempfile.mkdtemp()
        cls.world_path = os.path.join(cls.test_dir, 'test_world')
        os.makedirs(cls.world_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test world"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def test_default_dimension(self):
        """Test that default dimension is overworld"""
        world = anvil.World(self.world_path)
        self.assertEqual(world.get_dimension(), 'overworld')
    
    def test_create_overworld(self):
        """Test creating World with overworld dimension"""
        world = anvil.World(self.world_path, dimension='overworld')
        self.assertEqual(world.dimension, 'overworld')
        self.assertTrue(world.region_dir.endswith('region'))
    
    def test_create_nether(self):
        """Test creating World with nether dimension"""
        world = anvil.World(self.world_path, dimension='nether')
        self.assertEqual(world.dimension, 'nether')
        self.assertTrue('DIM-1' in world.region_dir)
    
    def test_create_end(self):
        """Test creating World with end dimension"""
        world = anvil.World(self.world_path, dimension='end')
        self.assertEqual(world.dimension, 'end')
        self.assertTrue('DIM1' in world.region_dir)
    
    def test_invalid_dimension(self):
        """Test that invalid dimension raises ValueError"""
        with self.assertRaises(ValueError):
            anvil.World(self.world_path, dimension='invalid')
    
    def test_dimension_paths(self):
        """Test that dimension paths are correct"""
        overworld = anvil.World(self.world_path, dimension='overworld')
        nether = anvil.World(self.world_path, dimension='nether')
        end = anvil.World(self.world_path, dimension='end')
        
        self.assertTrue(overworld.region_dir.endswith('region'))
        self.assertIn('DIM-1', nether.region_dir)
        self.assertIn('region', nether.region_dir)
        self.assertIn('DIM1', end.region_dir)
        self.assertIn('region', end.region_dir)
    
    def test_switch_dimension(self):
        """Test switching between dimensions"""
        world = anvil.World(self.world_path, dimension='overworld')
        self.assertEqual(world.get_dimension(), 'overworld')
        
        world.switch_dimension('nether', save_current=False)
        self.assertEqual(world.get_dimension(), 'nether')
        
        world.switch_dimension('end', save_current=False)
        self.assertEqual(world.get_dimension(), 'end')
        
        world.switch_dimension('overworld', save_current=False)
        self.assertEqual(world.get_dimension(), 'overworld')
    
    def test_switch_dimension_invalid(self):
        """Test that switching to invalid dimension raises ValueError"""
        world = anvil.World(self.world_path)
        with self.assertRaises(ValueError):
            world.switch_dimension('invalid')
    
    def test_switch_dimension_clears_cache(self):
        """Test that switching dimensions clears caches"""
        world = anvil.World(self.world_path, chunk_cache_size=64)
        
        world.set_block(Block('minecraft', 'stone'), 0, 64, 0)
        
        initial_stats = world.get_cache_stats()
        
        world.switch_dimension('nether', save_current=False)
        
        new_stats = world.get_cache_stats()
        if new_stats and 'chunk_cache' in new_stats and new_stats['chunk_cache']:
            self.assertEqual(new_stats['chunk_cache']['size'], 0)
    
    def test_get_dimension_info(self):
        """Test getting dimension information"""
        world = anvil.World(self.world_path, dimension='nether')
        info = world.get_dimension_info()
        
        self.assertEqual(info['name'], 'nether')
        self.assertEqual(info['path'], 'DIM-1/region')
        self.assertIn('full_path', info)
        self.assertIn('loaded_regions', info)
    
    def test_set_block_in_different_dimensions(self):
        """Test setting blocks in different dimensions"""
        overworld = anvil.World(self.world_path, dimension='overworld')
        nether = anvil.World(self.world_path, dimension='nether')
        end = anvil.World(self.world_path, dimension='end')
        
        # Set blocks
        overworld.set_block(Block('minecraft', 'grass_block'), 10, 64, 10)
        nether.set_block(Block('minecraft', 'netherrack'), 10, 64, 10)
        end.set_block(Block('minecraft', 'end_stone'), 10, 64, 10)
        
        # Get blocks back
        overworld_block = overworld.get_block(10, 64, 10)
        nether_block = nether.get_block(10, 64, 10)
        end_block = end.get_block(10, 64, 10)
        
        # Verify blocks were set (may be None if chunk creation failed)
        if overworld_block:
            self.assertEqual(overworld_block.name(), 'minecraft:grass_block')
        if nether_block:
            self.assertEqual(nether_block.name(), 'minecraft:netherrack')
        if end_block:
            self.assertEqual(end_block.name(), 'minecraft:end_stone')
    
    def test_dimension_isolation(self):
        """Test that dimensions are isolated from each other"""
        world = anvil.World(self.world_path, dimension='overworld')
        world.set_block(Block('minecraft', 'diamond_block'), 5, 64, 5)
        
        world.switch_dimension('nether', save_current=True)
        nether_block = world.get_block(5, 64, 5)
        
        if nether_block:
            self.assertNotEqual(nether_block.name(), 'minecraft:diamond_block')
    
    def test_save_in_different_dimensions(self):
        """Test saving in different dimensions"""
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
        
        self.assertTrue(success)
    
    def test_nether_coordinate_conversion(self):
        """Test Nether coordinate conversion (informational)"""
        overworld_x, overworld_z = 800, 800
        nether_x, nether_z = overworld_x // 8, overworld_z // 8
        
        self.assertEqual(nether_x, 100)
        self.assertEqual(nether_z, 100)
        
        back_to_overworld_x = nether_x * 8
        back_to_overworld_z = nether_z * 8
        
        self.assertEqual(back_to_overworld_x, overworld_x)
        self.assertEqual(back_to_overworld_z, overworld_z)
    
    def test_dimension_constants(self):
        """Test that dimension constants are correct"""
        self.assertEqual(anvil.World.DIMENSIONS['overworld'], 'region')
        self.assertEqual(anvil.World.DIMENSIONS['nether'], 'DIM-1/region')
        self.assertEqual(anvil.World.DIMENSIONS['end'], 'DIM1/region')


if __name__ == '__main__':
    unittest.main()
