"""conftest.py — fixtures compartidos para pytest."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def specs_dir(repo_root: Path) -> Path:
    return repo_root / "specs"


@pytest.fixture(scope="session")
def catalog_dir(repo_root: Path) -> Path:
    return repo_root / "catalog"


@pytest.fixture(scope="session")
def assets_dir(repo_root: Path) -> Path:
    return repo_root / "assets"
