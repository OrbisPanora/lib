"""EmptySection: a 16x16x16 section of blocks built from scratch."""

import array
from struct import Struct
from typing import List, Optional, Tuple

from nbt import nbt

from . import Block
from .errors import OutOfBoundsCoordinates
from .utilities import pack_indices


# dirty mixin to change q to Q
def _update_fmt(self, length):
    self.fmt = Struct(f'>{length}Q')
nbt.TAG_Long_Array.update_fmt = _update_fmt

def bin_append(a, b, length=None):
    length = length or b.bit_length()
    return (a << length) | b


def block_index(x: int, y: int, z: int) -> int:
    """Calculate block index in 16x16x16 section."""
    return y * 256 + z * 16 + x


def validate_section_coords(x: int, y: int, z: int) -> None:
    """Validate coordinates are within section bounds (0-15)."""
    if not 0 <= x < 16:
        raise OutOfBoundsCoordinates(f'X ({x!r}) must be in range of 0 to 15')
    if not 0 <= y < 16:
        raise OutOfBoundsCoordinates(f'Y ({y!r}) must be in range of 0 to 15')
    if not 0 <= z < 16:
        raise OutOfBoundsCoordinates(f'Z ({z!r}) must be in range of 0 to 15')

class EmptySection:
    """
    Used for making own sections.

    This is where the blocks are actually stored, in a 16³ sized array.
    To save up some space, ``None`` is used instead of the air block object,
    and will be replaced with ``self.air`` when needed

    Attributes
    ----------
    y: :class:`int`
        Section's Y index
    blocks: List[:class:`Block`]
        1D list of blocks
    air: :class:`Block`
        An air block
    """
    __slots__ = ('y', 'blocks', 'air')
    def __init__(self, y: int):
        self.y = y
        # None is the same as an air block
        self.blocks: List[Optional[Block]] = [None] * 4096
        # Block that will be used when None
        self.air = Block('minecraft', 'air')

    @staticmethod
    def inside(x: int, y: int, z: int) -> bool:
        """
        Check if X Y and Z are in range of 0-15

        Parameters
        ----------
        int x, y, z
            Coordinates
        """
        return x in range(16) and y in range(16) and z in range(16)

    def set_block(self, block: Block, x: int, y: int, z: int):
        """
        Sets the block at given coordinates

        Parameters
        ----------
        block
            Block to set
        int x, y, z
            Coordinates

        Raises
        ------
        anvil.OutOfBoundsCoordinates
            If coordinates are not in range of 0-15
        """
        validate_section_coords(x, y, z)
        index = block_index(x, y, z)
        self.blocks[index] = block

    def get_block(self, x: int, y: int, z: int) -> Block:
        """
        Gets the block at given coordinates.

        Parameters
        ----------
        int x, y, z
            Coordinates

        Raises
        ------
        anvil.OutOfBoundsCoordinates
            If coordinates are not in range of 0-15
        """
        validate_section_coords(x, y, z)
        index = block_index(x, y, z)
        return self.blocks[index] or self.air

    def palette(self) -> Tuple[Block, ...]:
        """
        Generates and returns a tuple of all the different blocks in the section,
        in the order of their first appearance. Air comes with the first ``None``.
        """
        seen = {}
        for block in self.blocks:
            seen.setdefault(self.air if block is None else block)
        return tuple(seen)

    def blockstates(self, palette: Optional[Tuple[Block, ...]]=None) -> array.array:
        """
        Returns the packed palette index of each block, as stored in the ``data`` tag of
        the section: at least 4 bits per block, the first block in the lowest bits of the
        first long, and no block split between two longs (the layout of 20w17a and later).

        Parameters
        ----------
        palette
            Section's palette. If not given will generate one.
        """
        palette = palette or self.palette()
        palette_map = {block: idx for idx, block in enumerate(palette)}
        bits = max((len(palette) - 1).bit_length(), 4)
        indices = [palette_map[self.air if block is None else block] for block in self.blocks]
        return array.array('Q', pack_indices(indices, bits))

    def to_dict(self, simplify: bool = True) -> dict:
        """
        Convert the section to a dictionary for JSON serialization.

        Parameters
        ----------
        simplify : bool
            If True, only return palette and Y index (lightweight)
            If False, return all blocks (heavy, 4096 blocks)

        Returns
        -------
        dict
            Dictionary with section data in API-friendly format

        Example
        -------
        >>> section = EmptySection(y=4)
        >>> section.to_dict(simplify=True)
        {'y': 4, 'palette': ['minecraft:air']}
        """
        palette = self.palette()

        if simplify:
            return {
                'y': self.y,
                'palette': [block.name() for block in palette],
                'block_count': len([b for b in self.blocks if b is not None])
            }
        else:
            # Full mode: include all blocks (4096 blocks)
            blocks_data = []
            for i, block in enumerate(self.blocks):
                if block is not None:
                    x = i % 16
                    y = (i // 16) % 16
                    z = i // 256
                    blocks_data.append({
                        'x': x,
                        'y': y,
                        'z': z,
                        'block': block.to_dict()
                    })

            return {
                'y': self.y,
                'palette': [block.to_dict() for block in palette],
                'blocks': blocks_data
            }

    def save(self) -> nbt.TAG_Compound:
        """
        Saves the section to a TAG_Compound, in the layout of 1.18 and later, to be put in
        the ``sections`` list of a chunk. The ``biomes`` tag is added by the chunk. There is
        no light data; Minecraft calculates it when the chunk is loaded.
        """
        root = nbt.TAG_Compound()
        root.tags.append(nbt.TAG_Byte(name='Y', value=self.y))

        palette = self.palette()
        nbt_pal = nbt.TAG_List(name='palette', type=nbt.TAG_Compound)
        for block in palette:
            tag = nbt.TAG_Compound()
            tag.tags.append(nbt.TAG_String(name='Name', value=block.name()))
            if block.properties:
                properties = nbt.TAG_Compound()
                properties.name = 'Properties'
                for key, value in block.properties.items():
                    if isinstance(value, str):
                        properties.tags.append(nbt.TAG_String(name=key, value=value))
                    elif isinstance(value, bool):
                        # booleans are a string saved as either 'true' or 'false'
                        properties.tags.append(nbt.TAG_String(name=key, value=str(value).lower()))
                    elif isinstance(value, int):
                        # ints also seem to be saved as a string
                        properties.tags.append(nbt.TAG_String(name=key, value=str(value)))
                    else:
                        # assume its a nbt tag and just append it
                        properties.tags.append(value)
                tag.tags.append(properties)
            nbt_pal.tags.append(tag)

        block_states = nbt.TAG_Compound(name='block_states')
        block_states.tags.append(nbt_pal)
        # A section with one block type has no data array.
        if len(palette) > 1:
            data = nbt.TAG_Long_Array(name='data')
            data.value = self.blockstates(palette=palette)
            block_states.tags.append(data)
        root.tags.append(block_states)

        return root
