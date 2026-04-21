"""Config: paths y constantes globales del proyecto."""
from __future__ import annotations

from pathlib import Path

# Raíz del repositorio (2 niveles arriba de este archivo: src/exceland_factory/ → src/ → repo)
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

CATALOG_DIR: Path = REPO_ROOT / "catalog"
SPECS_DIR: Path = REPO_ROOT / "specs"
ASSETS_DIR: Path = REPO_ROOT / "assets"
DIST_DIR: Path = REPO_ROOT / "dist"
BRAND_PATH: Path = ASSETS_DIR / "brand.json"

FORMULA_CATALOG_PATH: Path = CATALOG_DIR / "formulas.yaml"
VALIDATION_CATALOG_PATH: Path = CATALOG_DIR / "validations.yaml"
PRODUCT_REGISTRY_PATH: Path = CATALOG_DIR / "product_registry.yaml"

WAREHOUSE_DIR: Path = REPO_ROOT / "warehouse"
WAREHOUSE_TEMPLATES_DIR: Path = WAREHOUSE_DIR / "templates"
WAREHOUSE_PREVIEWS_DIR: Path = WAREHOUSE_DIR / "previews"
WAREHOUSE_MANIFEST_PATH: Path = WAREHOUSE_DIR / "manifest.json"
