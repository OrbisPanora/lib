import os
from typing import Dict, Tuple, Union, Optional
import math
from .region import Region
from .empty_region import EmptyRegion
from .chunk import Chunk
from .empty_chunk import EmptyChunk
from .block import Block
from .biome import Biome
from .errors import OutOfBoundsCoordinates
from pattern.point3d import Point3D

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
                # Convert to EmptyRegion as a fallback
                empty_region = EmptyRegion(region_x, region_z)
                
                # Try to copy existing chunks
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
    

    def apply(self, dictionary) -> None:
        """
        Apply the given dictionary of changes to the world.
        """
        for k, v in dictionary.items():
            print(f"Setting block {v} at {k}")
            self.set_block(v, k[0], k[1], k[2])

    def apply_pattern(self, origin, pattern) -> None:
        """
        Apply a pattern to the world at the specified origin.
        
        Parameters
        ----------
        origin: Tuple[int, int, int]
            Origin point (x, y, z) where to apply the pattern
        pattern: IPattern
            Pattern to apply
        """
        if not isinstance(origin, Point3D):
            origin = Point3D(origin[0], origin[1], origin[2])
        
        for point, block in pattern.generate():
            world_point = origin + point
            self.set_block(block, world_point.x, world_point.y, world_point.z)

    def save(self) -> None:
        """
        Save all modified regions to disk.
        """
        for (region_x, region_z), region in self.regions.items():
            if isinstance(region, EmptyRegion):
                region_path = os.path.join(self.region_dir, f"r.{region_x}.{region_z}.mca")
                region.save(region_path)
