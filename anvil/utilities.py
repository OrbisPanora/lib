from typing import Optional, TYPE_CHECKING
from nbt import nbt
from anvil.versions import VERSION_17w47a
if TYPE_CHECKING:
    from anvil.block import Block

def bin_append(a, b, length=None):
    """
    Appends number a to the left of b.

    Parameters
    ----------
    a : int
        Number to append on the left
    b : int
        Base number
    length : int, optional
        Bit length to use for shifting. If None, uses b.bit_length()

    Returns
    -------
    int
        Combined number with a appended to the left of b

    Examples
    --------
    >>> bin_append(0b1, 0b10)
    0b110
    """
    length = length or b.bit_length()
    return (a << length) | b


def nibble(byte_array, index):
    """
    Extract a nibble (4 bits) from a byte array at given index.

    Parameters
    ----------
    byte_array : array-like
        Array of bytes to extract nibble from
    index : int
        Index of the nibble to extract

    Returns
    -------
    int
        The nibble value (0-15)
    """
    value = byte_array[index // 2]
    if index % 2:
        return value >> 4
    else:
        return value & 0b1111


def palette_from_section(section: nbt.TAG_Compound) -> nbt.TAG_List:
    """
    Extract the block palette from a section NBT tag.

    Parameters
    ----------
    section : nbt.TAG_Compound
        The section NBT compound to extract palette from

    Returns
    -------
    nbt.TAG_List
        The palette list containing block definitions
    """
    if 'block_states' in section:
        return section["block_states"]["palette"]
    else:
        return section["Palette"]


def states_from_section(section: nbt.TAG_Compound) -> list:
    """
    Extract block states array from a section NBT tag.

    BlockStates is an array of 64 bit numbers that holds the blocks index on the palette list.
    Makes sure the number is unsigned by adding 2^64 if negative.

    Parameters
    ----------
    section : nbt.TAG_Compound
        The section NBT compound to extract states from

    Returns
    -------
    list
        List of unsigned 64-bit integers representing block states
    """
    if 'block_states' in section:
        states = section['block_states']['data']
    else:
        states = section['BlockStates']

    return [state if state >= 0 else states + 2 ** 64
        for state in states.value]

def calculate_blockstates_size(bits: int) -> int:
    """
    Calculate the number of longs needed for the given bits per block.

    Minecraft requires each Y-level's data to be aligned, with some padding.

    Parameters
    ----------
    bits : int
        Number of bits per block

    Returns
    -------
    int
        Number of longs needed to store all block states
    """
    # Calculate longs needed for one Y-level (16x16 blocks)
    bits_per_layer = 16 * 16 * bits
    base_longs_per_layer = (bits_per_layer + 63) // 64  # ceil division
    # Add padding (1/16 extra for alignment)
    padded_longs_per_layer = (base_longs_per_layer * 17 + 15) // 16  # ceil(base * 1.0625)
    # Multiply by 16 Y-levels
    total_longs = padded_longs_per_layer * 16
    return total_longs


def section_height_range(version: Optional[int]) -> range:
    """
    Get the valid section height range for a given Minecraft version.

    Parameters
    ----------
    version : int, optional
        Minecraft data version number

    Returns
    -------
    range
        Range object representing valid section Y indices
        (range(-4, 20) for modern versions, range(16) for older versions)
    """
    if version > VERSION_17w47a:
        return range(-4, 20)
    else:
        return range(16)

def get_air_block_index(palette: nbt.TAG_List) -> int:
    """
    Get the index of the air block in the palette, or 0 if not found.

    Parameters
    ----------
    palette : nbt.TAG_List
        The palette to search in

    Returns
    -------
    int
        The index of the air block, or 0 if not found
    """
    for i, entry in enumerate(palette):
        if entry['Name'].value == 'minecraft:air':
            return i
    return 0


def calculate_states_count(bits: int) -> int:
    """
    Calculate the number of longs needed to store all blocks in a section.
    In versions >= 20w17a, each long must contain a whole number of blocks.

    Parameters
    ----------
    bits : int
        Number of bits per block

    Returns
    -------
    int
        Number of longs needed to store all blocks
    """
    blocks_per_long = 64 // bits  # Integer division - number of complete blocks per long
    total_blocks = 16 * 16 * 16  # 4096 blocks per section
    return (total_blocks + blocks_per_long - 1) // blocks_per_long


def get_block_index_from_section(section: nbt.TAG_Compound, x: int, y: int, z: int) -> int | None:
    """
    Return the palette index of the block at (x,y,z) in a section, or None if empty.

    Parameters
    ----------
    section : nbt.TAG_Compound
        The section to read from
    x : int
        X coordinate within section (0-15)
    y : int
        Y coordinate within section (0-15)
    z : int
        Z coordinate within section (0-15)

    Returns
    -------
    int or None
        The palette index of the block, or None if section is empty
    """
    if 'block_states' in section:
        blockstates_tag = section['block_states']
        data = None
        if 'data' in blockstates_tag:
            data = blockstates_tag['data'].value
        elif hasattr(blockstates_tag, 'value'):
            data = blockstates_tag.value
    elif 'BlockStates' in section:
        blockstates_tag = section['BlockStates']
        data = getattr(blockstates_tag, 'value', None)
    else:
        return None

    if data is None:
        return None

    palette = palette_from_section(section)
    bits = max((len(palette) - 1).bit_length(), 4)

    index = y * 256 + z * 16 + x
    bit_pos = index * bits
    long_idx = bit_pos // 64
    long_off = bit_pos % 64

    if long_idx >= len(data):
        return None

    mask = (1 << bits) - 1
    val = (data[long_idx] >> long_off) & mask

    # handle spill
    spill = long_off + bits - 64
    if spill > 0 and long_idx + 1 < len(data):
        val |= (data[long_idx + 1] & ((1 << spill) - 1)) << (bits - spill)

    return val


def props_match(nbt_props, block_props: dict) -> bool:
    """
    Check if properties match.

    Parameters
    ----------
    nbt_props : nbt.TAG_Compound or None
        NBT properties from a palette entry
    block_props : dict
        Block properties to compare

    Returns
    -------
    bool
        True if properties match, False otherwise
    """
    if not nbt_props and not block_props:
        return True
    if not nbt_props or not block_props:
        return False
    for k, v in block_props.items():
        if k not in nbt_props or nbt_props[k].value != str(v):
            return False
    return True


def _create_biomes_in_section(section: nbt.TAG_Compound) -> None:
    """
    Create biomes structure in a section.

    Parameters
    ----------
    section : nbt.TAG_Compound
        The section to add biomes to

    Returns
    -------
    None
    """
    biomes = nbt.TAG_Compound(name='biomes')
    palette = nbt.TAG_List(name='palette', type=nbt.TAG_String)
    palette.tags.append(nbt.TAG_String(value='minecraft:plains'))
    biomes.tags.append(palette)
    section.tags.append(biomes)


def resize_biome_data_array(old_data: list, old_bits: int, new_bits: int) -> list:
    """
    Resize the biome data array when palette size changes.

    Extracts palette indices from old bit size and repackages them with new bit size.

    Parameters
    ----------
    old_data : list
        The old biome data array
    old_bits : int
        Previous number of bits per biome
    new_bits : int
        New number of bits per biome

    Returns
    -------
    list
        The resized biome data array
    """
    # Extract all 64 palette indices from the old data array
    indices = []
    for i in range(64):
        # Calculate which long and bit offset for old format
        bit_index = i * old_bits
        state_idx = bit_index // 64
        offset = bit_index % 64

        if state_idx < len(old_data):
            mask = (1 << old_bits) - 1
            # Check if the value spans two longs
            if offset + old_bits <= 64:
                palette_idx = (old_data[state_idx] >> offset) & mask
            else:
                # Value spans two longs
                bits_in_first = 64 - offset
                first_part = (old_data[state_idx] >> offset) & ((1 << bits_in_first) - 1)
                if state_idx + 1 < len(old_data):
                    bits_in_second = old_bits - bits_in_first
                    second_part = old_data[state_idx + 1] & ((1 << bits_in_second) - 1)
                    palette_idx = first_part | (second_part << bits_in_first)
                else:
                    palette_idx = first_part
            indices.append(palette_idx)
        else:
            indices.append(0)

    # Repack indices with new bit size
    total_bits = 64 * new_bits
    states_count = (total_bits + 63) // 64
    new_data = [0] * states_count

    for i, palette_idx in enumerate(indices):
        # Calculate which long and bit offset for new format
        bit_index = i * new_bits
        state_idx = bit_index // 64
        offset = bit_index % 64

        if state_idx < len(new_data):
            mask = (1 << new_bits) - 1
            # Check if the value spans two longs
            if offset + new_bits <= 64:
                new_data[state_idx] |= (palette_idx & mask) << offset
            else:
                # Value spans two longs
                bits_in_first = 64 - offset
                first_part = palette_idx & ((1 << bits_in_first) - 1)
                new_data[state_idx] |= first_part << offset
                if state_idx + 1 < len(new_data):
                    bits_in_second = new_bits - bits_in_first
                    second_part = (palette_idx >> bits_in_first) & ((1 << bits_in_second) - 1)
                    new_data[state_idx + 1] |= second_part

    return new_data


def set_biome_in_section_data(biomes_data: nbt.TAG_Compound,
                               palette_index: int, x: int, y: int, z: int) -> None:
    """
    Set biome index in section data array.

    Handles palette optimization: when only one biome type exists, removes the data array.
    When multiple biomes exist, creates/resizes the data array as needed.

    Parameters
    ----------
    biomes_data : nbt.TAG_Compound
        The biomes NBT compound
    palette_index : int
        The index in the biome palette
    x : int
        X coordinate within chunk (0-15)
    y : int
        Y coordinate within section (0-15)
    z : int
        Z coordinate within chunk (0-15)

    Returns
    -------
    None
    """
    palette = biomes_data['palette']

    # If palette has only one biome and we're setting to index 0, no data array needed
    if len(palette) == 1 and palette_index == 0:
        # Remove data array if it exists (optimization for uniform biomes)
        if 'data' in biomes_data:
            for i, tag in enumerate(biomes_data.tags):
                if tag.name == 'data':
                    del biomes_data.tags[i]
                    break
        return

    # Calculate position in the biome array (4x4x4 blocks per biome)
    index = (y // 4) * 16 + (z // 4) * 4 + (x // 4)

    new_bits = max((len(palette) - 1).bit_length(), 1)

    # Check if we need to resize the data array due to palette growth
    if 'data' in biomes_data:
        old_bits = max((len(palette) - 2).bit_length(), 1) if len(palette) > 1 else 1
        if new_bits != old_bits:
            # Palette grew and needs more bits, so we need to resize the data array
            old_data = biomes_data['data'].value
            new_data = resize_biome_data_array(old_data, old_bits, new_bits)
            biomes_data['data'].value = new_data

    # Create data array if it doesn't exist
    if 'data' not in biomes_data:
        total_bits = 64 * new_bits  # 64 biome positions (4x4x4 volume)
        states_count = (total_bits + 63) // 64
        data_array = nbt.TAG_Long_Array(name='data')
        # Initialize all positions to 0 (first palette entry)
        data_array.value = [0] * states_count
        biomes_data.tags.append(data_array)

    data = biomes_data['data'].value

    # Calculate which long and bit offset
    bit_index = index * new_bits
    state_idx = bit_index // 64
    offset = bit_index % 64

    # Ensure data array is large enough
    required_size = state_idx + 1
    if offset + new_bits > 64:
        required_size = state_idx + 2

    if len(data) < required_size:
        # Create new properly sized array
        new_data = list(data) + [0] * (required_size - len(data))
        biomes_data['data'].value = new_data
        data = new_data

    mask = (1 << new_bits) - 1

    # Check if the value spans two longs
    if offset + new_bits <= 64:
        # Value fits in one long
        data[state_idx] &= ~(mask << offset)
        data[state_idx] |= (palette_index & mask) << offset
    else:
        # Value spans two longs - split across boundary
        bits_in_first = 64 - offset
        bits_in_second = new_bits - bits_in_first

        # Clear and set first part
        first_mask = (1 << bits_in_first) - 1
        data[state_idx] &= ~(first_mask << offset)
        data[state_idx] |= ((palette_index & first_mask) << offset)

        # Clear and set second part
        second_mask = (1 << bits_in_second) - 1
        data[state_idx + 1] &= ~second_mask
        data[state_idx + 1] |= ((palette_index >> bits_in_first) & second_mask)


def is_block_in_palette(palette: nbt.TAG_List, block: 'Block') -> bool:
    """
    Check if a block is already in the palette.

    Parameters
    ----------
    palette : nbt.TAG_List
        The palette to search in
    block : Block
        The block to search for

    Returns
    -------
    bool
        True if the block is in the palette, False otherwise
    """
    for entry in palette:
        if entry.name() == block.name():
            if props_match(entry.properties, block.properties):
                return True
    return False


