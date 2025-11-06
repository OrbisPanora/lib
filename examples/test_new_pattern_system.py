import _path
import anvil
from pattern import Point3D, SpiralPattern, PredefinedStructurePattern


def test_spiral_pattern():
    """Test the new SpiralPattern system."""
    print("🌀 Test du nouveau système SpiralPattern")
    print("=" * 50)
    
    # Create a world
    world = anvil.World('test_spiral_pattern')
    
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
        origin=Point3D(0, 0, 0)
    )
    
    # Apply the spiral pattern at world coordinates (100, 64, 100)
    world.apply_pattern((100, 64, 100), spiral)
    
    # Save the world
    world.save()
    print("✅ Spiral pattern applied successfully!")


def test_cube_pattern():
    """Test the new PredefinedStructurePattern with cube."""
    print("\n🧪 Test du nouveau système PredefinedStructurePattern (Cube)")
    print("=" * 60)
    
    # Create a world
    world = anvil.World('test_cube_pattern')
    
    # Create materials for the cube
    materials = [
        anvil.Block('minecraft', 'stone'),
        anvil.Block('minecraft', 'cobblestone'),
        anvil.Block('minecraft', 'dirt')
    ]
    
    # Create a cube pattern using the factory method
    cube = PredefinedStructurePattern.create_cube(
        materials=materials,
        origin=Point3D(0, 0, 0),
        size=(5, 5, 5)
    )
    
    # Apply the cube pattern at world coordinates (200, 64, 200)
    world.apply_pattern((200, 64, 200), cube)
    
    # Save the world
    world.save()
    print("✅ Cube pattern applied successfully!")


def test_custom_structure():
    """Test creating a custom predefined structure."""
    print("\n🏗️ Test d'une structure personnalisée")
    print("=" * 40)
    
    # Create a world
    world = anvil.World('test_custom_structure')
    
    # Create a simple house structure
    house_structure = {
        # Floor
        (0, 0, 0): anvil.Block('minecraft', 'oak_planks'),
        (1, 0, 0): anvil.Block('minecraft', 'oak_planks'),
        (0, 0, 1): anvil.Block('minecraft', 'oak_planks'),
        (1, 0, 1): anvil.Block('minecraft', 'oak_planks'),
        
        # Walls
        (0, 1, 0): anvil.Block('minecraft', 'oak_log'),
        (1, 1, 0): anvil.Block('minecraft', 'oak_log'),
        (0, 1, 1): anvil.Block('minecraft', 'oak_log'),
        (1, 1, 1): anvil.Block('minecraft', 'oak_log'),
        
        # Roof
        (0, 2, 0): anvil.Block('minecraft', 'oak_stairs'),
        (1, 2, 0): anvil.Block('minecraft', 'oak_stairs'),
        (0, 2, 1): anvil.Block('minecraft', 'oak_stairs'),
        (1, 2, 1): anvil.Block('minecraft', 'oak_stairs'),
    }
    
    # Create the pattern
    house = PredefinedStructurePattern(
        structure=house_structure,
        origin=Point3D(0, 0, 0)
    )
    
    # Apply the house pattern at world coordinates (300, 64, 300)
    world.apply_pattern((300, 64, 300), house)
    
    # Save the world
    world.save()
    print("✅ Custom structure applied successfully!")


def main():
    """Main function to test all pattern systems."""
    print("🎨 Test du nouveau système de Patterns")
    print("=" * 50)
    
    try:
        test_spiral_pattern()
        test_cube_pattern()
        test_custom_structure()
        
        print("\n🎉 Tous les tests ont réussi !")
        print("Mondes créés :")
        print("   - test_spiral_pattern")
        print("   - test_cube_pattern")
        print("   - test_custom_structure")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
