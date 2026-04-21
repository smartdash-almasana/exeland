"""Parser / validator de specs YAML → ProductSpec."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from exceland_factory.models import ProductSpec


def load_spec(path: Path | str) -> ProductSpec:
    """
    Carga un archivo YAML de spec y lo valida con Pydantic.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: si la validación falla.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Spec no encontrado: {path}")

    with path.open(encoding="utf-8") as f:
        try:
            raw = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError(f"YAML inválido en {path}:\n{exc}") from exc

    try:
        return ProductSpec.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Spec inválido en {path}:\n{exc}") from exc


def validate_spec(path: Path | str) -> list[str]:
    """
    Valida un spec YAML. Retorna lista de errores (vacía si OK).
    """
    errors: list[str] = []
    try:
        load_spec(path)
    except FileNotFoundError as e:
        errors.append(str(e))
    except ValueError as e:
        errors.append(str(e))
    return errors

