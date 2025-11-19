from typing import Optional
from nbt import nbt
from anvil.versions import VERSION_17w47a


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

