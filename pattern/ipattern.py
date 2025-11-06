from abc import ABC, abstractmethod
from typing import Iterator, Tuple
from .point3d import Point3D
from anvil.block import Block


class IPattern(ABC):
    """
    Interface for pattern generators.
    
    A pattern generates a sequence of (Point3D, Block) tuples that can be
    applied to a Minecraft world.
    """
    
    @abstractmethod
    def generate(self) -> Iterator[Tuple[Point3D, Block]]:
        """
        Generate the pattern as an iterator of (Point3D, Block) tuples.
        
        Returns
        -------
        Iterator[Tuple[Point3D, Block]]
            Iterator yielding position and block pairs
        """
        pass
