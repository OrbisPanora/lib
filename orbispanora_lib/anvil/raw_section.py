"""RawSection: a section whose palette and block index array are set directly."""

import array
from typing import Iterable, Optional, Sequence, cast

from nbt import nbt

from . import Block, EmptySection
from .utilities import pack_indices


class RawSection:
    """
    Same as :class:`EmptySection` but you manually
    set the palette and the blocks array (which instead
    of :class:`Block`, it's indexes on the palette)

    Attributes
    ----------
    y: :class:`int`
        Section's Y index
    blocks: Iterable[:class:`int`]
        Array of palette indexes
    _palette: Sequence[:class:`Block`]
        Section's palette
    """
    __slots__ = ('y', '_palette', 'blocks')
    def __init__(self, y: int, blocks: Iterable[int], palette: Sequence[Block]):
        self.y = y
        self.blocks: Iterable[int] = blocks
        self._palette: Sequence[Block] = palette

    def palette(self) -> Sequence[Block]:
        """Returns ``self._palette``"""
        return self._palette

    def blockstates(self, palette: Optional[Sequence[Block]]=None) -> array.array:
        """Refer to :class:`EmptySection.blockstates()`"""
        bits = max((len(self._palette) - 1).bit_length(), 4)
        return array.array('Q', pack_indices(list(self.blocks), bits))

    def save(self) -> nbt.TAG_Compound:
        """Refer to :class:`EmptySection.save()`"""
        # RawSection has the attributes that EmptySection.save() reads: y, palette() and blockstates().
        return EmptySection.save(cast(EmptySection, self))
