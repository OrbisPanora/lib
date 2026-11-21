"""Print two result files side by side.

Usage::

    uv run python benchmarks/compare.py results/before.json results/after.json

Every number that appears in both files is listed with the ratio after / before. The labels
of both files (machine, commit, world) are printed first, so a difference caused by another
machine or another world is visible.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Tuple


def numbers(node: object, prefix: str = '') -> Iterator[Tuple[str, float]]:
    """Every number of a result file with its dotted path; labels are skipped."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ('machine', 'world', 'script', 'timestamp'):
                continue
            yield from numbers(value, f'{prefix}{key}.')
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        yield prefix.rstrip('.'), float(node)


def main(argv: List[str]) -> int:
    """Compare ``argv[0]`` (before) with ``argv[1]`` (after)."""
    if len(argv) != 2:
        print(__doc__)
        return 2
    before, after = (json.loads(Path(name).read_text(encoding='utf-8')) for name in argv)
    for name, data in zip(('before', 'after'), (before, after)):
        print(f'{name}: {data.get("machine")}  {data.get("world")}')
    old: Dict[str, float] = dict(numbers(before))
    print(f"\n{'metric':<56}{'before':>12}{'after':>12}{'ratio':>8}")
    for key, value in numbers(after):
        if key in old:
            ratio = f'{value / old[key]:.2f}' if old[key] else '-'
            print(f'{key:<56}{old[key]:>12.3f}{value:>12.3f}{ratio:>8}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
