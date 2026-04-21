"""Warehouse: almacenamiento y publicación de plantillas Excel listas para venta."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from exceland_factory.config import (
    WAREHOUSE_DIR,
    WAREHOUSE_MANIFEST_PATH,
    WAREHOUSE_PREVIEWS_DIR,
    WAREHOUSE_TEMPLATES_DIR,
)
from exceland_factory.models import BuildResult, ProductSpec
from exceland_factory.registry import get_product_entry, load_formula_catalog
from exceland_factory.validators import load_spec
from exceland_factory.workbook_builder import build_workbook


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------

def _load_manifest() -> dict[str, Any]:
    """Carga el manifest existente o retorna uno vacío."""
    if WAREHOUSE_MANIFEST_PATH.exists():
        with WAREHOUSE_MANIFEST_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {"products": {}}


def _save_manifest(manifest: dict[str, Any]) -> None:
    """Guarda el manifest con formato legible."""
    WAREHOUSE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with WAREHOUSE_MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def _ensure_dirs() -> None:
    """Crea las carpetas del warehouse si no existen."""
    WAREHOUSE_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    WAREHOUSE_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Formula usage detection
# ---------------------------------------------------------------------------

def _formulas_used(spec: ProductSpec) -> list[str]:
    """Extrae los formula_ref usados en todas las hojas engine del spec."""
    used: list[str] = []
    for sheet in spec.sheets:
        for binding in sheet.formulas:
            if binding.formula_ref and binding.formula_ref not in used:
                used.append(binding.formula_ref)
    return used


# ---------------------------------------------------------------------------
# Publish result model (simple dataclass)
# ---------------------------------------------------------------------------

class PublishResult:
    def __init__(
        self,
        slug: str,
        success: bool,
        warehouse_path: str = "",
        error: str | None = None,
    ) -> None:
        self.slug = slug
        self.success = success
        self.warehouse_path = warehouse_path
        self.error = error


# ---------------------------------------------------------------------------
# Core publish logic
# ---------------------------------------------------------------------------

def publish_product(
    slug_or_path: str,
    overwrite: bool = True,
) -> PublishResult:
    """
    Publica un producto al warehouse:
    1. Build del .xlsx desde el spec
    2. Copia a warehouse/templates/
    3. Registra metadata en warehouse/manifest.json

    Args:
        slug_or_path: slug del producto o path al YAML de spec.
        overwrite: si True, sobrescribe si ya existe (default). Si False, falla.

    Returns:
        PublishResult con resultado de la operación.
    """
    _ensure_dirs()

    # Resolver spec path
    spec_path = Path(slug_or_path)
    if not spec_path.exists():
        from exceland_factory.config import SPECS_DIR
        spec_path = SPECS_DIR / f"{slug_or_path}.yaml"

    try:
        spec = load_spec(spec_path)
    except (FileNotFoundError, ValueError) as exc:
        return PublishResult(slug=slug_or_path, success=False, error=str(exc))

    # Destino en warehouse
    dest_path = WAREHOUSE_TEMPLATES_DIR / f"{spec.slug}.xlsx"

    # Verificar sobreescritura
    if dest_path.exists() and not overwrite:
        return PublishResult(
            slug=spec.slug,
            success=False,
            error=f"Ya existe '{dest_path}'. Usá overwrite=True para reemplazar.",
        )

    # Build en directorio temporal (dist/)
    from exceland_factory.config import DIST_DIR
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    build_path = DIST_DIR / f"{spec.slug}.xlsx"

    build_result = build_workbook(spec, build_path)
    if not build_result.success:
        return PublishResult(slug=spec.slug, success=False, error=build_result.error)

    # Copiar al warehouse
    shutil.copy2(build_path, dest_path)

    # Obtener tags desde el registry (si existe entrada)
    tags: list[str] = []
    try:
        entry = get_product_entry(spec.slug)
        tags = entry.tags
    except KeyError:
        pass

    # Registrar en manifest
    manifest = _load_manifest()
    now = datetime.now(timezone.utc).isoformat()

    manifest["products"][spec.slug] = {
        "slug": spec.slug,
        "title": spec.title,
        "subtitle": spec.subtitle,
        "price_ars": spec.price_ars,
        "free": spec.price_ars == 0,
        "source_spec": str(spec_path),
        "output_file": str(dest_path),
        "version": spec.version,
        "category": spec.category,
        "status": "published",
        "published_at": now,
        "formulas_used": _formulas_used(spec),
        "tags": tags,
        "compatible_with": ["excel", "google_sheets"],
    }

    _save_manifest(manifest)

    return PublishResult(
        slug=spec.slug,
        success=True,
        warehouse_path=str(dest_path),
    )


def publish_all_products(overwrite: bool = True) -> list[PublishResult]:
    """
    Publica todos los productos registrados en product_registry.yaml.

    Returns:
        Lista de PublishResult, uno por producto.
    """
    from exceland_factory.registry import load_product_registry
    registry = load_product_registry()
    results: list[PublishResult] = []

    for slug, entry in registry.items():
        result = publish_product(entry.spec_path, overwrite=overwrite)
        results.append(result)

    return results


def list_published() -> list[dict[str, Any]]:
    """Lista todos los productos publicados en el manifest."""
    manifest = _load_manifest()
    return list(manifest.get("products", {}).values())
