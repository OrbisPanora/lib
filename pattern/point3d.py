from dataclasses import dataclass


@dataclass
class Point3D:
    """
    Represents a 3D point with integer coordinates.
    
    Attributes
    ----------
    x: int
        X coordinate
    y: int
        Y coordinate  
    z: int
        Z coordinate
    """
    x: int
    y: int
    z: int
    
    def __add__(self, other: 'Point3D') -> 'Point3D':
        """Add two points together."""
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Point3D') -> 'Point3D':
        """Subtract two points."""
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __str__(self) -> str:
        """String representation of the point."""
        return f"({self.x}, {self.y}, {self.z})"
