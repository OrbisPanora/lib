"""Shared fixtures: a copy of the committed region file inside a minimal world folder."""
import shutil
from pathlib import Path

import pytest

REGION_FIXTURE = Path(__file__).parent / 'world_files' / 'r.0.0.mca'


@pytest.fixture
def world_dir(tmp_path):
    """A world folder whose `region/` holds a copy of `r.0.0.mca`, so tests may modify it."""
    region_dir = tmp_path / 'world' / 'region'
    region_dir.mkdir(parents=True)
    shutil.copy(REGION_FIXTURE, region_dir / 'r.0.0.mca')
    return tmp_path / 'world'


@pytest.fixture
def region_file(world_dir):
    """Path of the writable copy of `r.0.0.mca`, as a string."""
    return str(world_dir / 'region' / 'r.0.0.mca')
