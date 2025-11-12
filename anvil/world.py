import os
from typing import Dict, Tuple, Union, Optional, List
import math
from .region import Region
from .empty_region import EmptyRegion
from .chunk import Chunk
from .empty_chunk import EmptyChunk
from .block import Block
from .biome import Biome
from .errors import OutOfBoundsCoordinates


class World:
    """
    Represents a Minecraft world, managing multiple regions.
    
    Attributes
    ----------
    world_folder: str
        Path to the world folder
    regions: Dict[Tuple[int, int], Region]
        Dictionary of loaded regions, with region coordinates as keys
    """
    
    def __init__(self, world_folder: str):
        """
        Initialize a World object.
        
        Parameters
        ----------
        world_folder: str
            Path to the world folder
        """
        self.world_folder = world_folder
        self.regions: Dict[Tuple[int, int], Union[Region, EmptyRegion]] = {}
        
        self.region_dir = os.path.join(world_folder, "region")
        os.makedirs(self.region_dir, exist_ok=True)
    
    def get_region(self, region_x: int, region_z: int) -> Union[Region, EmptyRegion]:
        """
        Get a region at the specified coordinates.
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
        
        if region_coords in self.regions:
            return self.regions[region_coords]
        
        region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
        if os.path.exists(region_path):
            region = Region.from_file(region_path)
            self.regions[region_coords] = region
            return region
        
        empty_region = EmptyRegion(region_x, region_z)
        self.regions[region_coords] = empty_region
        return empty_region
    
    def get_chunk(self, chunk_x: int, chunk_z: int) -> Union[Chunk, EmptyChunk, None]:
        """
        Get a chunk at the specified coordinates.
        
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
        region_x = chunk_x >> 5 
        region_z = chunk_z >> 5  
        
        region = self.get_region(region_x, region_z)
        
        if isinstance(region, Region):
            try:
                return region.get_chunk(chunk_x % 32, chunk_z % 32)
            except:
                return None
        elif isinstance(region, EmptyRegion):
            return region.get_chunk(chunk_x, chunk_z)
        
        return None
    
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
        region_x = x >> 9  # x >> 9  <≡>  x // 512
        region_z = z >> 9  # z >> 9  <≡>  z // 512

        region = self.get_region(region_x, region_z)
        try:
            if isinstance(region, Region):
                region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
                region.set_block(block, x, y, z, region_path)
            else:
                region.set_block(block, x, y, z)
        except Exception as e:
            if isinstance(region, Region):
                empty_region = EmptyRegion(region_x, region_z)
                
                for cx in range(32):
                    for cz in range(32):
                        try:
                            chunk = region.get_chunk(cx, cz)
                            if chunk:
                                empty_region.add_chunk(chunk)
                        except:
                            pass
                
                self.regions[(region_x, region_z)] = empty_region
                empty_region.set_block(block, x, y, z)

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
        Get the bounds of the loaded world based on existing region files.
        
        Returns
        -------
        Optional[Tuple[int, int, int, int, int, int]]
            (min_x, min_y, min_z, max_x, max_y, max_z) or None if no regions are loaded
            Note: Only X and Z bounds are accurate, Y bounds are set to Minecraft world limits
        """
        if not self.regions:
            return None
        
        min_x = min_z = float('inf')
        max_x = max_z = float('-inf')
        
        for region_x, region_z in self.regions.keys():
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
            If None, counts blocks in the entire loaded world
        
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
            world_bounds = self.get_world_bounds()
            if world_bounds:
                min_x, min_y, min_z, max_x, max_y, max_z = world_bounds
                for x, y, z, current_block in self.stream_blocks(min_x, min_y, min_z, max_x, max_y, max_z):
                    if current_block is not None and current_block.name() == block_name:
                        if not block.properties or current_block.properties == block.properties:
                            count += 1
        
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
                # Sauvegarder les EmptyRegion
                region.save(region_path)
            elif isinstance(region, Region):
                # Sauvegarder les Region normales
                region.save(region_path)
