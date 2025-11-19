from typing import Union, Tuple, Generator, Optional
from nbt import nbt
from .biome import Biome
from .block import Block, OldBlock
from .region import Region
from .errors import OutOfBoundsCoordinates, ChunkNotFound
from .versions import VERSION_21w43a, VERSION_20w17a, VERSION_19w36a, VERSION_17w47a, VERSION_PRE_15w32a
from utilities import bin_append, nibble, palette_from_section, states_from_section, section_height_range


class Chunk:
    """
    Represents a chunk from a ``.mca`` file.

    Note that this is read only.

    Attributes
    ----------
    x: :class:`int`
        Chunk's X position
    z: :class:`int`
        Chunk's Z position
    version: :class:`int`
        Version of the chunk NBT structure
    data: :class:`nbt.TAG_Compound`
        Raw NBT data of the chunk
    tile_entities: :class:`nbt.TAG_Compound`
        ``self.data['TileEntities']`` as an attribute for easier use
    """

    __slots__ = ("version", "data", "x", "z", "tile_entities")

    def __init__(self, nbt_data: nbt.NBTFile):
        """
        Initialize a Chunk object from NBT data.

        Parameters
        ----------
        nbt_data : nbt.NBTFile
            The NBT data containing chunk information
        """
        try:
            self.version = nbt_data["DataVersion"].value
        except KeyError:
            # Version is pre-1.9 snapshot 15w32a, so world does not have a Data Version.
            # See https://minecraft.wiki/w/Data_version
            self.version = VERSION_PRE_15w32a

        if self.version >= VERSION_21w43a:
            self.data = nbt_data
            self.tile_entities = self.data["block_entities"]
        else:
            self.data = nbt_data["Level"]
            self.tile_entities = self.data["TileEntities"]
        self.x = self.data["xPos"].value
        self.z = self.data["zPos"].value

    def get_section(self, y: int) -> nbt.TAG_Compound:
        """
        Returns the section at given y index
        can also return nothing if section is missing, aka it's empty

        Parameters
        ----------
        y
            Section Y index

        Raises
        ------
        anvil.OutOfBoundsCoordinates
            If Y is not in range of 0 to 15
        """
        section_range = section_height_range(self.version)
        if y not in section_range:
            raise OutOfBoundsCoordinates(f"Y ({y!r}) must be in range of "
                f"{section_range.start} to {section_range.stop}")

        if 'sections' in self.data:
            sections = self.data["sections"]
        else:
            try:
                sections = self.data["Sections"]
            except KeyError:
                return None

        for section in sections:
            if section["Y"].value == y:
                return section

    def get_palette(self, section: Union[int, nbt.TAG_Compound]) -> Tuple[Block]:
        """
        Returns the block palette for given section

        Parameters
        ----------
        section
            Either a section NBT tag or an index


        :rtype: Tuple[:class:`anvil.Block`]
        """
        if isinstance(section, int):
            section = self.get_section(section)
        if section is None:
            return
        palette = palette_from_section(section)
        return tuple(Block.from_palette(i) for i in palette)

    def get_biome(self, x: int, y: int, z: int) -> Biome:
        """
        Returns the biome in the given coordinates

        Parameters
        ----------
        int x, y, z
            Biome's coordinates in the chunk

        Raises
        ------
        anvil.OutOfBoundCoordidnates
            If X, Y or Z are not in the proper range

        :rtype: :class:`anvil.Biome`
        """
        section_range = section_height_range(self.version)
        if x not in range(16):
            raise OutOfBoundsCoordinates(f"X ({x!r}) must be in range of 0 to 15")
        if z not in range(16):
            raise OutOfBoundsCoordinates(f"Z ({z!r}) must be in range of 0 to 15")
        if y // 16 not in section_range:
            raise OutOfBoundsCoordinates(f"Y ({y!r}) must be in range of "
                f"{section_range.start * 16} to {section_range.stop * 16 - 1}")
        
        if 'Biomes' not in self.data:
            # Each biome index refers to a 4x4x4 volumes here so we do integer division by 4
            section = self.get_section(y // 16)
            biomes = section['biomes']
            biomes_palette = biomes['palette']
            if 'data' in biomes:
                biomes = biomes['data']
            else:
                # When there is only one biome in the section of the palette 'data'
                # is not present
                return Biome.from_name(biomes_palette[0].value)


            index = ((y % 16) // 4) * 16 + (z // 4) * 4 + (x // 4)
            bits = (len(biomes_palette) - 1).bit_length()
            state = index * bits // 64
            data = biomes[state]

            # shift the number to the right to remove the left over bits
            # and shift so the i'th biome is the first one
            shifted_data = data >> ((bits * index) % 64)

            # if there aren't enough bits it means the rest are in the next number
            if 64 - ((bits * index) % 64) < bits:
                data = biomes[state + 1]

                # get how many bits are from a palette index of the next biome
                leftover = (bits - ((state + 1) * 64 % bits)) % bits

                # Make sure to keep the length of the bits in the first state
                # Example: bits is 5, and leftover is 3
                # Next state                Current state (already shifted)
                # 0b101010110101101010010   0b01
                # will result in bin_append(0b010, 0b01, 2) = 0b01001
                shifted_data = bin_append(
                    data & 2**leftover - 1, shifted_data, bits - leftover
                )

            palette_id = shifted_data & 2**bits - 1
            return Biome.from_name(biomes_palette[palette_id].value)

        else:
            biomes = self.data["Biomes"]
            if self.version < VERSION_19w36a:
                # Each biome index refers to a column stored Z then X.
                index = z * 16 + x
            else:
                # https://minecraft.wiki/w/Java_Edition_19w36a
                # Get index on the biome list with the order YZX
                # Each biome index refers to a 4x4 areas here so we do integer division by 4
                index = (y // 4) * 4 * 4 + (z // 4) * 4 + (x // 4)
            biome_id = biomes[index]
            return Biome.from_numeric_id(biome_id)

    def get_block(
        self,
        x: int,
        y: int,
        z: int,
        section: Union[int, nbt.TAG_Compound] = None,
        force_new: bool = False,
    ) -> Union[Block, OldBlock]:
        """
        Returns the block in the given coordinates

        Parameters
        ----------
        int x, y, z
            Block's coordinates in the chunk
        section : int
            Either a section NBT tag or an index. If no section is given,
            assume Y is global and use it for getting the section.
        force_new
            Always returns an instance of Block if True, otherwise returns type OldBlock for pre-1.13 versions.
            Defaults to False

        Raises
        ------
        anvil.OutOfBoundCoordidnates
            If X, Y or Z are not in the proper range

        :rtype: :class:`anvil.Block`
        """
        if x not in range(16):
            raise OutOfBoundsCoordinates(f"X ({x!r}) must be in range of 0 to 15")
        if z not in range(16):
            raise OutOfBoundsCoordinates(f"Z ({z!r}) must be in range of 0 to 15")
        section_range = section_height_range(self.version)
        if y // 16 not in section_range:
            raise OutOfBoundsCoordinates(f"Y ({y!r}) must be in range of "
                f"{section_range.start * 16} to {section_range.stop * 16 - 1}")

        if section is None:
            section = self.get_section(y // 16)
            # global Y to section Y
            y %= 16

        if self.version < VERSION_17w47a:
            # Explained in depth here https://minecraft.wiki/w/index.php?title=Chunk_format&oldid=1153403#Block_format

            if section is None or "Blocks" not in section:
                if force_new:
                    return Block.from_name("minecraft:air")
                else:
                    return OldBlock(0)

            index = y * 16 * 16 + z * 16 + x

            block_id = section["Blocks"][index]
            if "Add" in section:
                block_id += nibble(section["Add"], index) << 8

            block_data = nibble(section["Data"], index)

            block = OldBlock(block_id, block_data)
            if force_new:
                return block.convert()
            else:
                return block

        # If its an empty section its most likely an air block
        if section is None:
            return Block.from_name("minecraft:air")
        try:
            states = states_from_section(section)
        except KeyError:
            return Block.from_name("minecraft:air")
            
        # Number of bits each block is on BlockStates
        # Cannot be lower than 4
        palette = palette_from_section(section)

        bits = max((len(palette) - 1).bit_length(), 4)

        # Get index on the block list with the order YZX
        index = y * 16 * 16 + z * 16 + x
        # in 20w17a and newer blocks cannot occupy more than one element on the BlockStates array
        stretches = self.version < VERSION_20w17a

        # get location in the BlockStates array via the index
        if stretches:
            state = index * bits // 64
        else:
            state = index // (64 // bits)

        data = states[state]

        if stretches:
            # shift the number to the right to remove the left over bits
            # and shift so the i'th block is the first one
            shifted_data = data >> ((bits * index) % 64)
        else:
            shifted_data = data >> (index % (64 // bits) * bits)

        # if there aren't enough bits it means the rest are in the next number
        if stretches and 64 - ((bits * index) % 64) < bits:
            data = states[state + 1]

            # get how many bits are from a palette index of the next block
            leftover = (bits - ((state + 1) * 64 % bits)) % bits

            # Make sure to keep the length of the bits in the first state
            # Example: bits is 5, and leftover is 3
            # Next state                Current state (already shifted)
            # 0b101010110101101010010   0b01
            # will result in bin_append(0b010, 0b01, 2) = 0b01001
            shifted_data = bin_append(
                data & 2**leftover - 1, shifted_data, bits - leftover
            )

        # get `bits` least significant bits
        # which are the palette index
        palette_id = shifted_data & 2**bits - 1
        return Block.from_palette(palette[palette_id])

    def stream_blocks(
        self,
        index: int = 0,
        section: Union[int, nbt.TAG_Compound] = None,
        force_new: bool = False,
    ) -> Generator[Block, None, None]:
        """
        Returns a generator for all the blocks in given section

        Parameters
        ----------
        index
            At what block to start from.

            To get an index from (x, y, z), simply do:

            ``y * 256 + z * 16 + x``
        section
            Either a Y index or a section NBT tag.
        force_new
            Always returns an instance of Block if True, otherwise returns type OldBlock for pre-1.13 versions.
            Defaults to False

        Raises
        ------
        anvil.OutOfBoundCoordidnates
            If `section` is not in the range of 0 to 15

        Yields
        ------
        :class:`anvil.Block`
        """

        if isinstance(section, int):
            section_range = section_height_range(self.version)
            if section not in section_range:
                raise OutOfBoundsCoordinates(f"section ({section!r}) must be in range of "
                    f"{section_range.start} to {section_range.stop}")

        # For better understanding of this code, read get_block()'s source

        if section is None or isinstance(section, int):
            section = self.get_section(section or 0)

        if self.version < VERSION_17w47a:
            if section is None or "Blocks" not in section:
                air = Block.from_name("minecraft:air") if force_new else OldBlock(0)
                for _ in range(4096):
                    yield air
                return

            while index < 4096:
                block_id = section["Blocks"][index]
                if "Add" in section:
                    block_id += nibble(section["Add"], index) << 8

                block_data = nibble(section["Data"], index)

                block = OldBlock(block_id, block_data)
                if force_new:
                    yield block.convert()
                else:
                    yield block

                index += 1
            return

        air = Block.from_name("minecraft:air")
        if section is None:
            for _ in range(4096):
                yield air
            return
        try:
            states = states_from_section(section)
        except KeyError:
            for _ in range(4096):
                yield air
            return

        palette = palette_from_section(section)
        bits = max((len(palette) - 1).bit_length(), 4)

        stretches = self.version < VERSION_20w17a

        if stretches:
            state = index * bits // 64
        else:
            state = index // (64 // bits)

        data = states[state]

        bits_mask = 2**bits - 1

        if stretches:
            offset = (bits * index) % 64
        else:
            offset = index % (64 // bits) * bits

        data_len = 64 - offset
        data >>= offset

        while index < 4096:
            if data_len < bits:
                state += 1
                new_data = states[state]

                if stretches:
                    leftover = data_len
                    data_len += 64

                    data = bin_append(new_data, data, leftover)
                else:
                    data = new_data
                    data_len = 64

            palette_id = data & bits_mask
            yield Block.from_palette(palette[palette_id])

            index += 1
            data >>= bits
            data_len -= bits

    def stream_chunk(
        self, index: int = 0, section: Union[int, nbt.TAG_Compound] = None
    ) -> Generator[Block, None, None]:
        """
        Returns a generator for all the blocks in the chunk

        This is a helper function that runs Chunk.stream_blocks from section 0 to 15

        Yields
        ------
        :class:`anvil.Block`
        """
        for section in section_height_range(self.version):
            for block in self.stream_blocks(section=section):
                yield block

    def to_dict(self, simplify: bool = True, include_blocks: bool = False) -> dict:
        """
        Convert the chunk to a dictionary for JSON serialization (API-friendly).
        
        Parameters
        ----------
        simplify : bool
            If True, only return metadata and palette (lightweight)
            If False, include section details
        include_blocks : bool
            If True, include all blocks (very heavy, ~500KB-2MB per chunk)
            Only used when simplify=False
        
        Returns
        -------
        dict
            Dictionary with chunk data in API-friendly format
            
        Example
        -------
        >>> chunk = region.get_chunk(0, 0)
        >>> chunk.to_dict(simplify=True)
        {'x': 0, 'z': 0, 'version': 3465, 'sections': [...]}
        """
        data = {
            'x': self.x,
            'z': self.z,
            'version': self.version
        }
        
        if simplify:
            # Lightweight mode: only palette per section with data array
            sections_data = []
            section_range = section_height_range(self.version)
            
            for y in section_range:
                section = self.get_section(y)
                if section is None:
                    continue
                    
                palette = self.get_palette(section)
                if not palette:
                    continue
                    
                data_array = []
                if 'block_states' in section:
                    block_states = section['block_states']
                    if 'data' in block_states:
                        states = block_states['data'].value
                        data_array = [int(state) if state >= 0 else int(state + 2**64) for state in states]
                elif 'BlockStates' in section:
                    states = section['BlockStates'].value
                    data_array = [int(state) if state >= 0 else int(state + 2**64) for state in states]
                
                section_dict = {
                    'y': y,
                    'data': data_array,
                    'palette': [block.name() for block in palette]
                }
                sections_data.append(section_dict)
            data['sections'] = sections_data
            
        else:
            # Full mode: detailed section data
            sections_data = []
            section_range = section_height_range(self.version)
            for y in section_range:
                section = self.get_section(y)
                if section is not None:
                    palette = self.get_palette(section)
                    if palette:
                        section_dict = {
                            'y': y,
                            'palette': [block.to_dict() for block in palette]
                        }
                        
                        if include_blocks:
                            # Include all 4096 blocks (very slow!)
                            blocks_list = []
                            for local_y in range(16):
                                for local_z in range(16):
                                    for local_x in range(16):
                                        try:
                                            block = self.get_block(local_x, y * 16 + local_y, local_z)
                                            if block and block.name() != 'minecraft:air':
                                                blocks_list.append({
                                                    'x': local_x,
                                                    'y': local_y,
                                                    'z': local_z,
                                                    'block': block.to_dict()
                                                })
                                        except:
                                            pass
                            section_dict['blocks'] = blocks_list
                        
                        sections_data.append(section_dict)
            data['sections'] = sections_data
        
        return data

    def get_surface_height(self, x: int, z: int) -> int:
        """
        Get the Y coordinate of the highest non-air block at given X, Z coordinates.
        Essential for isometric 2.5D rendering.
        
        Parameters
        ----------
        x : int
            X coordinate within chunk (0-15)
        z : int
            Z coordinate within chunk (0-15)
        
        Returns
        -------
        int
            Y coordinate of the surface block, or -64 if no block found
            
        Example
        -------
        >>> chunk = region.get_chunk(0, 0)
        >>> height = chunk.get_surface_height(8, 8)
        >>> print(f"Surface at Y={height}")
        """
        if x not in range(16) or z not in range(16):
            raise OutOfBoundsCoordinates(f"X and Z must be in range 0-15, got X={x}, Z={z}")
        
        section_range = section_height_range(self.version)
        for y in range(section_range.stop * 16 - 1, section_range.start * 16 - 1, -1):
            try:
                block = self.get_block(x, y, z)
                if block and block.name() != 'minecraft:air':
                    return y
            except:
                continue
        
        return section_range.start * 16  

    def to_heightmap(self) -> list:
        """
        Generate a 16x16 heightmap grid for the chunk.
        Perfect for 2.5D isometric rendering.
        
        Returns
        -------
        list
            2D list (16x16) of surface heights
            
        Example
        -------
        >>> chunk = region.get_chunk(0, 0)
        >>> heightmap = chunk.to_heightmap()
        >>> print(heightmap[0][0])  # Height at X=0, Z=0
        64
        """
        heightmap = []
        for x in range(16):
            row = []
            for z in range(16):
                height = self.get_surface_height(x, z)
                row.append(height)
            heightmap.append(row)
        return heightmap

    def get_surface_blocks(self, include_biome: bool = False) -> list:
        """
        Get only the visible surface blocks (top-most non-air blocks).
        Optimized for isometric rendering - much lighter than full chunk data.
        
        Parameters
        ----------
        include_biome : bool
            If True, include biome information for each block
        
        Returns
        -------
        list
            List of dictionaries with surface block data
            
        Example
        -------
        >>> chunk = region.get_chunk(0, 0)
        >>> surface = chunk.get_surface_blocks(include_biome=True)
        >>> print(surface[0])
        {'x': 0, 'y': 64, 'z': 0, 'block': 'minecraft:grass_block', 'biome': 'plains'}
        """
        surface_blocks = []
        
        for x in range(16):
            for z in range(16):
                y = self.get_surface_height(x, z)
                try:
                    block = self.get_block(x, y, z)
                    if block:
                        block_data = {
                            'x': x,
                            'y': y,
                            'z': z,
                            'block': block.name()
                        }
                        
                        if include_biome:
                            try:
                                biome = self.get_biome(x, y, z)
                                if biome:
                                    block_data['biome'] = biome.name()
                            except:
                                block_data['biome'] = None
                        
                        surface_blocks.append(block_data)
                except:
                    continue
        
        return surface_blocks

    # Block modification methods
    def set_block(self, block: Block, x: int, y: int, z: int) -> None:
        """
        Sets a block at given coordinates in the chunk.
        Optimized for Minecraft 1.21.1 only.
        
        Parameters
        ----------
        block : Block
            The block to set
        int x, z
            In range of 0 to 15
        int y
            Global Y coordinate
            
        Raises
        ------
        OutOfBoundsCoordinates
            If coordinates are out of bounds
        """
        # Need Optimisation
        if not (0 <= x < 16):
            raise OutOfBoundsCoordinates(f"X ({x!r}) must be in range of 0 to 15")
        if not (0 <= z < 16):
            raise OutOfBoundsCoordinates(f"Z ({z!r}) must be in range of 0 to 15")
        
        section_range = section_height_range(self.version)
        section_y = y // 16
        if section_y not in section_range:
            raise OutOfBoundsCoordinates(f"Y ({y!r}) must be in range of "
                f"{section_range.start * 16} to {section_range.stop * 16 - 1}")
        
        section = self.get_section(section_y)
        if section is None:
            section = self._create_section(section_y)
        
        local_y = y % 16
        self._set_block_in_section(section, block, x, local_y, z)
    
    def set_palette_in_section(self, section: nbt.TAG_Compound, palette: nbt.TAG_List) -> None:
        """Set the palette in a section directly."""
        old_palette = self.get_palette(section)
        if len(old_palette) != len(palette):
            raise ValueError("New palette must have the same length as the old palette.")
        if 'block_states' not in section:
            section.tags.append(nbt.TAG_Compound(name='block_states'))
        block_states = section['block_states']

        block_states.tags = [tag for tag in block_states.tags if tag.name != 'palette']
        
        block_states['palette'] = palette

    def _add_block_to_palette(self, section: nbt.TAG_Compound, block: Block) -> int:
        """
        Add a block to the palette and return its index.

        Parameters
        ----------
        section : nbt.TAG_Compound
            The section to add the block to
        block : Block
            The block to add to the palette

        Returns
        -------
        int
            The palette index of the newly added block
        """
        block_states = section['block_states']
        palette = block_states['palette']
        new_entry = nbt.TAG_Compound()
        new_entry.tags.append(nbt.TAG_String(name='Name', value=block.name()))
        if block.properties:
            props = nbt.TAG_Compound(name='Properties')
            for k, v in block.properties.items():
                props.tags.append(nbt.TAG_String(name=k, value=str(v)))
            new_entry.tags.append(props)
        palette.tags.append(new_entry)
        old_bits = max((len(palette) - 2).bit_length(), 4) if len(palette) > 1 else 4
        new_bits = max((len(palette) - 1).bit_length(), 4)
        if old_bits != new_bits:
            self._recalculate_blockstates_bits(section, old_bits, new_bits)
        return len(palette) - 1
    
    def _is_block_in_palette(self, palette: nbt.TAG_List, block: Block) -> bool:
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
                if self._props_match(entry.properties, block.properties):
                    return True
        return False
    
    def _create_section(self, section_y: int) -> nbt.TAG_Compound:
        """
        Create a new empty section.

        Parameters
        ----------
        section_y : int
            The Y index of the section to create

        Returns
        -------
        nbt.TAG_Compound
            The newly created section NBT compound
        """
        section = nbt.TAG_Compound()
        section.tags.append(nbt.TAG_Byte(name='Y', value=section_y))
        
        # Create initial palette with air block
        palette = nbt.TAG_List(name='Palette', type=nbt.TAG_Compound)
        air = nbt.TAG_Compound()
        air.tags.append(nbt.TAG_String(name='Name', value='minecraft:air'))
        palette.tags.append(air)
        section.tags.append(palette)
        
        # Calculate number of longs needed for block storage
        bits = 4  # Start with minimum 4 bits
        blocks_per_long = 64 // bits
        total_blocks = 16 * 16 * 16  # 4096 blocks per section
        states_count = (total_blocks + blocks_per_long - 1) // blocks_per_long
        block_states = nbt.TAG_Long_Array(name='BlockStates')
        block_states.value = [0] * states_count
        section.tags.append(block_states)
        
        # Add section to the chunk's section list
        if self.version >= VERSION_21w43a:
            if 'sections' not in self.data:
                sections = nbt.TAG_List(name='sections', type=nbt.TAG_Compound)
                self.data.tags.append(sections)
            self.data['sections'].tags.append(section)
        else:
            if 'Sections' not in self.data:
                sections = nbt.TAG_List(name='Sections', type=nbt.TAG_Compound)
                self.data.tags.append(sections)
            self.data['Sections'].tags.append(section)
        
        return section
    
    def _set_block_in_section(self, section: nbt.TAG_Compound, block: Block, 
                          x: int, y: int, z: int) -> None:
        """
        Set block in a section (modern format 1.21.1+).

        Parameters
        ----------
        section : nbt.TAG_Compound
            The section to modify
        block : Block
            The block to set
        x : int
            X coordinate within section (0-15)
        y : int
            Y coordinate within section (0-15)
        z : int
            Z coordinate within section (0-15)

        Returns
        -------
        None
        """
        palette = palette_from_section(section)
        block_states = section['block_states']
        
        # Find block in existing palette or add it
        block_name = block.name()
        block_index = None
        for i, entry in enumerate(palette):
            if entry['Name'].value == block_name:
                if self._props_match(entry.get('Properties'), block.properties):
                    block_index = i
                    break
        
        # If the block doesn't exist, add it to the palette
        if block_index is None:
            block_index = self._add_block_to_palette(section, block)
            # Update the palette reference after adding
            palette = palette_from_section(section)
        
        bits = max((len(palette) - 1).bit_length(), 4)
        if 'data' not in block_states:
            data = nbt.TAG_Long_Array(name='data')
            array_size = self._calculate_states_count(bits)
            data.value = [0] * array_size
            block_states.tags.append(data)
        states = block_states['data'].value
        self._write_block_index(states, block_index, x, y, z, bits, palette)
    def _recalculate_blockstates_bits(self, section: nbt.TAG_Compound, old_bits: int, new_bits: int) -> None:
        """
        Recalculate the BlockStates array when bits per block changes.

        Parameters
        ----------
        section : nbt.TAG_Compound
            The section to recalculate
        old_bits : int
            Previous number of bits per block
        new_bits : int
            New number of bits per block

        Returns
        -------
        None
        """
        block_states = section['block_states']
        palette = block_states['palette']

        # Create/get data array
        if 'data' not in block_states:
            data = nbt.TAG_Long_Array(name='data')
            array_size = self._calculate_states_count(new_bits)
            data.value = [0] * array_size
            block_states.tags.append(data)
        states = block_states['data'].value

        # If the array size needs to change, resize and rewrite all blocks
        required_size = self._calculate_states_count(new_bits)
        if len(states) != required_size:
                
            # Store current block indices
            block_indices = []
            for by in range(16):
                for bz in range(16):
                    for bx in range(16):
                        index = self._get_block_index_from_section(section, bx, by, bz)
                        if index is not None and index >= len(palette) - 1:
                            index = self._get_air_block_index(palette)
                        block_indices.append(0 if index is None else index)
                
            # Create new array with correct size
            new_states = [0] * required_size
                
            # Track blocks before and after for verification
            blocks_before = {}
            blocks_after = {}
                
            # Store current block arrangement
            for y in range(16):
                for z in range(16):
                    for x in range(16):
                        index = self._get_block_index_from_section(section, x, y, z)
                        if index is not None and index < len(palette):
                            blocks_before[(x,y,z)] = index
                
            # Write back all indices with new bit width
            for i, block_index in enumerate(block_indices):
                if block_index >= len(palette):
                    block_index = self._get_air_block_index(palette)
                    
                if self.version >= VERSION_20w17a:
                    long_index = i // (64 // new_bits)
                    offset = (i % (64 // new_bits)) * new_bits
                else:
                    bit_start = i * new_bits
                    long_index = bit_start // 64
                    offset = bit_start % 64
                    
                # Calculate x,y,z from index for better debugging
                y = (i // (16 * 16)) % 16
                z = (i // 16) % 16
                x = i % 16

                mask = (1 << new_bits) - 1
                if offset + new_bits <= 64:
                    # Simple case: all bits fit in one long
                    current = new_states[long_index]
                    current &= ~(mask << offset)
                    current |= (block_index & mask) << offset
                    new_states[long_index] = current & ((1 << 64) - 1)
                    
                    # Verify write
                    stored = (new_states[long_index] >> offset) & mask
                    if stored != block_index:
                        raise(f"ERROR: Value mismatch at {i}: wrote {block_index} but read {stored}")
                else:
                    # Complex case: bits span two longs
                    bits_in_first = 64 - offset
                    bits_in_second = new_bits - bits_in_first
                    
                    # First long
                    first_mask = (1 << bits_in_first) - 1
                    current = new_states[long_index]
                    current &= ~(first_mask << offset)
                    current |= (block_index & first_mask) << offset
                    new_states[long_index] = current & ((1 << 64) - 1)
                    
                    # Second long if we have room
                    if long_index + 1 < len(new_states):
                        second_mask = (1 << bits_in_second) - 1
                        current = new_states[long_index + 1]
                        current &= ~second_mask
                        current |= (block_index >> bits_in_first) & second_mask
                        new_states[long_index + 1] = current & ((1 << 64) - 1)
                        
                        # Verify spanning write
                        stored_first = (new_states[long_index] >> offset) & first_mask
                        stored_second = new_states[long_index + 1] & second_mask
                        stored = stored_first | (stored_second << bits_in_first)
                        if stored != block_index:
                            raise(f"ERROR: Spanning value mismatch at {i}: wrote {block_index} but read {stored}")
                
            # Update the states array
            states[:] = new_states
            
            # Verify blocks after resize
            for y in range(16):
                for z in range(16):
                    for x in range(16):
                        index = self._get_block_index_from_section(section, x, y, z)
                        if index is not None and index < len(palette):
                            blocks_after[(x,y,z)] = index
    
    def _get_air_block_index(self, palette: nbt.TAG_List) -> int:
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

    def _write_block_index(self, states, block_index, x, y, z, bits, palette: nbt.TAG_List) -> None:
        """
        Write a block index to the states array with proper bounds checking.

        Handles spanning across multiple longs when necessary.

        Parameters
        ----------
        states : list
            The block states array to modify
        block_index : int
            The palette index of the block to write
        x : int
            X coordinate within section (0-15)
        y : int
            Y coordinate within section (0-15)
        z : int
            Z coordinate within section (0-15)
        bits : int
            Number of bits per block
        palette : nbt.TAG_List
            The palette list for validation

        Returns
        -------
        None
        """
        # Debug check for invalid indices
        if block_index >= len(palette):
            block_index = self._get_air_block_index(palette)
        if block_index < 0:
            block_index = self._get_air_block_index(palette)
        
        # Calculate position in the section using YZX order
        index = y * 16 * 16 + z * 16 + x
        
        # In versions after 20w17a, blocks cannot occupy more than one element in BlockStates
        if self.version >= VERSION_20w17a:
            long_index = index // (64 // bits)
            offset = (index % (64 // bits)) * bits
        else:
            bit_start = index * bits
            long_index = bit_start // 64
            offset = bit_start % 64

        # Ensure states array has the correct number of longs based on bits
        required_longs = self._calculate_states_count(bits)
        if len(states) != required_longs:
            new_states = [0] * required_longs
            for i in range(min(len(states), required_longs)):
                new_states[i] = states[i]
            states[:] = new_states

        # Create a mask for the full value
        full_mask = (1 << bits) - 1
        if (block_index & full_mask) != block_index:
            raise ValueError(f"Block index {block_index} requires more than {bits} bits")

        if offset + bits <= 64:
            # Case 1: Block fits in single long
            current = states[long_index]
            
            # Clear the bits at the offset position
            current &= ~(full_mask << offset)
            # Insert the new value
            current |= (block_index << offset)
            # Store back
            states[long_index] = current & 0xFFFFFFFFFFFFFFFF
        
            
            # Verify the write
            verify_mask = full_mask << offset
            stored_value = (states[long_index] & verify_mask) >> offset
            if stored_value != block_index:
                raise ValueError(f"Verification failed! Wrote {block_index} but read back {stored_value}")
        else:
            # Case 2: Block spans two longs
            if long_index + 1 >= len(states):
                # Handle first long only since we can't span
                current = states[long_index]
                bits_in_first = 64 - offset
                mask_first = (1 << bits_in_first) - 1
                current &= ~(mask_first << offset)
                first_bits = block_index & mask_first
                current |= (first_bits << offset)
                states[long_index] = current & 0xFFFFFFFFFFFFFFFF
            else:
                current = states[long_index]
                next_long = states[long_index + 1]
            
                
                # Calculate bits in each long
                bits_in_first = 64 - offset
                bits_in_second = bits - bits_in_first
                
                # Handle first long - preserve existing bits outside our range
                mask_first = (1 << bits_in_first) - 1
                current_preserved = current & ~(mask_first << offset)
                first_bits = block_index & mask_first
                current = current_preserved | (first_bits << offset)
                states[long_index] = current & 0xFFFFFFFFFFFFFFFF
                
                # Handle second long - preserve existing bits outside our range
                mask_second = (1 << bits_in_second) - 1
                next_preserved = next_long & ~mask_second
                second_bits = (block_index >> bits_in_first) & mask_second
                next_long = next_preserved | second_bits
                states[long_index + 1] = next_long & 0xFFFFFFFFFFFFFFFF
                
                # Verify the spanning write
                stored_first = (states[long_index] >> offset) & mask_first
                stored_second = states[long_index + 1] & mask_second
                stored_value = stored_first | (stored_second << bits_in_first)
                if stored_value != block_index:
                    raise(f"WARNING: Block data verification failed at ({x},{y},{z}): wrote {block_index} but read {stored_value}")
            
            # Verify the write
            stored_first = (states[long_index] >> offset) & mask_first
            stored_second = states[long_index + 1] & mask_second
            stored_value = stored_first | (stored_second << bits_in_first)
            if stored_value != block_index:
                raise ValueError(f"Verification failed! Wrote {block_index} but read back {stored_value}")
    def _calculate_states_count(self, bits: int) -> int:
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

    def _get_block_index_from_section(self, section: nbt.TAG_Compound, x: int, y: int, z: int) -> int | None:
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

    
    def _props_match(self, nbt_props, block_props: dict) -> bool:
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
    
    def save(self, file_path: str) -> None:
        """
        Save the modified chunk to a region file.
        
        Parameters
        ----------
        file_path : str
            Path to the region file
        """
        region = Region.from_file(file_path)
        region.save_chunk(self, file_path)

    def get_tile_entity(self, x: int, y: int, z: int) -> Optional[nbt.TAG_Compound]:
        """
        Returns the tile entity at given coordinates, or None if there isn't a tile entity.

        To iterate through all tile entities in the chunk, use :class:`Chunk.tile_entities`

        Parameters
        ----------
        x : int
            X coordinate
        y : int
            Y coordinate
        z : int
            Z coordinate

        Returns
        -------
        nbt.TAG_Compound or None
            The tile entity NBT compound, or None if not found
        """
        for tile_entity in self.tile_entities:
            t_x, t_y, t_z = [tile_entity[k].value for k in "xyz"]
            if x == t_x and y == t_y and z == t_z:
                return tile_entity

    @classmethod
    def from_region(cls, region: Union[str, Region], chunk_x: int, chunk_z: int):
        """
        Creates a new chunk from region and the chunk's X and Z

        Parameters
        ----------
        region
            Either a :class:`anvil.Region` or a region file name (like ``r.0.0.mca``)

        Raises
        ----------
        anvil.ChunkNotFound
            If a chunk is outside this region or hasn't been generated yet
        """
        if isinstance(region, str):
            region = Region.from_file(region)
        nbt_data = region.chunk_data(chunk_x, chunk_z)
        if nbt_data is None:
            raise ChunkNotFound(f"Could not find chunk ({chunk_x}, {chunk_z})")
        return cls(nbt_data)
    
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
            The replacement block (either a block name like "minecraft:dirt" or a Block object)
        
        Returns
        -------
        bool
            True if the block was replaced, False otherwise
        
        Example
        -------
        >>> chunk.replace_block_at(5, 64, 10, "minecraft:diamond_block")
        >>> chunk.replace_block_at(5, 64, 10, Block.from_name("minecraft:stone"))
        """
        # Convert string to Block object if needed
        if isinstance(new_block, str):
            new_block = Block.from_name(new_block)
        
        try:
            self.set_block(new_block, x, y, z)
            return True
        except OutOfBoundsCoordinates:
            return False

    def replace_blocks(self, old_block: Union[str, Block], new_block: Union[str, Block]) -> int:
        """Replace all occurrences of a specific block type with another block type in the chunk."""
        # Convert strings to Block objects if needed
        if isinstance(old_block, str):
            old_block = Block.from_name(old_block)
        if isinstance(new_block, str):
            new_block = Block.from_name(new_block)

        old_block_name = old_block.name()
        old_props = old_block.properties
        count = 0

        section_range = section_height_range(self.version)

        for section_y in section_range:
            section = self.get_section(section_y)
            if section is None:
                continue

            for local_y in range(16):
                for z in range(16):
                    for x in range(16):
                        global_y = section_y * 16 + local_y

                        try:
                            current_block = self.get_block(x, global_y, z)

                            # Check if block name matches
                            if current_block.name() != old_block_name:
                                continue

                            # If old_block has no properties, match any variant
                            # Otherwise, check if properties match
                            if old_props and current_block.properties != old_props:
                                continue

                            # Replace the block
                            if self.replace_block_at(x, global_y, z, new_block):
                                count += 1

                        except (IndexError, OutOfBoundsCoordinates):
                            continue

        return count

    def set_biome(self, biome: Biome, x: int, y: int, z: int) -> None:
        """
        Sets the biome at given coordinates in the chunk.
        For Minecraft 1.21.1 only.

        Parameters
        ----------
        biome : Biome
            The biome to set
        int x, z
            In range of 0 to 15
        int y
            Global Y coordinate

        Raises
        ------
        OutOfBoundsCoordinates
            If coordinates are out of bounds
        """
        if x not in range(16):
            raise OutOfBoundsCoordinates(f"X ({x!r}) must be in range of 0 to 15")
        if z not in range(16):
            raise OutOfBoundsCoordinates(f"Z ({z!r}) must be in range of 0 to 15")

        section_range = section_height_range(self.version)
        section_y = y // 16
        if section_y not in section_range:
            raise OutOfBoundsCoordinates(f"Y ({y!r}) must be in range of "
                                         f"{section_range.start * 16} to {section_range.stop * 16 - 1}")

        section = self.get_section(section_y)
        if section is None:
            section = self._create_section(section_y)

        if 'biomes' not in section:
            self._create_biomes_in_section(section)

        biomes_data = section['biomes']
        palette = biomes_data['palette']
        biome_name = biome.name()

        # Check if this is a single-biome section without data array
        if len(palette) == 1 and 'data' not in biomes_data:
            # If it's already the same biome, nothing to do
            if palette[0].value == biome_name:
                return
            # Otherwise, we need to create a data array to support multiple biomes
            # Don't just replace the palette entry as that would change the entire section

        # Find or add biome in palette
        palette_index = None
        for i, pal_biome in enumerate(palette):
            if pal_biome.value == biome_name:
                palette_index = i
                break

        if palette_index is None:
            palette_index = len(palette)
            palette.tags.append(nbt.TAG_String(value=biome_name))

        self._set_biome_in_section_data(biomes_data, palette_index, x, y % 16, z)


    def _create_biomes_in_section(self, section: nbt.TAG_Compound) -> None:
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


    def _resize_biome_data_array(self, old_data: list, old_bits: int, new_bits: int) -> list:
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


    def _set_biome_in_section_data(self, biomes_data: nbt.TAG_Compound,
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
                new_data = self._resize_biome_data_array(old_data, old_bits, new_bits)
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

    def set_chunk_biome(self, biome: Biome) -> None:
        """
        Set the entire chunk to a single biome (optimized for uniform biomes).
        
        This method efficiently sets all sections in the chunk to the same biome
        by creating a minimal palette with a single entry and no data array.

        Parameters
        ----------
        biome : Biome
            The biome to apply to the whole chunk
            
        Example
        -------
        >>> chunk.set_chunk_biome(Biome.from_name("minecraft:desert"))
        """
        biome_name = biome.name()
        section_range = section_height_range(self.version)
        
        for section_y in section_range:
            section = self.get_section(section_y)
            if section is None:
                section = self._create_section(section_y)

            # Create or get biomes structure
            if 'biomes' not in section:
                biomes_data = nbt.TAG_Compound(name='biomes')
                palette = nbt.TAG_List(name='palette', type=nbt.TAG_String)
                palette.tags.append(nbt.TAG_String(value=biome_name))
                biomes_data.tags.append(palette)
                section.tags.append(biomes_data)
            else:
                biomes_data = section['biomes']
                palette = biomes_data['palette']
                
                # Reset palette to single biome
                palette.tags.clear()
                palette.tags.append(nbt.TAG_String(value=biome_name))
                
                # Remove data array if present (not needed for uniform biome)
                biomes_data.tags[:] = [tag for tag in biomes_data.tags if tag.name != 'data']
