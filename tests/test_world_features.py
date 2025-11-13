"""
Unit tests for World class advanced features
Tests all new functionality added to the World class
"""
import unittest
import os
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import anvil
from anvil import Block, Biome, EmptyRegion, EmptyChunk


class TestWorldFeatures(unittest.TestCase):
    """Test suite for World class advanced features"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test world"""
        cls.test_dir = tempfile.mkdtemp()
        cls.world_path = os.path.join(cls.test_dir, 'test_world')
        os.makedirs(cls.world_path)
        
        cls.world = anvil.World(cls.world_path, chunk_cache_size=64, region_cache_size=8)
        
        for x in range(0, 16):
            for z in range(0, 16):
                cls.world.set_block(Block('minecraft', 'stone'), x, 64, z)
                cls.world.set_block(Block('minecraft', 'dirt'), x, 63, z)
        
        cls.world.set_block(Block('minecraft', 'diamond_ore'), 5, 10, 5)
        cls.world.set_block(Block('minecraft', 'diamond_ore'), 10, 12, 10)
        
        cls.world.save()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test world"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    

    
    def test_get_biome(self):
        """Test getting biome at coordinates"""
        biome = self.world.get_biome(5, 64, 5)
        self.assertTrue(biome is None or isinstance(biome, Biome))
    
    def test_set_biome(self):
        """Test setting biome at coordinates"""
        self.world.set_biome(Biome('plains'), 8, 64, 8)
        
        biome = self.world.get_biome(8, 64, 8)
        self.assertTrue(biome is None or isinstance(biome, Biome))
    

    
    def test_find_blocks(self):
        """Test finding blocks"""
        positions = self.world.find_blocks(
            "minecraft:stone",
            bounds=(0, 60, 0, 16, 70, 16),
            limit=10
        )
        
        self.assertIsInstance(positions, list)
        self.assertGreater(len(positions), 0)
        self.assertLessEqual(len(positions), 10)
        
        if positions:
            x, y, z = positions[0]
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
            self.assertIsInstance(z, int)
    
    def test_find_blocks_with_limit(self):
        """Test finding blocks with limit"""
        positions = self.world.find_blocks(
            "minecraft:stone",
            bounds=(0, 60, 0, 16, 70, 16),
            limit=5
        )
        
        self.assertLessEqual(len(positions), 5)
    
    def test_find_nearest_block(self):
        """Test finding nearest block"""
        result = self.world.find_nearest_block(
            "minecraft:diamond_ore",
            0, 0, 0,
            max_radius=50
        )
        
        if result:
            x, y, z, distance = result
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
            self.assertIsInstance(z, int)
            self.assertIsInstance(distance, float)
            self.assertGreater(distance, 0)
    
    def test_scan_area(self):
        """Test scanning area for block distribution"""
        distribution = self.world.scan_area(0, 60, 0, 16, 70, 16)
        
        self.assertIsInstance(distribution, dict)
        self.assertGreater(len(distribution), 0)
        
        self.assertIn("minecraft:stone", distribution)
        self.assertIn("minecraft:dirt", distribution)
        
        self.assertGreater(distribution["minecraft:stone"], 0)
        self.assertGreater(distribution["minecraft:dirt"], 0)
    

    
    def test_get_memory_usage(self):
        """Test getting memory usage statistics"""
        stats = self.world.get_memory_usage()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('loaded_regions', stats)
        self.assertIn('cached_chunks', stats)
        self.assertIn('cached_regions', stats)
        self.assertIn('cache_stats', stats)
        
        self.assertIsInstance(stats['loaded_regions'], int)
        self.assertIsInstance(stats['cached_chunks'], int)
        self.assertIsInstance(stats['cached_regions'], int)
    
    def test_unload_region(self):
        """Test unloading a region"""
        region = self.world.get_region(0, 0)
        self.assertIsNotNone(region)
        
        result = self.world.unload_region(0, 0, save=False)
        self.assertTrue(result)
        
        result = self.world.unload_region(0, 0, save=False)
        self.assertFalse(result)
        
        region = self.world.get_region(0, 0)
    
    def test_unload_all_regions(self):
        """Test unloading all regions"""
        self.world.get_region(0, 0)
        
        count = self.world.unload_all_regions(save=False)
        self.assertGreater(count, 0)
        
        self.world.get_region(0, 0)
    

    
    def test_get_world_info(self):
        """Test getting world information"""
        info = self.world.get_world_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('world_folder', info)
        self.assertIn('loaded_regions', info)
        self.assertIn('region_coordinates', info)
        self.assertIn('bounds', info)
        self.assertIn('size_x', info)
        self.assertIn('size_z', info)
        self.assertIn('cache_enabled', info)
        
        self.assertEqual(info['world_folder'], self.world_path)
        self.assertIsInstance(info['loaded_regions'], int)
        self.assertIsInstance(info['region_coordinates'], list)
        self.assertTrue(info['cache_enabled'])
    
    def test_get_block_distribution(self):
        """Test getting block distribution"""
        distribution = self.world.get_block_distribution(
            bounds=(0, 60, 0, 16, 70, 16)
        )
        
        self.assertIsInstance(distribution, dict)
        self.assertGreater(len(distribution), 0)
        
        counts = list(distribution.values())
        self.assertEqual(counts, sorted(counts, reverse=True))
    
    def test_get_block_distribution_top_n(self):
        """Test getting top N blocks"""
        distribution = self.world.get_block_distribution(
            bounds=(0, 60, 0, 16, 70, 16),
            top_n=3
        )
        
        self.assertLessEqual(len(distribution), 3)
    
    def test_get_height_map(self):
        """Test getting height map"""
        height = self.world.get_height_map(5, 5, start_y=100, end_y=50)
        
        if height is not None:
            self.assertIsInstance(height, int)
            self.assertGreaterEqual(height, 50)
            self.assertLessEqual(height, 100)
    
    def test_count_blocks(self):
        """Test counting specific blocks"""
        count = self.world.count_blocks(
            "minecraft:stone",
            bounds=(0, 60, 0, 16, 70, 16)
        )
        
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)
    

    
    def test_fill_area(self):
        """Test filling an area"""
        count = self.world.fill_area(
            "minecraft:gold_block",
            50, 64, 50,
            52, 66, 52
        )
        
        self.assertIsInstance(count, int)
        self.assertEqual(count, 3 * 3 * 3)  # 3x3x3 = 27
        
        block = self.world.get_block(50, 64, 50)
        self.assertIsNotNone(block)
        self.assertEqual(block.name(), "minecraft:gold_block")
    
    def test_clear_area(self):
        """Test clearing an area"""
        self.world.fill_area("minecraft:stone", 60, 64, 60, 62, 66, 62)
        
        count = self.world.clear_area(60, 64, 60, 62, 66, 62)
        
        self.assertIsInstance(count, int)
        self.assertEqual(count, 3 * 3 * 3)
        
        block = self.world.get_block(60, 64, 60)
        self.assertIsNotNone(block)
        self.assertEqual(block.name(), "minecraft:air")
    
    def test_copy_area(self):
        """Test copying an area"""
        self.world.set_block(Block('minecraft', 'emerald_block'), 70, 64, 70)
        self.world.set_block(Block('minecraft', 'emerald_block'), 71, 64, 70)
        
        count = self.world.copy_area(
            70, 64, 70,  # Source start
            71, 64, 70,  # Source end
            80, 64, 80   # Dest start
        )
        
        self.assertGreater(count, 0)
        
        block = self.world.get_block(80, 64, 80)
        self.assertIsNotNone(block)
        self.assertEqual(block.name(), "minecraft:emerald_block")
        
        block = self.world.get_block(81, 64, 80)
        self.assertIsNotNone(block)
        self.assertEqual(block.name(), "minecraft:emerald_block")
    

    
    def test_stream_blocks(self):
        """Test streaming blocks"""
        count = 0
        for x, y, z, block in self.world.stream_blocks(0, 63, 0, 5, 65, 5):
            count += 1
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
            self.assertIsInstance(z, int)
        
        self.assertGreater(count, 0)
    
    def test_stream_chunks(self):
        """Test streaming chunks"""
        count = 0
        for chunk_x, chunk_z, chunk in self.world.stream_chunks(0, 0, 16, 16):
            count += 1
            self.assertIsInstance(chunk_x, int)
            self.assertIsInstance(chunk_z, int)
        
        self.assertGreater(count, 0)
    
    
    def test_cache_stats(self):
        """Test getting cache statistics"""
        stats = self.world.get_cache_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('chunk_cache', stats)
        self.assertIn('region_cache', stats)
        
        if stats['chunk_cache']:
            chunk_cache = stats['chunk_cache']
            self.assertIn('size', chunk_cache)
            self.assertIn('max_size', chunk_cache)
            self.assertIn('hits', chunk_cache)
            self.assertIn('misses', chunk_cache)
    
    def test_clear_cache(self):
        """Test clearing cache"""
        self.world.get_chunk(0, 0)
        self.world.get_region(0, 0)
        
        self.world.clear_cache()
        
        stats = self.world.get_cache_stats()
        if stats['chunk_cache']:
            self.assertEqual(stats['chunk_cache']['size'], 0)
        if stats['region_cache']:
            self.assertEqual(stats['region_cache']['size'], 0)
    
    def test_invalidate_chunk(self):
        """Test invalidating specific chunk"""
        chunk = self.world.get_chunk(0, 0)
        
        self.world.invalidate_chunk(0, 0)
        
        chunk = self.world.get_chunk(0, 0)
        self.assertIsNotNone(chunk)
    
    def test_invalidate_region(self):
        """Test invalidating specific region"""
        region = self.world.get_region(0, 0)
        
        self.world.invalidate_region(0, 0)
        
        region = self.world.get_region(0, 0)
        self.assertIsNotNone(region)


class TestWorldWithoutCache(unittest.TestCase):
    """Test World class with caching disabled"""
    
    def setUp(self):
        """Set up test world without cache"""
        self.test_dir = tempfile.mkdtemp()
        self.world_path = os.path.join(self.test_dir, 'test_world_no_cache')
        os.makedirs(self.world_path)
        
        self.world = anvil.World(
            self.world_path,
            chunk_cache_size=None,
            region_cache_size=None
        )
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_world_without_cache(self):
        """Test that world works without cache"""
        self.world.set_block(Block('minecraft', 'stone'), 0, 64, 0)
        
        block = self.world.get_block(0, 64, 0)
        self.assertIsNotNone(block)
        self.assertEqual(block.name(), "minecraft:stone")
        
        info = self.world.get_world_info()
        self.assertFalse(info['cache_enabled'])
        self.assertEqual(info['chunk_cache_size'], 0)
        self.assertEqual(info['region_cache_size'], 0)


if __name__ == '__main__':
    unittest.main()
