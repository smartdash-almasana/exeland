"""Template Precio & Margen — builder especializado."""
from __future__ import annotations

from pathlib import Path

from exceland_factory.config import SPECS_DIR
from exceland_factory.factory import build_product
from exceland_factory.models import BuildResult


def build(output_path: Path | None = None) -> BuildResult:
    """Construye la plantilla Calculadora Precio & Margen."""
    spec_path = SPECS_DIR / "precio_margen.yaml"
    return build_product(str(spec_path), output_path)
