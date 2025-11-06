import _path
import anvil
import os
from pattern import Point3D, SpiralPattern, PredefinedStructurePattern


def modify_existing_mca():
    """Modifie le fichier r.0.0.mca existant avec des patterns."""
    print("🔧 Modification du fichier r.0.0.mca existant")
    print("=" * 50)
    
    # Chemin vers le fichier MCA existant
    mca_file = "r.0.0.mca"
    
    if not os.path.exists(mca_file):
        print(f"❌ Erreur : Le fichier {mca_file} n'existe pas!")
        return
    
    print(f"✅ Fichier {mca_file} trouvé")
    
    # Charger la région depuis le fichier MCA
    try:
        region = anvil.Region.from_file(mca_file)
        print(f"✅ Région chargée depuis {mca_file}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la région : {e}")
        return
    
    # Créer un monde temporaire pour utiliser les méthodes existantes
    world = anvil.World('temp_modify_mca')
    
    # Remplacer la région (0,0) par notre région chargée
    world.regions[(0, 0)] = region
    
    print("🏗️ Application des patterns sur la région existante...")
    
    # 1. Ajouter une spirale près du spawn
    print("\n🌀 Création d'une spirale...")
    spiral_materials = [
        anvil.Block('minecraft', 'gold_block'),
        anvil.Block('minecraft', 'diamond_block'),
        anvil.Block('minecraft', 'emerald_block')
    ]
    
    spiral = SpiralPattern(
        radius=8.0,
        height=20,
        materials=spiral_materials,
        origin=Point3D(0, 0, 0)
    )
    
    # Appliquer la spirale aux coordonnées (50, 70, 50)
    world.apply_pattern((50, 70, 50), spiral)
    
    # 2. Ajouter un cube de matériaux précieux
    print("\n💎 Création d'un cube précieux...")
    precious_materials = [
        anvil.Block('minecraft', 'diamond_block'),
        anvil.Block('minecraft', 'gold_block'),
        anvil.Block('minecraft', 'iron_block')
    ]
    
    cube = PredefinedStructurePattern.create_cube(
        materials=precious_materials,
        origin=Point3D(0, 0, 0),
        size=(7, 7, 7)
    )
    
    # Appliquer le cube aux coordonnées (100, 65, 100)
    world.apply_pattern((100, 65, 100), cube)
    
    # 3. Ajouter une petite tour
    print("\n🏰 Création d'une tour...")
    tower_structure = {}
    
    # Base de la tour (3x3)
    for x in range(3):
        for z in range(3):
            tower_structure[(x, 0, z)] = anvil.Block('minecraft', 'stone_bricks')
    
    # Murs de la tour (3x4)
    for y in range(1, 5):
        for x in range(3):
            tower_structure[(x, y, 0)] = anvil.Block('minecraft', 'stone_bricks')
            tower_structure[(x, y, 2)] = anvil.Block('minecraft', 'stone_bricks')
        for z in range(3):
            tower_structure[(0, y, z)] = anvil.Block('minecraft', 'stone_bricks')
            tower_structure[(2, y, z)] = anvil.Block('minecraft', 'stone_bricks')
    
    # Toit de la tour
    for x in range(3):
        for z in range(3):
            tower_structure[(x, 5, z)] = anvil.Block('minecraft', 'oak_stairs')
    
    # Créer le pattern de la tour
    tower = PredefinedStructurePattern(
        structure=tower_structure,
        origin=Point3D(0, 0, 0)
    )
    
    # Appliquer la tour aux coordonnées (150, 64, 150)
    world.apply_pattern((150, 64, 150), tower)
    
    # 4. Ajouter un panneau de bienvenue
    print("\n📋 Création d'un panneau de bienvenue...")
    welcome_structure = {
        (0, 0, 0): anvil.Block('minecraft', 'oak_sign'),
        (1, 0, 0): anvil.Block('minecraft', 'oak_sign'),
        (2, 0, 0): anvil.Block('minecraft', 'oak_sign'),
    }
    
    welcome = PredefinedStructurePattern(
        structure=welcome_structure,
        origin=Point3D(0, 0, 0)
    )
    
    # Appliquer le panneau aux coordonnées (200, 70, 200)
    world.apply_pattern((200, 70, 200), welcome)
    
    # Sauvegarder les modifications dans le fichier MCA d'origine
    print("\n💾 Sauvegarde des modifications...")
    try:
        # Utiliser la nouvelle méthode save() de Region
        region.save(mca_file)
        print(f"✅ Modifications sauvegardées dans {mca_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        return
    
    print("\n🎉 Modification du fichier MCA terminée avec succès!")
    print("\nStructures ajoutées :")
    print("   🌀 Spirale précieuse aux coordonnées (50, 70, 50)")
    print("   💎 Cube 7x7x7 aux coordonnées (100, 65, 100)")
    print("   🏰 Tour 3x3x5 aux coordonnées (150, 64, 150)")
    print("   📋 Panneau aux coordonnées (200, 70, 200)")
    
    print(f"\n📁 Le fichier {mca_file} a été modifié sur place.")
    print("   Tu peux maintenant copier ce fichier dans ton monde Minecraft!")


def main():
    """Fonction principale."""
    modify_existing_mca()


if __name__ == "__main__":
    main()
