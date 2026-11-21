# OrbisPanora lib

A Python library that reads, edits and writes Minecraft Java worlds in the Anvil format:
regions, chunks, blocks, biomes and structures. It targets Minecraft 1.21.1 and can read
older chunk layouts.

It is the first of three parts of OrbisPanora, an isometric world viewer:

| Repository | Role |
|---|---|
| **lib** (this one) | Reads and writes the world files. |
| [api](https://github.com/OrbisPanora/api) | Serves chunks as JSON, using this library. |
| [viewer](https://github.com/OrbisPanora/viewer) | Draws the chunks in the browser. |

## Install

Requires Python 3.14 or newer.

```bash
uv add git+https://github.com/OrbisPanora/lib@v0.1.0     # in a uv project
pip install git+https://github.com/OrbisPanora/lib@v0.1.0
```

Each release also has a wheel and a source archive on the
[releases page](https://github.com/OrbisPanora/lib/releases).

`Chunk.block_array()` decodes a whole chunk at once and needs numpy, which is an optional
extra: `pip install "orbispanora-lib[fast] @ git+https://github.com/OrbisPanora/lib@<tag>"`
(or `uv add "orbispanora-lib[fast] @ git+https://github.com/OrbisPanora/lib@<tag>"`).

## Quick start

The package is `orbispanora_lib`. It has the subpackages `anvil` (regions, chunks, blocks,
worlds) and `patterns` (cubes, pyramids, spheres, spirals).

```python
from orbispanora_lib.anvil import Block, Region, World

# One chunk of a region file
chunk = Region.from_file('world/region/r.0.0.mca').get_chunk(0, 0)
print(chunk.get_block(0, 62, 0, force_new=True).name())

# A whole world: read and change blocks, then write the changed regions
world = World('world')
world.set_block(Block('minecraft', 'diamond_block'), 0, 70, 0)
world.replace_blocks('minecraft:stone', 'minecraft:dirt', bounds=(0, 0, 0, 63, 63, 63))
world.save()
```

`World.save()` overwrites the region files. Work on a copy of a world you care about.

Memory: a `World` does not read region files into memory. It reads the header of a region
and each chunk when it is asked for, keeps at most `region_cache_size` (32) region files open
and `chunk_cache_size` (128) decoded chunks (about 240 KB each), and releases the rest.
Regions with unsaved changes are kept until `World.save()`. `lazy_regions=False` reads whole
files again (10 to 14 MB per region in a large world), and `World.close()` releases everything.

More examples (chunks, biomes, heights, areas, patterns, structures) are in
[`docs/usage.rst`](docs/usage.rst). The reference is generated from the code:

```bash
uv run --group docs sphinx-build -W -b html docs docs/_build/html
```

## Development

```bash
uv sync                      # creates .venv with the project and the dev group
uv run pytest --cov          # tests; CI fails below 80 % coverage
uv run pylint --rcfile=.github/workflows/pylintrc orbispanora_lib
uv run ty check
```

The tests use the region file `tests/world_files/r.0.0.mca` and temporary directories.
They do not read or write any other world.

A release is made by pushing a tag `vX.Y.Z` that matches the version in `pyproject.toml`.
The workflow in `.github/workflows/release.yaml` runs the checks again and attaches the
wheel and the source archive to a GitHub Release.

## Origin

OrbisPanora lib is a fork of [anvil-parser2](https://github.com/0xTiger/anvil-parser2),
which is a fork of [matcool's anvil-parser](https://github.com/matcool/anvil-parser). It
was started as a student project at the IUT and is now maintained on GitHub.

## Licence

MIT, see `LICENSE`.
