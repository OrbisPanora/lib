"""Time how the library reads a world, to find which step of reading a chunk is slow.

Usage::

    uv run python benchmarks/bench_read.py --world /path/to/world --label small

It only reads the world. It prints a table and writes ``benchmarks/results/<timestamp>.json``
(git-ignored). The file holds the numbers and labels (machine, commit, world size, region count)
so that two runs can be compared with ``benchmarks/compare.py``.
"""
import argparse
import io
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from nbt import nbt

from orbispanora_lib.anvil import Chunk, Region
from orbispanora_lib.anvil.chunk import section_height_range

REGION_NAME = re.compile(r'r\.(-?\d+)\.(-?\d+)\.mca$')
RESULTS_DIR = Path(__file__).parent / 'results'


def rss_mb() -> float:
    """Resident memory of this process in MB (Linux only, 0.0 elsewhere)."""
    try:
        with open('/proc/self/status', encoding='utf-8') as status:
            for line in status:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1]) / 1024
    except OSError:
        pass
    return 0.0


def percentile(values: List[float], fraction: float) -> float:
    """Nearest-rank percentile; 0.0 for an empty list."""
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def summary(values: List[float]) -> Dict[str, float]:
    """p50, p95, max and mean of a list of measurements."""
    return {
        'count': len(values),
        'p50': round(percentile(values, 0.5), 3),
        'p95': round(percentile(values, 0.95), 3),
        'max': round(max(values), 3) if values else 0.0,
        'mean': round(statistics.fmean(values), 3) if values else 0.0,
    }


def timed(function: Callable[[], object]) -> float:
    """Milliseconds taken by one call."""
    start = time.perf_counter()
    function()
    return (time.perf_counter() - start) * 1000


def command_output(command: List[str], cwd: Optional[Path] = None) -> str:
    """Output of a command, or an empty string if it fails."""
    try:
        return subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def machine_labels() -> Dict[str, object]:
    """CPU, cores, memory, Python and commit, written next to the numbers."""
    cpu = ''
    memory_mb = 0
    try:
        with open('/proc/cpuinfo', encoding='utf-8') as info:
            cpu = next((line.split(':', 1)[1].strip() for line in info if line.startswith('model name')), '')
        with open('/proc/meminfo', encoding='utf-8') as info:
            memory_mb = int(next(line for line in info if line.startswith('MemTotal')).split()[1]) // 1024
    except (OSError, StopIteration):
        pass
    here = Path(__file__).parent
    return {
        'cpu': cpu or platform.processor(),
        'cores': os.cpu_count(),
        'memory_mb': memory_mb,
        'python': platform.python_version(),
        'commit': command_output(['git', 'rev-parse', '--short', 'HEAD'], here),
        'dirty': bool(command_output(['git', 'status', '--porcelain'], here)),
    }


def region_files(world: Path) -> List[Path]:
    """Non-empty region files of the overworld, sorted by name."""
    files = [path for path in (world / 'region').glob('r.*.mca') if REGION_NAME.match(path.name) and path.stat().st_size > 8192]
    return sorted(files)


def evenly(items: List, count: int) -> List:
    """``count`` items spread over the list."""
    if count >= len(items):
        return list(items)
    return [items[i * len(items) // count] for i in range(count)]


def existing_chunks(region: Region) -> List[tuple]:
    """Coordinates of the chunks stored in a region file."""
    return [(x, z) for z in range(32) for x in range(32) if region.chunk_location(x, z) != (0, 0)]


def read_region(path: Path) -> Region:
    """Open a region file with the chunk cache off, as ``World`` does."""
    return Region.from_file(str(path), cache_size=None)


def raw_chunk(region: Region, chunk_x: int, chunk_z: int) -> bytes:
    """Compressed bytes of a chunk, as stored in the file."""
    offset = region.chunk_location(chunk_x, chunk_z)[0] * 4096
    length = int.from_bytes(region.data[offset:offset + 4], 'big')
    return bytes(region.data[offset + 5:offset + 4 + length])


def bench_regions(files: List[Path]) -> Dict[str, object]:
    """Time to read each file and its size, plus resident memory after holding more and more regions."""
    sizes = [path.stat().st_size / 1e6 for path in files]
    times = [timed(lambda path=path: read_region(path)) for path in files]
    held: List[Region] = []
    memory = {}
    before = rss_mb()
    for index, path in enumerate(files, start=1):
        held.append(read_region(path))
        if index in (1, 10, 100) or index == len(files):
            memory[str(index)] = round(rss_mb() - before, 1)
    return {'file_mb': summary(sizes), 'open_ms': summary(times), 'rss_growth_mb_after_n_regions': memory}


def first_section(chunk: Chunk):
    """First section that is not only air, with its index."""
    for section_y in reversed(section_height_range(chunk.version)):
        section = chunk.get_section(section_y)
        if section is not None and 'block_states' in section and not chunk._holds_only_air(section):  # pylint: disable=protected-access
            return section_y, section
    return None


def bench_chunks(files: List[Path], per_region: int, block_calls: int) -> Dict[str, object]:
    """Time each step of reading a chunk: decompress, parse, build, per-block reads, surface walk."""
    steps: Dict[str, List[float]] = {key: [] for key in (
        'compressed_kb', 'zlib_ms', 'nbt_ms', 'unzipped_kb', 'get_block_us', 'heightmap_ms', 'surface_blocks_ms', 'blocks_per_chunk')}
    versions = set()
    for path in files:
        region = read_region(path)
        for chunk_x, chunk_z in evenly(existing_chunks(region), per_region):
            compressed = raw_chunk(region, chunk_x, chunk_z)
            steps['compressed_kb'].append(len(compressed) / 1024)
            raw = zlib.decompress(compressed)
            steps['unzipped_kb'].append(len(raw) / 1024)
            steps['zlib_ms'].append(timed(lambda data=compressed: zlib.decompress(data)))
            steps['nbt_ms'].append(timed(lambda data=raw: nbt.NBTFile(buffer=io.BytesIO(data))))
            chunk = Chunk(nbt.NBTFile(buffer=io.BytesIO(raw)))
            versions.add(chunk.version)
            found = first_section(chunk)
            if found is not None:
                section = found[1]
                start = time.perf_counter()
                for call in range(block_calls):
                    chunk.get_block(call % 16, (call // 16) % 16, (call // 256) % 16, section, force_new=True)
                steps['get_block_us'].append((time.perf_counter() - start) / block_calls * 1e6)
            steps['heightmap_ms'].append(timed(chunk.to_heightmap))
            surface: list = []
            steps['surface_blocks_ms'].append(timed(lambda: surface.extend(chunk.get_surface_blocks())))
            steps['blocks_per_chunk'].append(len(surface))
    result: Dict[str, object] = {key: summary(values) for key, values in steps.items()}
    result['data_versions'] = sorted(versions)
    return result


def world_labels(world: Path, label: str, files: List[Path]) -> Dict[str, object]:
    """Size and region count of the world, and the name the person chose for it."""
    every = list((world / 'region').glob('r.*.mca'))
    total = sum(path.stat().st_size for path in every)
    return {'label': label, 'size_mb': round(total / 1e6, 1), 'region_files': len(every), 'non_empty_region_files': len(files)}


def print_table(results: Dict[str, Any]) -> None:
    """Print the measurements as rows of p50, p95 and max."""
    print(f"{'metric':<28}{'count':>7}{'p50':>12}{'p95':>12}{'max':>12}")
    for group in ('regions', 'chunks'):
        for key, value in results[group].items():
            if isinstance(value, dict) and 'p50' in value:
                print(f"{key:<28}{value['count']:>7}{value['p50']:>12}{value['p95']:>12}{value['max']:>12}")
    print('rss growth (MB) after n regions:', results['regions']['rss_growth_mb_after_n_regions'])


def main(argv: Optional[List[str]] = None) -> int:
    """Run the benchmark and write the result file."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--world', required=True, type=Path, help='World folder (the one that holds region/).')
    parser.add_argument('--label', default='world', help='Name for this world in the result file, for example small or large.')
    parser.add_argument('--regions', type=int, default=20, help='Region files to sample (default 20).')
    parser.add_argument('--chunks', type=int, default=8, help='Chunks to sample per region file (default 8).')
    parser.add_argument('--block-calls', type=int, default=4096, help='get_block calls per chunk (default 4096).')
    parser.add_argument('--out', type=Path, default=RESULTS_DIR, help='Folder for the result file.')
    args = parser.parse_args(argv)

    files = region_files(args.world)
    if not files:
        print(f'No region files in {args.world / "region"}', file=sys.stderr)
        return 1
    sample = evenly(files, args.regions)

    results: Dict[str, Any] = {
        'script': 'lib/bench_read',
        'timestamp': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'machine': machine_labels(),
        'world': world_labels(args.world, args.label, files),
        'regions': bench_regions(sample),
        'chunks': bench_chunks(sample, args.chunks, args.block_calls),
    }
    print_table(results)

    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f'lib-{args.label}-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'Wrote {path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
