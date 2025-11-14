"""
Legacy block and biome mapping for pre-1.13 Minecraft versions.
Loads JSON mappings for numeric ID to namespaced ID conversion.
"""
import json
import os

with open(os.path.join(os.path.dirname(__file__), 'legacy_blocks.json'), 'r') as file:
    LEGACY_ID_MAP = json.load(file)

with open(os.path.join(os.path.dirname(__file__), 'legacy_biomes.json'), 'r') as file:
    LEGACY_BIOMES_ID_MAP = {int(k):v for k, v in json.load(file).items()}