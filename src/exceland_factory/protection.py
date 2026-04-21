"""Módulo de protección extra de hojas (helper sobre xlsxwriter)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_BRAND_PATH = Path(__file__).resolve().parents[2] / "assets" / "brand.json"


def get_protection_config() -> dict[str, Any]:
    """Retorna la configuración de protección desde brand.json."""
    with _BRAND_PATH.open(encoding="utf-8") as f:
        brand = json.load(f)
    return brand["protection"]


def protection_options() -> dict[str, bool]:
    """Retorna el dict de opciones de protección listo para xlsxwriter."""
    cfg = get_protection_config()
    return {
        "select_locked_cells": cfg["allow_select_locked"],
        "select_unlocked_cells": cfg["allow_select_unlocked"],
        "sort": cfg["allow_sort"],
        "autofilter": cfg["allow_filter"],
    }


def protection_password() -> str:
    """Retorna la contraseña de protección."""
    return get_protection_config()["password"]
