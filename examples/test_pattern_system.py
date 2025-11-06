import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anvil
from pattern.spiral_pattern import SpiralPattern
from pattern.point3d import Point3D


def main():
    # Create or load a world
    world_path = 'C:/Users/ssim9/AppData/Roaming/.minecraft/saves/testop'
    world = anvil.World(world_path)
    
    # Create materials for the spiral
    materials = [
        anvil.Block('minecraft', 'oak_log'),
        anvil.Block('minecraft', 'birch_log'),
        anvil.Block('minecraft', 'spruce_log')
    ]
    
    # Create a spiral pattern
    spiral = SpiralPattern(
        radius=10.0,
        height=30,
        materials=materials,
        origin=Point3D(0, 60, 0)  # Center of spiral
    )
    
    # Apply the pattern at world coordinates (100, 60, 100)
    world.apply_pattern((100, 60, 100), spiral)
    
    # Save the world
    world.save()
    print("Spiral pattern applied successfully!")


if __name__ == "__main__":
    main()
