import os
from typing import Dict, Tuple, Union, Optional, List
import math
from .region import Region
from .empty_region import EmptyRegion
from .chunk import Chunk
from .empty_chunk import EmptyChunk
from .structure import Structure
from .block import Block
from .biome import Biome
from .errors import OutOfBoundsCoordinates
from .cache_manager import CacheManager


class World:
    """
    Represents a Minecraft world, managing multiple regions with LRU caching.
    Supports Overworld, Nether (DIM-1), and End (DIM1) dimensions.
    
    Attributes
    ----------
    world_folder: str
        Path to the world folder
    dimension: str
        Current dimension ('overworld', 'nether', or 'end')
    regions: Dict[Tuple[int, int], Region]
        Dictionary of loaded regions, with region coordinates as keys
    _chunk_cache: CacheManager
        LRU cache for chunks across all regions
    _region_cache: CacheManager
        LRU cache for loaded regions
    """
    
    DIMENSIONS = {
        'overworld': 'region',
        'nether': 'DIM-1/region',
        'end': 'DIM1/region'
    }
    
    def __init__(self, world_folder: str, dimension: str = 'overworld', 
                 chunk_cache_size: int = 512, region_cache_size: int = 32):
        """
        Initialize a World object with caching support.
        
        Parameters
        ----------
        world_folder: str
            Path to the world folder
        dimension: str
            Dimension to load ('overworld', 'nether', or 'end'). Default: 'overworld'
        chunk_cache_size: int
            Maximum number of chunks to cache (default: 512)
        region_cache_size: int
            Maximum number of regions to keep in memory (default: 32)
            
        Example
        -------
        >>> world = World(r'C:\\path\\to\\world')  # Overworld
        >>> nether = World(r'C:\\path\\to\\world', dimension='nether')
        >>> end = World(r'C:\\path\\to\\world', dimension='end')
        """
        if dimension not in self.DIMENSIONS:
            raise ValueError(f"Invalid dimension '{dimension}'. Must be one of: {list(self.DIMENSIONS.keys())}")
        
        self.world_folder = world_folder
        self.dimension = dimension
        self.regions: Dict[Tuple[int, int], Union[Region, EmptyRegion]] = {}
        
        # Initialize caches (None disables caching)
        self._chunk_cache = CacheManager(max_size=chunk_cache_size) if chunk_cache_size else None
        self._region_cache = CacheManager(max_size=region_cache_size) if region_cache_size else None
        
        self.region_dir = os.path.join(world_folder, self.DIMENSIONS[dimension])
        os.makedirs(self.region_dir, exist_ok=True)
    
    def get_region(self, region_x: int, region_z: int) -> Union[Region, EmptyRegion]:
        """
        Get a region at the specified coordinates with caching support.
        If the region doesn't exist in memory, try to load it from disk.
        If it doesn't exist on disk, create a new empty region.
        
        Parameters
        ----------
        region_x: int
            Region X coordinate
        region_z: int
            Region Z coordinate
            
        Returns
        -------
        Union[Region, EmptyRegion]
            The region at the specified coordinates
        """
        region_coords = (region_x, region_z)
        
        if self._region_cache is not None:
            cached_region = self._region_cache.get(region_coords)
            if cached_region is not None:
                return cached_region
        
        # Check in-memory regions
        if region_coords in self.regions:
            region = self.regions[region_coords]
            if self._region_cache is not None:
                self._region_cache.put(region_coords, region)
            return region
        
        # Load from disk
        region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
        if os.path.exists(region_path):
            # Disable Region's internal cache since World has its own cache
            region = Region.from_file(region_path, cache_size=None)
            self.regions[region_coords] = region
            if self._region_cache is not None:
                self._region_cache.put(region_coords, region)
            return region
        
        # Create new empty region
        empty_region = EmptyRegion(region_x, region_z)
        self.regions[region_coords] = empty_region
        if self._region_cache is not None:
            self._region_cache.put(region_coords, empty_region)
        return empty_region
    
    def get_chunk(self, chunk_x: int, chunk_z: int) -> Union[Chunk, EmptyChunk, None]:
        """
        Get a chunk at the specified coordinates with caching support.
        
        Parameters
        ----------
        chunk_x: int
            Chunk X coordinate
        chunk_z: int
            Chunk Z coordinate
            
        Returns
        -------
        Union[Chunk, EmptyChunk, None]
            The chunk at the specified coordinates, or None if not found
        """
        chunk_key = (chunk_x, chunk_z)
        if self._chunk_cache is not None:
            cached_chunk = self._chunk_cache.get(chunk_key)
            if cached_chunk is not None:
                return cached_chunk
        
        region_x = chunk_x >> 5 
        region_z = chunk_z >> 5  
        
        region = self.get_region(region_x, region_z)
        
        chunk = None
        if isinstance(region, Region):
            try:
                chunk = region.get_chunk(chunk_x % 32, chunk_z % 32)
            except:
                chunk = None
        elif isinstance(region, EmptyRegion):
            chunk = region.get_chunk(chunk_x, chunk_z)
        
        if chunk is not None and self._chunk_cache is not None:
            self._chunk_cache.put(chunk_key, chunk)
        
        return chunk
    
    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """
        Get a block at the specified global coordinates.
        
        Parameters
        ----------
        x: int
            Global X coordinate
        y: int
            Global Y coordinate
        z: int
            Global Z coordinate
            
        Returns
        -------
        Optional[Block]
            The block at the specified coordinates, or None if not found
        """
        chunk_x = x >> 4  
        chunk_z = z >> 4  
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            return None
        
        local_x = x & 15 
        local_z = z & 15 
        
        try:
            return chunk.get_block(local_x, y, local_z)
        except:
            return None
    def is_in_palette_section(self, block: Block, x: int, y: int, z:int) -> bool:
        """
        Check if a block exists in the palette of the section containing the specified global coordinates.
        
        Parameters
        ----------
        block: Block
            The block to check
        x: int
            Global X coordinate
        y: int
            Global Y coordinate
        z: int
            Global Z coordinate
            
        Returns
        -------
        bool
            True if the block exists in the palette, False otherwise
        """
        chunk_x = x >> 4  
        chunk_z = z >> 4  
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            return False
        
        section_index = y >> 4  
        section = chunk.get_section(section_index)
        if section is None:
            return False
        
        palette = chunk.get_palette(section)
        return chunk._is_block_in_palette(palette, block)
    
    def add_block_to_palette(self, block: Block, x: int, y: int, z: int) -> int:
        """
        Add a block to the palette of the section containing the specified global coordinates.
        
        Parameters
        ----------
        block: Block
            The block to add
        x: int
            Global X coordinate
        y: int
            Global Y coordinate
        z: int
            Global Z coordinate
            
        Returns
        -------
        int
            The index of the block in the palette after adding
        """
        chunk_x = x >> 4  
        chunk_z = z >> 4  
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            raise OutOfBoundsCoordinates("Chunk does not exist")
        
        section_index = y >> 4  
        section = chunk.get_section(section_index)
        if section is None:
            raise OutOfBoundsCoordinates("Section does not exist")
        index_palette = chunk._add_block_to_palette(section, block)
        self.save()
        return index_palette
    
    def set_block(self, block: Block, x: int, y: int, z: int) -> None:
        """
        Set a block at the specified global coordinates.
        
        Parameters
        ----------
        block: Block
            The block to set
        x: int
            Global X coordinate
        y: int
            Global Y coordinate
        z: int
            Global Z coordinate
        """
        region_x = x >> 9  # Divide by 512 (x >> 9 equivalent to x // 512)
        region_z = z >> 9  # Divide by 512 (z >> 9 equivalent to z // 512)

        region = self.get_region(region_x, region_z)
        try:
            if isinstance(region, Region):
                region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
                region.set_block(block, x, y, z, region_path)
            else:
                # EmptyRegion handling
                region.set_block(block, x, y, z) 
        except Exception as e:
            # If setting block fails on Region, convert to EmptyRegion
            if isinstance(region, Region):
                empty_region = EmptyRegion(region_x, region_z)
                
                # Copy existing chunks to the new empty region
                for cx in range(32):
                    for cz in range(32):
                        try:
                            chunk = region.get_chunk(cx, cz)
                            if chunk:
                                empty_region.add_chunk(chunk)
                        except:
                            pass
                
                # Replace region with empty region and retry
                self.regions[(region_x, region_z)] = empty_region
                empty_region.set_block(block, x, y, z)

    def get_biome(self, x: int, y: int, z: int) -> Optional[Biome]:
        """
        Get the biome at the specified global coordinates.
        
        Parameters
        ----------
        x: int
            Global X coordinate
        y: int
            Global Y coordinate
        z: int
            Global Z coordinate
            
        Returns
        -------
        Optional[Biome]
            The biome at the specified coordinates, or None if not found
            
        Example
        -------
        >>> biome = world.get_biome(100, 64, -50)
        >>> print(biome.name())
        """
        chunk_x = x >> 4  
        chunk_z = z >> 4  
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            return None
        
        local_x = x & 15 
        local_z = z & 15 
        
        try:
            return chunk.get_biome(local_x, y, local_z)
        except:
            return None

    def set_biome(self, biome: Biome, x: int, y: int, z: int) -> None:
        """
        Set the biome at the specified global coordinates.
        This sets the biome for a 4x4x4 volume.
        
        Parameters
        ----------
        biome: Biome
            The biome to set
        x: int
            Global X coordinate
        y: int
            Global Y coordinate
        z: int
            Global Z coordinate
            
        Example
        -------
        >>> from anvil import Biome
        >>> world.set_biome(Biome.from_name("minecraft:desert"), 100, 64, -50)
        """
        chunk_x = x >> 4  
        chunk_z = z >> 4  
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            raise OutOfBoundsCoordinates("Chunk does not exist")
        
        local_x = x & 15 
        local_z = z & 15 
        
        # EmptyChunk.set_biome() takes only x, z (no y parameter)
        # while Chunk.set_biome() takes x, y, z
        if isinstance(chunk, EmptyChunk):
            chunk.set_biome(biome, local_x, local_z)
        else:
            chunk.set_biome(biome, local_x, y, local_z)
        self.save()

    def set_chunk_biome(self, biome: Biome, chunk_x: int, chunk_z: int) -> None:
        """
        Set the entire chunk to a single biome (optimized for uniform biomes).
        
        Parameters
        ----------
        biome: Biome
            The biome to set for the entire chunk
        chunk_x: int
            Chunk X coordinate
        chunk_z: int
            Chunk Z coordinate
            
        Example
        -------
        >>> from anvil import Biome
        >>> world.set_chunk_biome(Biome.from_name("minecraft:ice_spikes"), 5, -3)
        """
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            raise OutOfBoundsCoordinates("Chunk does not exist")
        
        chunk.set_chunk_biome(biome)
        self.save()

    def set_section_biome(self, biome: Biome, chunk_x: int, chunk_z: int, section_y: int) -> None:
        """
        Set an entire section to a single biome within a chunk.
        
        Parameters
        ----------
        biome: Biome
            The biome to set for the entire section
        chunk_x: int
            Chunk X coordinate
        chunk_z: int
            Chunk Z coordinate
        section_y: int
            Section Y index (e.g., -4 to 19 for standard world height)
            
        Example
        -------
        >>> from anvil import Biome
        >>> world.set_section_biome(Biome.from_name("minecraft:jungle"), 5, -3, 4)
        """
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            raise OutOfBoundsCoordinates("Chunk does not exist")
        
        section = chunk.get_section(section_y)
        if section is None:
            section = chunk._create_section(section_y)
        
        biome_name = biome.name()
        
        # Create or update biomes structure in section
        if 'biomes' not in section:
            from . import nbt
            biomes_data = nbt.TAG_Compound(name='biomes')
            palette = nbt.TAG_List(name='palette', type=nbt.TAG_String)
            palette.tags.append(nbt.TAG_String(value=biome_name))
            biomes_data.tags.append(palette)
            section.tags.append(biomes_data)
        else:
            biomes_data = section['biomes']
            palette = biomes_data['palette']
            
            # Reset palette to single biome
            palette.tags.clear()
            palette.tags.append(nbt.TAG_String(value=biome_name))
            
            # Remove data array if present (not needed for uniform biome)
            biomes_data.tags[:] = [tag for tag in biomes_data.tags if tag.name != 'data']
        
        self.save()

    def set_region_biome(self, biome: Biome, region_x: int, region_z: int) -> None:
        """
        Set all chunks in a region to a single biome.
        
        Parameters
        ----------
        biome: Biome
            The biome to set for the entire region
        region_x: int
            Region X coordinate
        region_z: int
            Region Z coordinate
            
        Example
        -------
        >>> from anvil import Biome
        >>> world.set_region_biome(Biome.from_name("minecraft:plains"), 0, 0)
        """
        region = self.get_region(region_x, region_z)
        
        # Iterate through all possible chunks in the region
        for chunk_x in range(32):
            for chunk_z in range(32):
                try:
                    if isinstance(region, Region):
                        chunk = region.get_chunk(chunk_x, chunk_z)
                    else:
                        # Calculate global chunk coordinates for EmptyRegion
                        global_chunk_x = region_x * 32 + chunk_x
                        global_chunk_z = region_z * 32 + chunk_z
                        chunk = region.get_chunk(global_chunk_x, global_chunk_z)
                    
                    if chunk is not None:
                        chunk.set_chunk_biome(biome)
                except:
                    continue
        
        self.save()

    def replace_block_at(self, x: int, y: int, z: int, new_block: Union[str, Block]) -> bool:
        """
        Replace a single block at specific global coordinates.

        Parameters
        ----------
        x : int
            Global X coordinate
        y : int
            Global Y coordinate
        z : int
            Global Z coordinate
        new_block : Union[str, Block]
            The replacement block (either a block name like "minecraft:dirt" or a Block object)

        Returns
        -------
        bool
            True if the block was replaced, False otherwise

        Example
        -------
        >>> world.replace_block_at(100, 64, -50, "minecraft:diamond_block")
        >>> world.replace_block_at(100, 64, -50, Block.from_name("minecraft:stone"))
        """
        region_x = x >> 9
        region_z = z >> 9

        region = self.get_region(region_x, region_z)

        if isinstance(region, EmptyRegion):
            return False

        file_path = os.path.join(self.world_folder, 'region', f'r.{region_x}.{region_z}.mca')

        return region.replace_block_at(x, y, z, new_block, file_path)

    def replace_blocks(self, old_block: Union[str, Block], new_block: Union[str, Block],
                       bounds: Optional[Tuple[int, int, int, int, int, int]] = None) -> int:
        """
        Replace all occurrences of a specific block type with another block type.
        
        Parameters
        ----------
        old_block : Union[str, Block]
            The block to replace (either a block name like "minecraft:stone" or a Block object)
        new_block : Union[str, Block]
            The replacement block (either a block name like "minecraft:dirt" or a Block object)
        bounds : Optional[Tuple[int, int, int, int, int, int]]
            Bounding box as (min_x, min_y, min_z, max_x, max_y, max_z)
            If None, replaces blocks in the entire world
        
        Returns
        -------
        int
            The number of blocks replaced
        
        Example
        -------
        >>> world.replace_blocks("minecraft:stone", "minecraft:dirt")
        >>> world.replace_blocks(Block.from_name("minecraft:oak_log"), Block.from_name("minecraft:birch_log"), 
        ...                     bounds=(0, 60, 0, 100, 70, 100))
        """
        # Convert strings to Block objects if needed
        if isinstance(old_block, str):
            old_block = Block.from_name(old_block)
        if isinstance(new_block, str):
            new_block = Block.from_name(new_block)
        
        old_block_name = old_block.name()
        count = 0
        
        # Determine the range of chunks to check
        if bounds:
            min_x, min_y, min_z, max_x, max_y, max_z = bounds
            min_chunk_x = min_x >> 4
            min_chunk_z = min_z >> 4
            max_chunk_x = max_x >> 4
            max_chunk_z = max_z >> 4
        else:
            min_chunk_x = min_chunk_z = max_chunk_x = max_chunk_z = None
        
        if bounds is None:
            for (region_x, region_z), region in self.regions.items():
                if isinstance(region, Region):
                    for chunk_x in range(32):
                        for chunk_z in range(32):
                            try:
                                chunk = region.get_chunk(chunk_x, chunk_z)
                                if chunk:
                                    chunk_count = chunk.replace_blocks(old_block, new_block)
                                    count += chunk_count
                            except:
                                continue
                elif isinstance(region, EmptyRegion):
                    for chunk_x in range(32):
                        for chunk_z in range(32):
                            chunk = region.get_chunk(chunk_x, chunk_z)
                            if chunk:
                                chunk_count = chunk.replace_blocks(old_block, new_block)
                                count += chunk_count
        else:
            for chunk_x in range(min_chunk_x, max_chunk_x + 1):
                for chunk_z in range(min_chunk_z, max_chunk_z + 1):
                    chunk = self.get_chunk(chunk_x, chunk_z)
                    if chunk:
                        chunk_min_x = chunk_x * 16
                        chunk_min_z = chunk_z * 16
                        chunk_max_x = chunk_min_x + 15
                        chunk_max_z = chunk_min_z + 15
                        
                        if (chunk_max_x < min_x or chunk_min_x > max_x or 
                            chunk_max_z < min_z or chunk_min_z > max_z):
                            continue
                        
                        # Replace blocks in this chunk with bounds checking
                        for x in range(max(0, min_x - chunk_min_x), min(16, max_x - chunk_min_x + 1)):
                            for z in range(max(0, min_z - chunk_min_z), min(16, max_z - chunk_min_z + 1)):
                                for y in range(min_y, max_y + 1):
                                    try:
                                        current_block = chunk.get_block(x, y, z)
                                        if current_block.name() == old_block_name:
                                            if not old_block.properties or current_block.properties == old_block.properties:
                                                if chunk.replace_block_at(x, y, z, new_block):
                                                    count += 1
                                    except (IndexError, OutOfBoundsCoordinates):
                                        continue
        
        return count
    
    def replace_blocks_in_area(self, old_block: Union[str, Block], new_block: Union[str, Block], 
                               x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> int:
        """
        Replace all occurrences of a specific block type with another block type within a defined area.
        
        Parameters
        ----------
        old_block : Union[str, Block]
            The block to replace (either a block name like "minecraft:stone" or a Block object)
        new_block : Union[str, Block]
            The replacement block (either a block name like "minecraft:dirt" or a Block object)
        x1, y1, z1 : int
            Minimum coordinates of the area
        x2, y2, z2 : int
            Maximum coordinates of the area
        
        Returns
        -------
        int
            The number of blocks replaced
        
        Example
        -------
        >>> count = world.replace_blocks_in_area("minecraft:stone", "minecraft:dirt", 
        ...                                      0, 60, 0, 100, 70, 100)
        """
        bounds = (min(x1, x2), min(y1, y2), min(z1, z2), max(x1, x2), max(y1, y2), max(z1, z2))
        return self.replace_blocks(old_block, new_block, bounds)
    
    def stream_blocks(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int):
        """
        Stream blocks in a defined area efficiently. Returns a generator that yields (x, y, z, block).
        
        Parameters
        ----------
        x1, y1, z1 : int
            Minimum coordinates of the area
        x2, y2, z2 : int
            Maximum coordinates of the area
        
        Yields
        ------
        Tuple[int, int, int, Block]
            (x, y, z, block) for each block in the area
        
        Example
        -------
        >>> for x, y, z, block in world.stream_blocks(0, 60, 0, 10, 65, 10):
        ...     if block.name() == "minecraft:stone":
        ...         print(f"Found stone at {x}, {y}, {z}")
        """
        min_x, min_y, min_z = min(x1, x2), min(y1, y2), min(z1, z2)
        max_x, max_y, max_z = max(x1, x2), max(y1, y2), max(z1, z2)
        
        min_chunk_x = min_x >> 4
        min_chunk_z = min_z >> 4
        max_chunk_x = max_x >> 4
        max_chunk_z = max_z >> 4
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_z in range(min_chunk_z, max_chunk_z + 1):
                chunk = self.get_chunk(chunk_x, chunk_z)
                if chunk is None:
                    continue
                
                chunk_min_x = chunk_x * 16
                chunk_min_z = chunk_z * 16
                chunk_max_x = chunk_min_x + 15
                chunk_max_z = chunk_min_z + 15
                
                overlap_min_x = max(min_x, chunk_min_x)
                overlap_max_x = min(max_x, chunk_max_x)
                overlap_min_z = max(min_z, chunk_min_z)
                overlap_max_z = min(max_z, chunk_max_z)
                
                for x in range(overlap_min_x, overlap_max_x + 1):
                    for z in range(overlap_min_z, overlap_max_z + 1):
                        for y in range(min_y, max_y + 1):
                            try:
                                block = chunk.get_block(x - chunk_min_x, y, z - chunk_min_z)
                                yield (x, y, z, block)
                            except (IndexError, OutOfBoundsCoordinates):
                                continue
    
    def stream_chunks(self, x1: int, z1: int, x2: int, z2: int):
        """
        Stream chunks in a defined area efficiently. Returns a generator that yields (chunk_x, chunk_z, chunk).
        
        Parameters
        ----------
        x1, z1 : int
            Minimum coordinates of the area
        x2, z2 : int
            Maximum coordinates of the area
        
        Yields
        ------
        Tuple[int, int, Union[Chunk, EmptyChunk, None]]
            (chunk_x, chunk_z, chunk) for each chunk in the area
        
        Example
        -------
        >>> for chunk_x, chunk_z, chunk in world.stream_chunks(-10, -10, 10, 10):
        ...     if chunk:
        ...         print(f"Found chunk at {chunk_x}, {chunk_z}")
        """
        min_x, min_z = min(x1, x2), min(z1, z2)
        max_x, max_z = max(x1, x2), max(z1, z2)
        
        min_chunk_x = min_x >> 4
        min_chunk_z = min_z >> 4
        max_chunk_x = max_x >> 4
        max_chunk_z = max_z >> 4
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_z in range(min_chunk_z, max_chunk_z + 1):
                chunk = self.get_chunk(chunk_x, chunk_z)
                yield (chunk_x, chunk_z, chunk)
    
    def get_world_bounds(self) -> Optional[Tuple[int, int, int, int, int, int]]:
        """
        Get the bounds of the world based on existing region files.
        If no regions are loaded in memory, scans region files on disk.
        
        Returns
        -------
        Optional[Tuple[int, int, int, int, int, int]]
            (min_x, min_y, min_z, max_x, max_y, max_z) or None if no regions exist
            Note: Only X and Z bounds are accurate, Y bounds are set to Minecraft world limits
        """
        region_coords = []
        
        # First, try to use loaded regions in memory
        if self.regions:
            region_coords = list(self.regions.keys())
        # If no regions loaded, scan disk
        elif os.path.exists(self.region_dir):
            region_files = [f for f in os.listdir(self.region_dir) if f.endswith('.mca')]
            for region_file in region_files:
                # Parse region coordinates from filename (r.x.z.mca)
                parts = region_file.replace('.mca', '').split('.')
                if len(parts) == 3:
                    try:
                        region_x = int(parts[1])
                        region_z = int(parts[2])
                        region_coords.append((region_x, region_z))
                    except (ValueError, IndexError):
                        continue
        
        if not region_coords:
            return None
        
        min_x = min_z = float('inf')
        max_x = max_z = float('-inf')
        
        for region_x, region_z in region_coords:
            region_min_x = region_x * 512
            region_max_x = region_min_x + 511
            region_min_z = region_z * 512
            region_max_z = region_min_z + 511
            
            min_x = min(min_x, region_min_x)
            max_x = max(max_x, region_max_x)
            min_z = min(min_z, region_min_z)
            max_z = max(max_z, region_max_z)
        
        min_y = -64
        max_y = 320
        
        return (int(min_x), min_y, int(min_z), int(max_x), max_y, int(max_z))
    
    def count_blocks(self, block: Union[str, Block], bounds: Optional[Tuple[int, int, int, int, int, int]] = None) -> int:
        """
        Count the occurrences of a specific block type in the world or within bounds.
        
        Parameters
        ----------
        block : Union[str, Block]
            The block to count (either a block name like "minecraft:stone" or a Block object)
        bounds : Optional[Tuple[int, int, int, int, int, int]]
            Bounding box as (min_x, min_y, min_z, max_x, max_y, max_z)
            If None, counts blocks in the entire world (scans all region files on disk)
        
        Returns
        -------
        int
            The number of blocks found
        
        Example
        -------
        >>> stone_count = world.count_blocks("minecraft:stone")
        >>> dirt_count = world.count_blocks("minecraft:dirt", (0, 60, 0, 100, 70, 100))
        """
        if isinstance(block, str):
            block = Block.from_name(block)
        
        block_name = block.name()
        count = 0
        
        if bounds:
            x1, y1, z1, x2, y2, z2 = bounds
            for x, y, z, current_block in self.stream_blocks(x1, y1, z1, x2, y2, z2):
                if current_block is not None and current_block.name() == block_name:
                    if not block.properties or current_block.properties == block.properties:
                        count += 1
        else:
            # Scan all region files on disk, not just loaded regions
            if os.path.exists(self.region_dir):
                region_files = [f for f in os.listdir(self.region_dir) if f.endswith('.mca')]
                for region_file in region_files:
                    # Parse region coordinates from filename (r.x.z.mca)
                    parts = region_file.replace('.mca', '').split('.')
                    if len(parts) == 3:
                        try:
                            region_x = int(parts[1])
                            region_z = int(parts[2])
                            # Get bounds for this region
                            min_x = region_x * 512
                            max_x = min_x + 511
                            min_z = region_z * 512
                            max_z = min_z + 511
                            # Stream blocks in this region
                            for x, y, z, current_block in self.stream_blocks(min_x, -64, min_z, max_x, 320, max_z):
                                if current_block is not None and current_block.name() == block_name:
                                    if not block.properties or current_block.properties == block.properties:
                                        count += 1
                        except (ValueError, IndexError):
                            continue
        
        return count
    
    def get_loaded_regions(self) -> List[Tuple[int, int]]:
        """
        Get a list of all currently loaded region coordinates.
        
        Returns
        -------
        List[Tuple[int, int]]
            List of (region_x, region_z) tuples
        """
        return list(self.regions.keys())
    
    def apply_figure(self, figure_cls, blocks, point, size, filled=True) -> None:
        """
        Create and apply a geometric figure to the world.
        
        Parameters
        ----------
        figure_cls : class
            The class of the figure (e.g., Cube, Pyramid, Sphere, Spiral)
        blocks : list[Block]
            List of block types to use
        point : tuple[int, int, int]
            Starting point (x, y, z)
        size : tuple[int, int, int]
            Size of the figure (width, height, depth)
        filled : bool
            If True, use filled figure, else use empty (hollow)
        """
        figure = figure_cls(blocks, point, size)
        dictblock = figure.filled() if filled else figure.empty()
        self.apply(dictblock)

    def apply(self, dictionary) -> None:
        """
        Apply the given dictionary of changes to the world.
        """
        for k, v in dictionary.items():
            self.set_block(v, k[0], k[1], k[2])
    
    def save(self) -> None:
        """
        Save all modified regions to disk.
        """
        for (region_x, region_z), region in self.regions.items():
            region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
            
            if isinstance(region, EmptyRegion):
                # Save EmptyRegion
                region.save(region_path)
            elif isinstance(region, Region):
                # Save Region
                region.save(region_path)
    
    def clear_cache(self) -> None:
        """Clear all caches (chunks and regions)."""
        if self._chunk_cache is not None:
            self._chunk_cache.clear()
        if self._region_cache is not None:
            self._region_cache.clear()
    
    def get_cache_stats(self) -> dict:
        """
        Get statistics about cache performance.
        
        Returns
        -------
        dict
            Dictionary with cache statistics for chunks and regions
        """
        return {
            'chunk_cache': self._chunk_cache.get_stats() if self._chunk_cache else None,
            'region_cache': self._region_cache.get_stats() if self._region_cache else None
        }
    
    def invalidate_chunk(self, chunk_x: int, chunk_z: int) -> None:
        """
        Invalidate a specific chunk in the cache.
        
        Parameters
        ----------
        chunk_x : int
            Chunk X coordinate
        chunk_z : int
            Chunk Z coordinate
        """
        if self._chunk_cache is not None:
            self._chunk_cache.invalidate((chunk_x, chunk_z))
    
    def invalidate_region(self, region_x: int, region_z: int) -> None:
        """
        Invalidate a specific region in the cache.
        
        Parameters
        ----------
        region_x : int
            Region X coordinate
        region_z : int
            Region Z coordinate
        """
        if self._region_cache is not None:
            self._region_cache.invalidate((region_x, region_z))
    

    
    def get_biome(self, x: int, y: int, z: int) -> Optional[Biome]:
        """
        Get a biome at the specified global coordinates.
        
        Parameters
        ----------
        x : int
            Global X coordinate
        y : int
            Global Y coordinate
        z : int
            Global Z coordinate
            
        Returns
        -------
        Optional[Biome]
            The biome at the specified coordinates, or None if not found
        
        Example
        -------
        >>> biome = world.get_biome(100, 64, 200)
        >>> print(biome.name())
        """
        chunk_x = x >> 4
        chunk_z = z >> 4
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            return None
        
        local_x = x & 15
        local_z = z & 15
        
        try:
            return chunk.get_biome(local_x, y, local_z)
        except:
            return None
    
    def set_biome(self, biome: Biome, x: int, y: int, z: int) -> None:
        """
        Set a biome at the specified global coordinates.
        
        Parameters
        ----------
        biome : Biome
            The biome to set
        x : int
            Global X coordinate
        y : int
            Global Y coordinate
        z : int
            Global Z coordinate
        
        Example
        -------
        >>> from anvil import Biome
        >>> world.set_biome(Biome('desert'), 100, 64, 200)
        """
        chunk_x = x >> 4
        chunk_z = z >> 4
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            # Create new chunk if needed
            region_x = chunk_x >> 5
            region_z = chunk_z >> 5
            region = self.get_region(region_x, region_z)
            if isinstance(region, EmptyRegion):
                empty_chunk = EmptyChunk(chunk_x, chunk_z)
                region.add_chunk(empty_chunk)
                chunk = empty_chunk
        
        local_x = x & 15
        local_z = z & 15
        
        try:
            chunk.set_biome(biome, local_x, y, local_z)
        except Exception as e:
            print(f"Failed to set biome at ({x}, {y}, {z}): {e}")
    
    def replace_biomes(self, old_biome: Union[str, Biome], new_biome: Union[str, Biome],
                       bounds: Optional[Tuple[int, int, int, int, int, int]] = None) -> int:
        """
        Replace all occurrences of a specific biome with another biome.
        
        Parameters
        ----------
        old_biome : Union[str, Biome]
            The biome to replace (either a biome name like "minecraft:desert" or a Biome object)
        new_biome : Union[str, Biome]
            The replacement biome (either a biome name like "minecraft:plains" or a Biome object)
        bounds : Optional[Tuple[int, int, int, int, int, int]]
            Bounding box as (min_x, min_y, min_z, max_x, max_y, max_z)
            If None, replaces biomes in the entire world
        
        Returns
        -------
        int
            The number of biomes replaced
        
        Example
        -------
        >>> count = world.replace_biomes("minecraft:desert", "minecraft:plains")
        >>> count = world.replace_biomes(Biome('desert'), Biome('plains'), bounds=(0, 60, 0, 100, 70, 100))
        """
        if isinstance(old_biome, str):
            old_biome = Biome.from_name(old_biome)
        if isinstance(new_biome, str):
            new_biome = Biome.from_name(new_biome)
        
        old_biome_name = old_biome.name()
        count = 0
        
        if bounds:
            x1, y1, z1, x2, y2, z2 = bounds
            for x, y, z, block in self.stream_blocks(x1, y1, z1, x2, y2, z2):
                try:
                    current_biome = self.get_biome(x, y, z)
                    if current_biome and current_biome.name() == old_biome_name:
                        self.set_biome(new_biome, x, y, z)
                        count += 1
                except:
                    continue
        else:
            world_bounds = self.get_world_bounds()
            if world_bounds:
                min_x, min_y, min_z, max_x, max_y, max_z = world_bounds
                for x, y, z, block in self.stream_blocks(min_x, min_y, min_z, max_x, max_y, max_z):
                    try:
                        current_biome = self.get_biome(x, y, z)
                        if current_biome and current_biome.name() == old_biome_name:
                            self.set_biome(new_biome, x, y, z)
                            count += 1
                    except:
                        continue
        
        return count
    

    
    def find_blocks(self, block: Union[str, Block], 
                    bounds: Optional[Tuple[int, int, int, int, int, int]] = None,
                    limit: Optional[int] = None) -> List[Tuple[int, int, int]]:
        """
        Find all positions of a specific block type in the world.
        
        Parameters
        ----------
        block : Union[str, Block]
            The block to find (either a block name like "minecraft:diamond_ore" or a Block object)
        bounds : Optional[Tuple[int, int, int, int, int, int]]
            Bounding box as (min_x, min_y, min_z, max_x, max_y, max_z)
            If None, searches the entire loaded world
        limit : Optional[int]
            Maximum number of blocks to find (None = no limit)
        
        Returns
        -------
        List[Tuple[int, int, int]]
            List of (x, y, z) positions where the block was found
        
        Example
        -------
        >>> positions = world.find_blocks("minecraft:diamond_ore", limit=10)
        >>> for x, y, z in positions:
        ...     print(f"Found diamond ore at {x}, {y}, {z}")
        """
        if isinstance(block, str):
            block = Block.from_name(block)
        
        block_name = block.name()
        positions = []
        
        if bounds:
            x1, y1, z1, x2, y2, z2 = bounds
        else:
            world_bounds = self.get_world_bounds()
            if not world_bounds:
                return positions
            x1, y1, z1, x2, y2, z2 = world_bounds
        
        for x, y, z, current_block in self.stream_blocks(x1, y1, z1, x2, y2, z2):
            if current_block and current_block.name() == block_name:
                if not block.properties or current_block.properties == block.properties:
                    positions.append((x, y, z))
                    if limit and len(positions) >= limit:
                        return positions
        
        return positions
    
    def find_nearest_block(self, block: Union[str, Block], x: int, y: int, z: int,
                          max_radius: int = 100) -> Optional[Tuple[int, int, int, float]]:
        """
        Find the nearest block of a specific type from given coordinates.
        
        Parameters
        ----------
        block : Union[str, Block]
            The block to find
        x, y, z : int
            Starting coordinates
        max_radius : int
            Maximum search radius in blocks (default: 100)
        
        Returns
        -------
        Optional[Tuple[int, int, int, float]]
            (x, y, z, distance) of nearest block, or None if not found
        
        Example
        -------
        >>> result = world.find_nearest_block("minecraft:diamond_ore", 100, 64, 200)
        >>> if result:
        ...     x, y, z, distance = result
        ...     print(f"Found at {x}, {y}, {z}, distance: {distance:.2f}")
        """
        if isinstance(block, str):
            block = Block.from_name(block)
        
        block_name = block.name()
        nearest = None
        min_distance = float('inf')
        
        bounds = (x - max_radius, y - max_radius, z - max_radius,
                 x + max_radius, y + max_radius, z + max_radius)
        
        for bx, by, bz, current_block in self.stream_blocks(*bounds):
            if current_block and current_block.name() == block_name:
                if not block.properties or current_block.properties == block.properties:
                    distance = math.sqrt((bx - x)**2 + (by - y)**2 + (bz - z)**2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest = (bx, by, bz, distance)
        
        return nearest
    
    def scan_area(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> Dict[str, int]:
        """
        Scan an area and return block type distribution.
        
        Parameters
        ----------
        x1, y1, z1 : int
            Minimum coordinates
        x2, y2, z2 : int
            Maximum coordinates
        
        Returns
        -------
        Dict[str, int]
            Dictionary mapping block names to their counts
        
        Example
        -------
        >>> distribution = world.scan_area(0, 60, 0, 16, 70, 16)
        >>> for block_name, count in distribution.items():
        ...     print(f"{block_name}: {count}")
        """
        distribution = {}
        
        for x, y, z, block in self.stream_blocks(x1, y1, z1, x2, y2, z2):
            if block:
                block_name = block.name()
                distribution[block_name] = distribution.get(block_name, 0) + 1
        
        return distribution
    
    
    def unload_region(self, region_x: int, region_z: int, save: bool = True) -> bool:
        """
        Unload a region from memory, optionally saving it first.
        
        Parameters
        ----------
        region_x : int
            Region X coordinate
        region_z : int
            Region Z coordinate
        save : bool
            Whether to save the region before unloading (default: True)
        
        Returns
        -------
        bool
            True if region was unloaded, False if it wasn't loaded
        
        Example
        -------
        >>> world.unload_region(0, 0, save=True)
        """
        region_coords = (region_x, region_z)
        
        if region_coords not in self.regions:
            return False
        
        if save:
            region = self.regions[region_coords]
            region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
            
            if isinstance(region, EmptyRegion):
                region.save(region_path)
            elif isinstance(region, Region):
                region.save(region_path)
        
        del self.regions[region_coords]
        
        if self._region_cache is not None:
            self._region_cache.invalidate(region_coords)
        
        return True
    
    def unload_all_regions(self, save: bool = True) -> int:
        """
        Unload all regions from memory.
        
        Parameters
        ----------
        save : bool
            Whether to save regions before unloading (default: True)
        
        Returns
        -------
        int
            Number of regions unloaded
        
        Example
        -------
        >>> count = world.unload_all_regions(save=True)
        >>> print(f"Unloaded {count} regions")
        """
        region_coords_list = list(self.regions.keys())
        count = 0
        
        for region_x, region_z in region_coords_list:
            if self.unload_region(region_x, region_z, save=save):
                count += 1
        
        return count
    
    def get_memory_usage(self) -> dict:
        """
        Get memory usage statistics for the world.
        
        Returns
        -------
        dict
            Dictionary with memory usage information
        
        Example
        -------
        >>> stats = world.get_memory_usage()
        >>> print(f"Loaded regions: {stats['loaded_regions']}")
        >>> print(f"Cached chunks: {stats['cached_chunks']}")
        """
        return {
            'loaded_regions': len(self.regions),
            'cached_chunks': len(self._chunk_cache) if self._chunk_cache else 0,
            'cached_regions': len(self._region_cache) if self._region_cache else 0,
            'cache_stats': self.get_cache_stats()
        }
    

    
    def get_world_info(self) -> dict:
        """
        Get general information about the world.
        
        Returns
        -------
        dict
            Dictionary with world information
        
        Example
        -------
        >>> info = world.get_world_info()
        >>> print(f"World folder: {info['world_folder']}")
        >>> print(f"Loaded regions: {info['loaded_regions']}")
        """
        bounds = self.get_world_bounds()
        
        return {
            'world_folder': self.world_folder,
            'loaded_regions': len(self.regions),
            'region_coordinates': list(self.regions.keys()),
            'bounds': bounds,
            'size_x': (bounds[3] - bounds[0] + 1) if bounds else 0,
            'size_z': (bounds[5] - bounds[2] + 1) if bounds else 0,
            'cache_enabled': self._chunk_cache is not None,
            'chunk_cache_size': self._chunk_cache.max_size if self._chunk_cache else 0,
            'region_cache_size': self._region_cache.max_size if self._region_cache else 0
        }
    
    def get_block_distribution(self, bounds: Optional[Tuple[int, int, int, int, int, int]] = None,
                               top_n: Optional[int] = None) -> Dict[str, int]:
        """
        Get the distribution of block types in the world or within bounds.
        
        Parameters
        ----------
        bounds : Optional[Tuple[int, int, int, int, int, int]]
            Bounding box as (min_x, min_y, min_z, max_x, max_y, max_z)
            If None, analyzes the entire loaded world
        top_n : Optional[int]
            Return only the top N most common blocks (None = all blocks)
        
        Returns
        -------
        Dict[str, int]
            Dictionary mapping block names to their counts, sorted by count
        
        Example
        -------
        >>> distribution = world.get_block_distribution(top_n=10)
        >>> for block_name, count in distribution.items():
        ...     print(f"{block_name}: {count}")
        """
        if bounds:
            x1, y1, z1, x2, y2, z2 = bounds
        else:
            world_bounds = self.get_world_bounds()
            if not world_bounds:
                return {}
            x1, y1, z1, x2, y2, z2 = world_bounds
        
        distribution = self.scan_area(x1, y1, z1, x2, y2, z2)
        
        # Sort by count (descending)
        sorted_distribution = dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
        
        if top_n:
            return dict(list(sorted_distribution.items())[:top_n])
        
        return sorted_distribution
    
    def get_height_map(self, x: int, z: int, start_y: int = 319, end_y: int = -64) -> Optional[int]:
        """
        Get the Y coordinate of the highest non-air block at given X, Z coordinates.
        
        Parameters
        ----------
        x : int
            Global X coordinate
        z : int
            Global Z coordinate
        start_y : int
            Y coordinate to start searching from (default: 319, world top)
        end_y : int
            Y coordinate to stop searching at (default: -64, world bottom)
        
        Returns
        -------
        Optional[int]
            Y coordinate of highest non-air block, or None if all air
        
        Example
        -------
        >>> height = world.get_height_map(100, 200)
        >>> print(f"Surface height at (100, 200): {height}")
        """
        step = 1 if end_y > start_y else -1
        
        for y in range(start_y, end_y + step, step):
            block = self.get_block(x, y, z)
            if block and block.name() != "minecraft:air":
                return y
        
        return None
    
    def create_structure(self, x: int, y: int, z: int, pattern: Structure) -> None:
        """
        Create a pattern file from a specified area in the world.
        
        Parameters
        ----------
        x1, y1, z1 : int
            Minimum coordinates of the area
        pattern_file : str
            Path to save the pattern file (JSON format)
        
        Example
        -------
        >>> world.create_pattern(0, 64, 0, 'pattern.json')
        """
        for block in pattern.blocks:
            palette_index = block[1]
            if not self.is_in_palette_section(pattern.palette[palette_index], block[0][0]+x, block[0][1]+y, block[0][2]+z):
                self.add_block_to_palette(pattern.palette[palette_index], block[0][0]+x, block[0][1]+y, block[0][2]+z)
        for block in self.blocks:
            palette_index = block[1]
            if palette_index >= len(self.palette):
                air_block = Block.from_name("minecraft:air")
                self.set_block(air_block, block[0][0]+x, block[0][1]+y, block[0][2]+z)
                continue
            self.set_block(pattern.palette[palette_index], block[0][0]+x, block[0][1]+y, block[0][2]+z)
        self.save()
    
    def copy_area(self, src_x1: int, src_y1: int, src_z1: int,
                  src_x2: int, src_y2: int, src_z2: int,
                  dest_x: int, dest_y: int, dest_z: int) -> int:
        """
        Copy blocks from one area to another within the world.
        
        Parameters
        ----------
        src_x1, src_y1, src_z1 : int
            Source area minimum coordinates
        src_x2, src_y2, src_z2 : int
            Source area maximum coordinates
        dest_x, dest_y, dest_z : int
            Destination starting coordinates
        
        Returns
        -------
        int
            Number of blocks copied
        
        Example
        -------
        >>> # Copy a 10x10x10 area
        >>> count = world.copy_area(0, 64, 0, 10, 74, 10, 100, 64, 100)
        >>> print(f"Copied {count} blocks")
        """
        count = 0
        offset_x = dest_x - src_x1
        offset_y = dest_y - src_y1
        offset_z = dest_z - src_z1
        
        for x, y, z, block in self.stream_blocks(src_x1, src_y1, src_z1, src_x2, src_y2, src_z2):
            if block:
                new_x = x + offset_x
                new_y = y + offset_y
                new_z = z + offset_z
                self.set_block(block, new_x, new_y, new_z)
                count += 1
        
        return count
    
    def fill_area(self, block: Union[str, Block],
                  x1: int, y1: int, z1: int,
                  x2: int, y2: int, z2: int) -> int:
        """
        Fill an area with a specific block type.
        
        Parameters
        ----------
        block : Union[str, Block]
            The block to fill with
        x1, y1, z1 : int
            Minimum coordinates
        x2, y2, z2 : int
            Maximum coordinates
        
        Returns
        -------
        int
            Number of blocks placed
        
        Example
        -------
        >>> # Fill a 10x10x10 cube with stone
        >>> count = world.fill_area("minecraft:stone", 0, 64, 0, 10, 74, 10)
        >>> print(f"Placed {count} blocks")
        """
        if isinstance(block, str):
            block = Block.from_name(block)
        
        count = 0
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        min_z, max_z = min(z1, z2), max(z1, z2)
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    self.set_block(block, x, y, z)
                    count += 1
        
        return count
    
    def clear_area(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> int:
        """
        Clear an area by filling it with air blocks.
        
        Parameters
        ----------
        x1, y1, z1 : int
            Minimum coordinates
        x2, y2, z2 : int
            Maximum coordinates
        
        Returns
        -------
        int
            Number of blocks cleared
        
        Example
        -------
        >>> count = world.clear_area(0, 64, 0, 10, 74, 10)
        >>> print(f"Cleared {count} blocks")
        """
        return self.fill_area("minecraft:air", x1, y1, z1, x2, y2, z2)
    
    def switch_dimension(self, dimension: str, save_current: bool = True) -> None:
        """
        Switch to a different dimension (overworld, nether, or end).
        
        Parameters
        ----------
        dimension : str
            Target dimension ('overworld', 'nether', or 'end')
        save_current : bool
            Whether to save the current dimension before switching (default: True)
        
        Example
        -------
        >>> world = World(r'C:\\path\\to\\world')
        >>> world.switch_dimension('nether')
        >>> world.switch_dimension('end', save_current=True)
        """
        if dimension not in self.DIMENSIONS:
            raise ValueError(f"Invalid dimension '{dimension}'. Must be one of: {list(self.DIMENSIONS.keys())}")
        
        if dimension == self.dimension:
            return
        
        if save_current:
            self.save()
        
        self.regions.clear()
        if self._chunk_cache:
            self._chunk_cache.clear()
        if self._region_cache:
            self._region_cache.clear()
        
        self.dimension = dimension
        self.region_dir = os.path.join(self.world_folder, self.DIMENSIONS[dimension])
        os.makedirs(self.region_dir, exist_ok=True)
    
    def get_dimension(self) -> str:
        """
        Get the current dimension.
        
        Returns
        -------
        str
            Current dimension name ('overworld', 'nether', or 'end')
        
        Example
        -------
        >>> dim = world.get_dimension()
        >>> print(f"Current dimension: {dim}")
        """
        return self.dimension
    
    def get_dimension_info(self) -> dict:
        """
        Get information about the current dimension.
        
        Returns
        -------
        dict
            Dictionary with dimension information
        
        Example
        -------
        >>> info = world.get_dimension_info()
        >>> print(f"Dimension: {info['name']}")
        >>> print(f"Path: {info['path']}")
        """
        return {
            'name': self.dimension,
            'path': self.DIMENSIONS[self.dimension],
            'full_path': self.region_dir,
            'loaded_regions': len(self.regions)
        }
    
    def get_chunk_data(self, chunk_x: int, chunk_z: int, mode: str = 'heightmap') -> Optional[dict]:
        """
        Get chunk data in different formats optimized for API/viewer consumption.
        Essential for the isometric viewer.
        
        Parameters
        ----------
        chunk_x : int
            Chunk X coordinate
        chunk_z : int
            Chunk Z coordinate
        mode : str
            Data format mode:
            - 'heightmap': Only heightmap (lightest, ~1KB)
            - 'surface': Surface blocks with biomes (~10-50KB)
            - 'simplified': Palette only (~5KB)
            - 'full': All chunk data (heaviest, ~500KB-2MB)
        
        Returns
        -------
        Optional[dict]
            Chunk data in requested format, or None if chunk not found
            
        Example
        -------
        >>> data = world.get_chunk_data(0, 0, mode='heightmap')
        >>> print(data['heightmap'])
        [[64, 65, 64, ...], ...]
        """
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            return None
        
        if mode == 'heightmap':
            return {
                'chunk_x': chunk_x,
                'chunk_z': chunk_z,
                'heightmap': chunk.to_heightmap()
            }
        elif mode == 'surface':
            return {
                'chunk_x': chunk_x,
                'chunk_z': chunk_z,
                'heightmap': chunk.to_heightmap(),
                'surface_blocks': chunk.get_surface_blocks(include_biome=True)
            }
        elif mode == 'simplified':
            return {
                'chunk_x': chunk_x,
                'chunk_z': chunk_z,
                **chunk.to_dict(simplify=True)
            }
        elif mode == 'full':
            return {
                'chunk_x': chunk_x,
                'chunk_z': chunk_z,
                **chunk.to_dict(simplify=False, include_blocks=True)
            }
        else:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'heightmap', 'surface', 'simplified', or 'full'")
    
    def get_area_heightmap(self, x1: int, z1: int, x2: int, z2: int) -> dict:
        """
        Get heightmap for an entire area (multiple chunks).
        Perfect for rendering large portions of the world in the isometric viewer.
        
        Parameters
        ----------
        x1, z1 : int
            Minimum coordinates (block coordinates)
        x2, z2 : int
            Maximum coordinates (block coordinates)
        
        Returns
        -------
        dict
            Dictionary with area heightmap data
            
        Example
        -------
        >>> heightmap = world.get_area_heightmap(0, 0, 64, 64)
        >>> print(heightmap['width'], heightmap['height'])
        65 65
        """
        min_x, min_z = min(x1, x2), min(z1, z2)
        max_x, max_z = max(x1, x2), max(z1, z2)
        
        width = max_x - min_x + 1
        height = max_z - min_z + 1
        
        heightmap = []
        for x in range(min_x, max_x + 1):
            row = []
            for z in range(min_z, max_z + 1):
                chunk_x = x >> 4
                chunk_z = z >> 4
                local_x = x & 15
                local_z = z & 15
                
                chunk = self.get_chunk(chunk_x, chunk_z)
                if chunk:
                    try:
                        h = chunk.get_surface_height(local_x, local_z)
                        row.append(h)
                    except:
                        row.append(-64)
                else:
                    row.append(-64)
            heightmap.append(row)
        
        return {
            'x1': min_x,
            'z1': min_z,
            'x2': max_x,
            'z2': max_z,
            'width': width,
            'height': height,
            'heightmap': heightmap
        }
    
    def get_tile_data(self, tile_x: int, tile_z: int, tile_size: int = 16) -> dict:
        """
        Get data for a tile-based rendering system.
        A tile is a square area of chunks (e.g., 16x16 chunks = 256x256 blocks).
        Optimized for progressive loading in the viewer.
        
        Parameters
        ----------
        tile_x : int
            Tile X coordinate
        tile_z : int
            Tile Z coordinate
        tile_size : int
            Number of chunks per tile side (default: 16)
        
        Returns
        -------
        dict
            Dictionary with tile data including all chunks in the tile
            
        Example
        -------
        >>> tile = world.get_tile_data(0, 0, tile_size=16)
        >>> print(f"Tile contains {len(tile['chunks'])} chunks")
        """
        start_chunk_x = tile_x * tile_size
        start_chunk_z = tile_z * tile_size
        
        chunks_data = []
        for cx in range(start_chunk_x, start_chunk_x + tile_size):
            for cz in range(start_chunk_z, start_chunk_z + tile_size):
                chunk_data = self.get_chunk_data(cx, cz, mode='surface')
                if chunk_data:
                    chunks_data.append(chunk_data)
        
        return {
            'tile_x': tile_x,
            'tile_z': tile_z,
            'tile_size': tile_size,
            'start_chunk_x': start_chunk_x,
            'start_chunk_z': start_chunk_z,
            'chunks': chunks_data,
            'chunk_count': len(chunks_data)
        }
    
    def get_world_info(self) -> dict:
        """
        Get comprehensive world information for the API/viewer.
        Includes bounds, dimension, loaded regions, cache stats, etc.
        
        Returns
        -------
        dict
            Dictionary with world metadata
            
        Example
        -------
        >>> info = world.get_world_info()
        >>> print(f"World dimension: {info['dimension']}")
        >>> print(f"Bounds: {info['bounds']}")
        """
        bounds = self.get_world_bounds()
        
        return {
            'dimension': self.dimension,
            'world_folder': self.world_folder,
            'region_dir': self.region_dir,
            'bounds': bounds,
            'loaded_regions': len(self.regions),
            'region_list': self.get_loaded_regions(),
            'cache_stats': self.get_cache_stats()
        }
