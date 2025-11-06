import math
from typing import Iterator, Tuple, List
from .ipattern import IPattern
from .point3d import Point3D
from anvil.block import Block
from random import choice

class SpiralPattern(IPattern):
    """
    Pattern generator for spiral structures.
    
    Creates a 3D spiral using the specified materials.
    """
    
    def __init__(self, radius: float, height: int, materials: List[Block], origin: Point3D = None):
        """
        Initialize spiral pattern.
        
        Parameters
        ----------
        radius : float
            Radius of the spiral
        height : int
            Height of the spiral
        materials : List[Block]
            List of blocks to use for the spiral
        origin : Point3D, optional
            Origin point of the spiral, defaults to (0, 0, 0)
        """
        self.radius = radius
        self.height = height
        self.materials = materials
        self.origin = origin or Point3D(0, 0, 0)
    
    def generate(self) -> Iterator[Tuple[Point3D, Block]]:   
        """
        Generate the spiral pattern.
        
        Yields
        ------
        Tuple[Point3D, Block]
            Position and block pairs for the spiral
        """
        n_tours = 3  
        step = 5     
        
        k = self.height / (4 * math.pi * n_tours)
        
        for angle_deg in range(0, 360 * n_tours, step):
            theta = math.radians(angle_deg)
            
            x = self.radius * math.cos(theta)
            z = self.radius * math.sin(theta)
            y = k * theta
            
            point = Point3D(
                int(round(x)) + self.origin.x,
                int(round(y)) + self.origin.y,
                int(round(z)) + self.origin.z
            )
            
            block = choice(self.materials)
            
            yield point, block
