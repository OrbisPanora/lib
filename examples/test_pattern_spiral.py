from pattern import SpiralPattern, Point3D
import anvil

spiral = SpiralPattern(
    radius=10.0,
    height=30, 
    materials=[anvil.Block('minecraft', 'oak_log')],
    origin=Point3D(0, 60, 0)
)

world = anvil.World(world_path)
world.apply_pattern((100, 60, 100), spiral)
world.save()