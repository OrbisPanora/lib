"""The benchmark scripts still run on the committed region file. No timing is checked."""
import importlib.util
import json
import sys
from pathlib import Path

BENCHMARKS = Path(__file__).parent.parent / 'benchmarks'


def load(name):
    """Import a script of ``benchmarks/`` by path."""
    spec = importlib.util.spec_from_file_location(name, BENCHMARKS / f'{name}.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_bench_read_writes_a_result_file(world_dir, tmp_path):
    bench = load('bench_read')
    out = tmp_path / 'results'
    assert bench.main(['--world', str(world_dir), '--label', 'fixture', '--regions', '1', '--chunks', '3',
                       '--block-calls', '64', '--out', str(out)]) == 0
    files = list(out.glob('lib-fixture-*.json'))
    assert len(files) == 1
    result = json.loads(files[0].read_text(encoding='utf-8'))
    assert result['world']['region_files'] == 1
    assert result['chunks']['zlib_ms']['count'] == 3
    assert 'cpu' in result['machine']


def test_bench_read_without_regions_fails(tmp_path):
    (tmp_path / 'region').mkdir()
    assert load('bench_read').main(['--world', str(tmp_path), '--out', str(tmp_path / 'out')]) == 1


def test_compare_lists_common_numbers(tmp_path, capsys):
    compare = load('compare')
    first = tmp_path / 'a.json'
    second = tmp_path / 'b.json'
    first.write_text(json.dumps({'machine': {}, 'world': {}, 'chunks': {'zlib_ms': {'p50': 2.0}}}), encoding='utf-8')
    second.write_text(json.dumps({'machine': {}, 'world': {}, 'chunks': {'zlib_ms': {'p50': 1.0}}}), encoding='utf-8')
    assert compare.main([str(first), str(second)]) == 0
    assert 'chunks.zlib_ms.p50' in capsys.readouterr().out
    assert compare.main([]) == 2
