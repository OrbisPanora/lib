"""CacheManager, Biome, Block, OldBlock and Structure."""
import pytest
from nbt import nbt

from orbispanora_lib.anvil import Biome, Block, OldBlock, Structure
from orbispanora_lib.anvil.cache_manager import CacheManager


class TestCacheManager:

    def test_least_recently_used_entry_is_evicted(self):
        cache = CacheManager(2)
        cache.put((0, 0), 'a')
        cache.put((0, 1), 'b')
        assert cache.get((0, 0)) == 'a'
        cache.put((0, 2), 'c')
        assert cache.get((0, 1)) is None
        assert cache.get((0, 2)) == 'c'
        assert len(cache) == 2

    def test_stats_resize_invalidate_clear(self):
        cache = CacheManager(4)
        cache.put((0, 0), 'a')
        cache.get((0, 0))
        cache.get((9, 9))
        stats = cache.get_stats()
        assert stats['hits'] == 1 and stats['misses'] == 1 and stats['hit_rate'] == '50.00%'
        cache.put((0, 1), 'b')
        cache.resize(1)
        assert len(cache) == 1
        cache.invalidate((0, 1))
        assert len(cache) == 0
        cache.put((1, 1), 'x')
        cache.clear()
        assert len(cache) == 0
        assert 'CacheManager' in repr(cache)


class TestBiome:

    def test_from_name_and_name(self):
        assert Biome.from_name('minecraft:plains').name() == 'minecraft:plains'

    def test_from_numeric_id(self):
        assert Biome.from_numeric_id(1).name() == 'minecraft:plains'
        with pytest.raises(KeyError):
            Biome.from_numeric_id(999999)

    def test_equality_and_repr(self):
        assert Biome('minecraft', 'plains') == Biome('minecraft', 'plains')
        assert Biome('minecraft', 'plains') != Biome('minecraft', 'desert')
        assert 'plains' in repr(Biome('minecraft', 'plains'))


class TestBlock:

    def test_from_name_and_to_dict(self):
        block = Block.from_name('minecraft:stone')
        assert block.to_dict() == {'name': 'minecraft:stone', 'id': 'stone', 'namespace': 'minecraft', 'properties': {}}

    def test_default_namespace_and_equality(self):
        assert Block('minecraft', 'stone') == Block.from_name('minecraft:stone')
        assert Block('minecraft', 'stone') != Block('minecraft', 'dirt')
        assert hash(Block('minecraft', 'stone')) == hash(Block('minecraft', 'stone'))

    def test_properties(self):
        block = Block('minecraft', 'oak_stairs', {'facing': 'north'})
        assert block.properties['facing'] == 'north'
        assert 'oak_stairs' in repr(block)

    def test_from_palette_reads_nbt_properties(self):
        entry = nbt.TAG_Compound()
        entry.tags.append(nbt.TAG_String(name='Name', value='minecraft:oak_stairs'))
        props = nbt.TAG_Compound(name='Properties')
        props.tags.append(nbt.TAG_String(name='facing', value='north'))
        entry.tags.append(props)
        block = Block.from_palette(entry)
        assert block.name() == 'minecraft:oak_stairs'
        assert str(block.properties['facing']) == 'north'


class TestOldBlock:

    def test_convert_to_current_name(self):
        assert OldBlock(1, 0).convert().name() == 'minecraft:stone'
        assert 'OldBlock' in repr(OldBlock(1, 0))

    def test_unknown_id_is_an_error(self):
        with pytest.raises(KeyError):
            OldBlock(99999, 0).convert()


class TestStructure:

    @staticmethod
    def structure_nbt():
        data = nbt.NBTFile()
        size = nbt.TAG_List(name='size', type=nbt.TAG_Int)
        size.tags.extend([nbt.TAG_Int(2), nbt.TAG_Int(1), nbt.TAG_Int(1)])
        data.tags.append(size)
        palette = nbt.TAG_List(name='palette', type=nbt.TAG_Compound)
        entry = nbt.TAG_Compound()
        entry.tags.append(nbt.TAG_String(name='Name', value='minecraft:stone'))
        palette.tags.append(entry)
        data.tags.append(palette)
        blocks = nbt.TAG_List(name='blocks', type=nbt.TAG_Compound)
        for x, state in ((0, 0), (1, 0), (1, 7)):
            block = nbt.TAG_Compound()
            pos = nbt.TAG_List(name='pos', type=nbt.TAG_Int)
            pos.tags.extend([nbt.TAG_Int(x), nbt.TAG_Int(0), nbt.TAG_Int(0)])
            block.tags.append(pos)
            block.tags.append(nbt.TAG_Int(name='state', value=state))
            blocks.tags.append(block)
        data.tags.append(blocks)
        return data

    def test_blocks_with_an_unknown_palette_index_are_skipped(self, capsys):
        structure = Structure(self.structure_nbt())
        assert [pos for pos, _ in structure.blocks] == [(0, 0, 0), (1, 0, 0)]
        assert structure.palette[0].name() == 'minecraft:stone'
        assert 'invalid palette index' in capsys.readouterr().out

    def test_from_file(self, tmp_path):
        path = tmp_path / 'structure.nbt'
        self.structure_nbt().write_file(str(path))
        assert len(Structure.from_file(str(path)).blocks) == 2
