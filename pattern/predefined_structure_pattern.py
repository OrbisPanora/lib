from typing import Iterator, Tuple, List, Dict
from .ipattern import IPattern
from .point3d import Point3D
from anvil.block import Block

class PredefinedStructurePattern(IPattern):
    """
    Pattern generator for predefined structures.
    
    Creates structures from a predefined dictionary of positions and blocks.
    """
    
    def __init__(self, structure: Dict[Tuple[int, int, int], Block], origin: Point3D = None):
        """
        Initialize predefined structure pattern.
        
        Parameters
        ----------
        structure : Dict[Tuple[int, int, int], Block]
            Dictionary mapping relative coordinates to blocks
        origin : Point3D, optional
            Origin point of the structure, defaults to (0, 0, 0)
        """
        self.structure = structure
        self.origin = origin or Point3D(0, 0, 0)
    
    def generate(self) -> Iterator[Tuple[Point3D, Block]]:
        """
        Generate the predefined structure pattern.
        
        Yields
        ------
        Tuple[Point3D, Block]
            Position and block pairs for the structure
        """
        for (x, y, z), block in self.structure.items():
            point = Point3D(
                x + self.origin.x,
                y + self.origin.y,
                z + self.origin.z
            )
            yield point, block
    
    @classmethod
    def create_cube(cls, materials: List[Block], origin: Point3D, size: Tuple[int, int, int]) -> 'PredefinedStructurePattern':
        """
        Create a cube pattern.
        
        Parameters
        ----------
        materials : List[Block]
            List of blocks to use for the cube
        origin : Point3D
            Origin point of the cube
        size : Tuple[int, int, int]
            Size of the cube (width, height, depth)
            
        Returns
        -------
        PredefinedStructurePattern
            Cube pattern
        """
        from random import choice
        
        structure = {}
        width, height, depth = size
        
        for y in range(height):
            for z in range(depth):
                for x in range(width):
                    structure[(x, y, z)] = choice(materials)
        
        return cls(structure, origin)
