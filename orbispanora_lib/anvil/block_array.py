"""Decoding the blocks of a whole chunk into one numpy array.

``Chunk.get_block`` finds the section, rebuilds the list of stored values and allocates a
``Block`` on every call, about 7 microseconds each. A caller that needs many blocks of the same
chunk (the surface of all 256 columns, for example) is faster with :func:`decode_chunk_blocks`,
which unpacks every section once with array operations.

numpy is an optional dependency: ``pip install orbispanora-lib[fast]``.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from .utilities import palette_from_section, read_packed_index, section_height_range, states_from_section
from .versions import VERSION_17w47a, VERSION_20w17a

if TYPE_CHECKING:
    from .chunk import Chunk

AIR = "minecraft:air"
#: Blocks per side of a section.
SECTION_SIZE = 16
#: Blocks in a section.
SECTION_BLOCKS = SECTION_SIZE ** 3


@dataclass(frozen=True)
class ChunkBlocks:
    """
    The blocks of one chunk as a palette and an array of palette indices.

    Attributes
    ----------
    names
        Block names with their namespace, for example ``minecraft:stone``. ``names[0]`` is always
        ``minecraft:air``. Block properties (facing, waterlogged, ...) are not kept: two blocks that
        differ only in their properties have the same index.
    indices
        ``uint16`` array of shape ``(height, 16, 16)``, indexed ``[y - min_y][z][x]``, with x and z
        the position inside the chunk. A section that is missing from the chunk is filled with air.
    min_y
        The y of the first layer of ``indices``: -64 for 1.18 and later, 0 for older versions.
    """

    names: Tuple[str, ...]
    indices: Any
    min_y: int

    @property
    def height(self) -> int:
        """Number of layers of ``indices``."""
        return int(self.indices.shape[0])

    def name_at(self, x: int, y: int, z: int) -> str:
        """
        Name of the block at a position of the chunk.

        Parameters
        ----------
        x, z
            Position inside the chunk, 0 to 15.
        y
            Absolute height, from ``min_y`` up to ``min_y + height - 1``.
        """
        return self.names[int(self.indices[y - self.min_y, z, x])]


def _numpy() -> Any:
    """Import numpy, with a message that says which extra to install."""
    try:
        import numpy  # pylint: disable=import-outside-toplevel
    except ImportError as error:
        raise ImportError(
            "Decoding a chunk into an array needs numpy. Install it with: pip install orbispanora-lib[fast]"
        ) from error
    return numpy


def _section_data(section: Any) -> Any:
    """The ``data`` long array of a flattened section, or ``None`` if the section has none."""
    try:
        if "block_states" in section:
            return section["block_states"]["data"].value
        return section["BlockStates"].value
    except KeyError:
        return None


def _unpack(np: Any, data: List[int], bits: int, stretches: bool, section: Any) -> Any:
    """The 4096 palette indices of a section, in the order y, z, x."""
    if stretches:
        # Before 20w17a a block may span two longs. This is slower and only used by old worlds.
        states = states_from_section(section)
        return np.array([read_packed_index(states, i, bits, True) for i in range(SECTION_BLOCKS)], dtype=np.intp)
    per_long = 64 // bits
    try:
        longs = np.array(data, dtype=np.uint64)
    except OverflowError:
        # Some NBT readers give the longs as signed values.
        longs = np.array([value & 0xFFFFFFFFFFFFFFFF for value in data], dtype=np.uint64)
    shifts = np.arange(per_long, dtype=np.uint64) * np.uint64(bits)
    values = (longs[:, None] >> shifts) & np.uint64((1 << bits) - 1)
    return values.ravel()[:SECTION_BLOCKS].astype(np.intp)


def _legacy_section(np: Any, chunk: "Chunk", section: Any, name_id: Any) -> Any:
    """A section of a world from before 1.13, read block by block through ``Chunk.get_block``."""
    layer = np.zeros((SECTION_SIZE, SECTION_SIZE, SECTION_SIZE), dtype=np.uint16)
    for y in range(SECTION_SIZE):
        for z in range(SECTION_SIZE):
            for x in range(SECTION_SIZE):
                layer[y, z, x] = name_id(chunk.get_block(x, y, z, section, force_new=True).name())
    return layer


def decode_chunk_blocks(chunk: "Chunk") -> ChunkBlocks:
    """
    Decode the blocks of a whole chunk into a :class:`ChunkBlocks`.

    Parameters
    ----------
    chunk
        A chunk read from a region file.

    Raises
    ------
    ImportError
        If numpy is not installed.
    """
    np = _numpy()
    version = chunk.version
    section_range = section_height_range(version)
    names: List[str] = [AIR]
    name_ids: Dict[str, int] = {AIR: 0}

    def name_id(name: str) -> int:
        found = name_ids.get(name)
        if found is None:
            found = name_ids[name] = len(names)
            names.append(name)
        return found

    indices = np.zeros((len(section_range) * SECTION_SIZE, SECTION_SIZE, SECTION_SIZE), dtype=np.uint16)
    for section_y in section_range:
        section = chunk.get_section(section_y)
        if section is None:
            continue
        first = (section_y - section_range.start) * SECTION_SIZE
        layer = indices[first:first + SECTION_SIZE]

        if version <= VERSION_17w47a:
            layer[:] = _legacy_section(np, chunk, section, name_id)
            continue

        try:
            palette = [entry["Name"].value for entry in palette_from_section(section)]
        except KeyError:
            continue
        if not palette:
            continue
        lookup = np.array([name_id(name) for name in palette], dtype=np.uint16)
        data = _section_data(section)
        if data is None:
            # Minecraft leaves the array out when the palette has one entry: the whole section is that block.
            if lookup[0]:
                layer[:] = lookup[0]
            continue
        bits = max((len(palette) - 1).bit_length(), 4)
        raw = _unpack(np, data, bits, version < VERSION_20w17a, section)
        layer[:] = lookup[raw].reshape(SECTION_SIZE, SECTION_SIZE, SECTION_SIZE)

    return ChunkBlocks(names=tuple(names), indices=indices, min_y=section_range.start * SECTION_SIZE)
