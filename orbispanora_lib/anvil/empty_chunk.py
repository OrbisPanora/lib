"""EmptyChunk: a chunk built from scratch, for writing new regions."""

from typing import TYPE_CHECKING, List, Optional, Union

from nbt import nbt

from .biome import Biome
from .block import Block
from .empty_section import EmptySection
from .errors import EmptySectionAlreadyExists, OutOfBoundsCoordinates
from .legacy import LEGACY_BIOMES_ID_MAP

if TYPE_CHECKING:
    from .raw_section import RawSection

# Constants for chunk dimensions
CHUNK_SIZE = 16
CHUNK_HEIGHT = 256
SECTION_HEIGHT = 16
BIOME_COUNT = 16 * 16


def validate_chunk_coords_xyz(x: int, z: int) -> None:
    """Validate chunk X and Z coordinates (0-15)."""
    if not 0 <= x < CHUNK_SIZE:
        raise OutOfBoundsCoordinates(f'X ({x!r}) must be in range of 0 to 15')
    if not 0 <= z < CHUNK_SIZE:
        raise OutOfBoundsCoordinates(f'Z ({z!r}) must be in range of 0 to 15')


def validate_chunk_coords_full(x: int, y: int, z: int) -> None:
    """Validate all chunk coordinates including Y (0-255)."""
    validate_chunk_coords_xyz(x, z)
    if not 0 <= y < CHUNK_HEIGHT:
        raise OutOfBoundsCoordinates(f'Y ({y!r}) must be in range of 0 to 255')


def biome_index(x: int, z: int) -> int:
    """Calculate biome index in chunk."""
    return z * CHUNK_SIZE + x


def _get_legacy_biome_id(biome: Biome) -> int:
    for k, v in LEGACY_BIOMES_ID_MAP.items():
        if v == biome.id:
            return k
    raise ValueError(f'Biome id "{biome.id}" has no legacy equivalent')


class EmptyChunk:
    """
    Used for making own chunks

    Attributes
    ----------
    x: :class:`int`
        Chunk's X position
    z: :class:`int`
        Chunk's Z position
    sections: List[:class:`anvil.EmptySection`]
        List of all the sections in this chunk
    version: :class:`int`
        Chunk's DataVersion
    """
    __slots__ = ('x', 'z', 'sections', 'biomes', 'version')
    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z
        self.sections: List[Union[EmptySection, 'RawSection', None]] = [None]*16
        self.biomes: List[Biome] = [Biome('ocean')]*16*16
        self.version = 3955 #1.21.1 DataVersion (https://minecraft.wiki/w/Java_Edition_1.21.1#:~:text=1.21.1%20is%20a%20minor%20hotfix%20update%20to,this%20version%20are%20compatible%20with%201.21%20clients.)

    def add_section(self, section: 'Union[EmptySection, RawSection]', replace: bool = True):
        """
        Adds a section to the chunk

        Parameters
        ----------
        section
            Section to add
        replace
            Whether to replace section if one at same Y already exists

        Raises
        ------
        anvil.EmptySectionAlreadyExists
            If ``replace`` is ``False`` and section with same Y already exists in this chunk
        """
        if self.sections[section.y] and not replace:
            raise EmptySectionAlreadyExists(f'EmptySection (Y={section.y}) already exists in this chunk')
        self.sections[section.y] = section

    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """
        Gets the block at given coordinates

        Parameters
        ----------
        int x, z
            In range of 0 to 15
        y
            In range of 0 to 255

        Raises
        ------
        anvil.OutOfBoundCoordidnates
            If X, Y or Z are not in the proper range

        Returns
        -------
        block : :class:`anvil.Block` or None
            Returns ``None`` if the section is empty, meaning the block
            is most likely an air block.
        """
        validate_chunk_coords_full(x, y, z)
        section = self.sections[y // SECTION_HEIGHT]
        if section is None:
            return None
        if not isinstance(section, EmptySection):
            raise TypeError('get_block is not supported on a RawSection')
        return section.get_block(x, y % SECTION_HEIGHT, z)

    def set_block(self, block: Block, x: int, y: int, z: int):
        """
        Sets block at given coordinates

        Parameters
        ----------
        int x, z
            In range of 0 to 15
        y
            In range of 0 to 255

        Raises
        ------
        anvil.OutOfBoundCoordidnates
            If X, Y or Z are not in the proper range
        """
        validate_chunk_coords_full(x, y, z)
        section = self.sections[y // SECTION_HEIGHT]
        if section is None:
            section = EmptySection(y // SECTION_HEIGHT)
            self.add_section(section)
        if not isinstance(section, EmptySection):
            raise TypeError('set_block is not supported on a RawSection')
        section.set_block(block, x, y % SECTION_HEIGHT, z)

    def set_biome(self, biome: Biome, x: int, z: int):
        """
        Sets biome at given coordinates

        Parameters
        ----------
        int x, z
            In range of 0 to 15

        Raises
        ------
        anvil.OutOfBoundCoordidnates
            If X or Z are not in the proper range

        """
        validate_chunk_coords_xyz(x, z)
        index = biome_index(x, z)
        self.biomes[index] = biome

    def replace_block_at(self, x: int, y: int, z: int, new_block: Union[str, Block]) -> bool:
        """
        Replace a single block at specific coordinates.

        Parameters
        ----------
        x : int
            X coordinate (0-15)
        y : int
            Global Y coordinate
        z : int
            Z coordinate (0-15)
        new_block : Union[str, Block]
            The replacement block

        Returns
        -------
        bool
            True if the block was replaced, False otherwise
        """
        try:
            if isinstance(new_block, str):
                new_block = Block.from_name(new_block)
            self.set_block(new_block, x, y, z)
            return True
        except OutOfBoundsCoordinates:
            return False

    def replace_blocks(self, old_block: Union[str, Block], new_block: Union[str, Block]) -> int:
        """
        Replace all occurrences of a specific block type with another block type in the chunk.

        Parameters
        ----------
        old_block : Union[str, Block]
            The block to replace
        new_block : Union[str, Block]
            The replacement block

        Returns
        -------
        int
            The number of blocks replaced
        """
        if isinstance(old_block, str):
            old_block = Block.from_name(old_block)
        if isinstance(new_block, str):
            new_block = Block.from_name(new_block)

        old_block_name = old_block.name()
        count = 0

        for section in self.sections:
            if section is None:
                continue
            section_y = section.y
            for local_y in range(16):
                global_y = section_y * 16 + local_y
                for x in range(16):
                    for z in range(16):
                        try:
                            current_block = self.get_block(x, global_y, z)
                            if current_block and current_block.name() == old_block_name:
                                if not old_block.properties or current_block.properties == old_block.properties:
                                    if self.replace_block_at(x, global_y, z, new_block):
                                        count += 1
                        except (IndexError, OutOfBoundsCoordinates):
                            continue

        return count

    def save(self) -> nbt.NBTFile:
        """
        Saves the chunk data to a :class:`NBTFile`

        Notes
        -----
        Does not contain most data a regular chunk would have,
        but minecraft stills accept it.
        """
        root = nbt.NBTFile()
        root.tags.append(nbt.TAG_Int(name='DataVersion',value=self.version))
        level = nbt.TAG_Compound()
        # Needs to be in a separate line because it just gets
        # ignored if you pass it as a kwarg in the constructor
        level.name = 'Level'
        level.tags.extend([
            nbt.TAG_List(name='Entities', type=nbt.TAG_Compound),
            nbt.TAG_List(name='TileEntities', type=nbt.TAG_Compound),
            nbt.TAG_List(name='LiquidTicks', type=nbt.TAG_Compound),
            nbt.TAG_Int(name='xPos', value=self.x),
            nbt.TAG_Int(name='zPos', value=self.z),
            nbt.TAG_Long(name='LastUpdate', value=0),
            nbt.TAG_Long(name='InhabitedTime', value=0),
            nbt.TAG_Byte(name='isLightOn', value=1),
            nbt.TAG_String(name='Status', value='full')
        ])
        sections = nbt.TAG_List(name='Sections', type=nbt.TAG_Compound)
        biomes = nbt.TAG_Int_Array(name='Biomes')

        biomes.value = [_get_legacy_biome_id(biome) for biome in self.biomes]
        for s in self.sections:
            if s:
                p = s.palette()
                # Minecraft does not save sections that are just air
                # So we can just skip them
                if len(p) == 1 and p[0].name() == 'minecraft:air':
                    continue
                sections.tags.append(s.save())
        level.tags.append(sections)
        level.tags.append(biomes)
        root.tags.append(level)
        return root
