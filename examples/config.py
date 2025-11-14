"""
Configuration file for all example scripts.
Modify the WORLD_PATH variable to point to your Minecraft world.

This allows all examples to use the same world path without having to modify each file individually.
"""

import os

# =============================================================================
# WORLD CONFIGURATION
# =============================================================================

# Path to your Minecraft world
# Examples:
#   Windows: r'C:\Users\YourName\AppData\Roaming\.minecraft\saves\YourWorld'
#   Linux/Mac: '/home/username/.minecraft/saves/YourWorld'
WORLD_PATH = r'your_world_path_here'

# Alternative: Use environment variable
# Uncomment the line below to use an environment variable instead
# WORLD_PATH = os.environ.get('MINECRAFT_WORLD_PATH', WORLD_PATH)

# =============================================================================
# VALIDATION
# =============================================================================

def validate_world_path(path: str = None) -> tuple[bool, str]:
    """
    Validate that the world path exists and contains a region folder.
    
    Args:
        path: Path to validate. If None, uses WORLD_PATH.
    
    Returns:
        Tuple of (is_valid, message)
    """
    if path is None:
        path = WORLD_PATH
    
    if path == 'your_world_path_here' or path == 'yourpath' or path == 'your_path':
        return False, "Please configure WORLD_PATH in examples/config.py"
    
    if not os.path.exists(path):
        return False, f"World path does not exist: {path}"
    
    region_folder = os.path.join(path, "region")
    if not os.path.exists(region_folder):
        return False, f"Region folder not found. Is this a valid Minecraft world? {path}"
    
    return True, f"Valid world path: {path}"


def get_world_path() -> str:
    """
    Get the configured world path.
    
    Returns:
        The configured world path.
    
    Raises:
        ValueError: If the world path is not configured or invalid.
    """
    is_valid, message = validate_world_path()
    if not is_valid:
        raise ValueError(message)
    return WORLD_PATH


def print_config_info():
    """Print configuration information."""
    print("=" * 60)
    print("CONFIGURATION INFO")
    print("=" * 60)
    print(f"World path: {WORLD_PATH}")
    is_valid, message = validate_world_path()
    print(f"Status: {'✓ Valid' if is_valid else '✗ Invalid'}")
    print(f"Message: {message}")
    print("=" * 60)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    """
    Run this file directly to test your configuration:
        python config.py
    """
    print_config_info()
    
    if WORLD_PATH in ['your_world_path_here', 'yourpath', 'your_path']:
        print("\n⚠ CONFIGURATION NEEDED ⚠")
        print("\nPlease edit examples/config.py and set WORLD_PATH to your Minecraft world.")
        print("\nExamples:")
        print("  Windows: WORLD_PATH = r'C:\\Users\\YourName\\AppData\\Roaming\\.minecraft\\saves\\YourWorld'")
        print("  Linux:   WORLD_PATH = '/home/username/.minecraft/saves/YourWorld'")
        print("  Mac:     WORLD_PATH = '/Users/username/Library/Application Support/minecraft/saves/YourWorld'")
    else:
        is_valid, message = validate_world_path()
        if is_valid:
            print("\n✓ Configuration is valid! You can now run the example scripts.")
        else:
            print(f"\n✗ Configuration error: {message}")
