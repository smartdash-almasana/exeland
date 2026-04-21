"""Registry: carga y acceso al catálogo de fórmulas, validaciones y productos."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from exceland_factory.models import (
    FormulaDefinition,
    ProductRegistryEntry,
    ValidationDefinition,
)

# Rutas base (relativas a la raíz del repo)
_REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = _REPO_ROOT / "catalog"
SPECS_DIR = _REPO_ROOT / "specs"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Formula Registry
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_formula_catalog() -> dict[str, FormulaDefinition]:
    """Carga catalog/formulas.yaml y retorna dict slug→FormulaDefinition."""
    raw = _load_yaml(CATALOG_DIR / "formulas.yaml")
    formulas: dict[str, FormulaDefinition] = {}
    for slug, data in raw.get("formulas", {}).items():
        formulas[slug] = FormulaDefinition(**data)
    return formulas


def get_formula(slug: str) -> FormulaDefinition:
    """Obtiene una fórmula por slug; lanza KeyError si no existe."""
    catalog = load_formula_catalog()
    if slug not in catalog:
        available = ", ".join(sorted(catalog.keys()))
        raise KeyError(f"Fórmula '{slug}' no encontrada. Disponibles: {available}")
    return catalog[slug]


def resolve_formula(slug: str, bindings: dict[str, str]) -> str:
    """
    Resuelve la fórmula Excel del catálogo reemplazando los placeholders
    {input_name} por las referencias de celda dadas en `bindings`.

    Ejemplo:
        resolve_formula("margen_bruto", {"precio_venta": "C7", "costo_unitario": "C8"})
        → "=(C7-C8)/C7"
    """
    formula_def = get_formula(slug)
    result = formula_def.excel_formula
    for placeholder, cell_ref in bindings.items():
        result = result.replace(f"{{{placeholder}}}", cell_ref)
    return result


# ---------------------------------------------------------------------------
# Validation Registry
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_validation_catalog() -> dict[str, ValidationDefinition]:
    """Carga catalog/validations.yaml y retorna dict slug→ValidationDefinition."""
    raw = _load_yaml(CATALOG_DIR / "validations.yaml")
    validations: dict[str, ValidationDefinition] = {}
    for slug, data in raw.get("validations", {}).items():
        validations[slug] = ValidationDefinition(**data)
    return validations


def get_validation(slug: str) -> ValidationDefinition | None:
    """Obtiene una validación por slug; retorna None si no existe."""
    catalog = load_validation_catalog()
    return catalog.get(slug)


# ---------------------------------------------------------------------------
# Product Registry
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_product_registry() -> dict[str, ProductRegistryEntry]:
    """Carga catalog/product_registry.yaml."""
    raw = _load_yaml(CATALOG_DIR / "product_registry.yaml")
    products: dict[str, ProductRegistryEntry] = {}
    for slug, data in raw.get("products", {}).items():
        products[slug] = ProductRegistryEntry(**data)
    return products


def list_products() -> list[str]:
    """Lista todos los slugs registrados."""
    return sorted(load_product_registry().keys())


def get_product_entry(slug: str) -> ProductRegistryEntry:
    """Obtiene un producto del registry por slug."""
    registry = load_product_registry()
    if slug not in registry:
        raise KeyError(f"Producto '{slug}' no registrado.")
    return registry[slug]
