"""Factory: punto de entrada de alto nivel para construcción de productos."""
from __future__ import annotations

from pathlib import Path

from exceland_factory.config import SPECS_DIR
from exceland_factory.models import BuildResult
from exceland_factory.registry import load_product_registry
from exceland_factory.validators import load_spec
from exceland_factory.workbook_builder import build_workbook


def build_product(slug_or_path: str, output_path: Path | None = None) -> BuildResult:
    """
    Construye un producto Excel a partir de su slug o path de spec.

    Args:
        slug_or_path: slug del producto (ej: "caja_diaria") o path al YAML.
        output_path: destino del archivo generado. Si None, usa dist/{slug}.xlsx

    Returns:
        BuildResult con resultado de la operación.
    """
    # Resolver path
    spec_path = Path(slug_or_path)
    if not spec_path.exists():
        # Intentar como slug en specs/
        spec_path = SPECS_DIR / f"{slug_or_path}.yaml"

    spec = load_spec(spec_path)
    return build_workbook(spec, output_path)


def build_all_products(output_dir: Path | None = None) -> list[BuildResult]:
    """
    Construye todos los productos registrados en product_registry.yaml.

    Returns:
        Lista de BuildResult, uno por producto.
    """
    registry = load_product_registry()
    results: list[BuildResult] = []

    for slug, entry in registry.items():
        out = None
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            out = output_dir / f"{slug}.xlsx"

        result = build_product(entry.spec_path, out)
        results.append(result)

    return results
