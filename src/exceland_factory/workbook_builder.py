"""Workbook Builder — orquestador principal."""
from __future__ import annotations

import json
from pathlib import Path

import xlsxwriter

from exceland_factory.config import DIST_DIR
from exceland_factory.layouts import (
    build_dashboard_sheet,
    build_engine_sheet,
    build_guide_sheet,
    build_input_sheet,
    build_welcome_sheet,
)
from exceland_factory.models import BuildResult, ProductSpec, SheetType
from exceland_factory.style_system import build_styles


def build_workbook(spec: ProductSpec, output_path: Path | None = None) -> BuildResult:
    """
    Orquesta la creación completa del workbook Excel para un spec dado.

    Args:
        spec: ProductSpec validado (cargado desde YAML).
        output_path: Path del archivo de salida. Si None, usa dist/{slug}.xlsx

    Returns:
        BuildResult con success/error y output_path.
    """
    if output_path is None:
        DIST_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DIST_DIR / f"{spec.slug}.xlsx"
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        wb = xlsxwriter.Workbook(str(output_path), {"strings_to_numbers": False})
        wb.set_properties({
            "title": spec.title,
            "subject": spec.subtitle,
            "author": "Exceland Factory",
            "company": "Exceland",
            "comments": f"v{spec.version} | ARS {spec.price_ars:,.0f}",
        })

        styles = build_styles(wb)
        brand = _load_brand()
        protection_cfg = brand["protection"]

        for sheet_spec in spec.sheets:
            ws = wb.add_worksheet(sheet_spec.name)

            # Dispatch por tipo de hoja
            if sheet_spec.type == SheetType.welcome:
                build_welcome_sheet(wb, ws, spec, styles)

            elif sheet_spec.type == SheetType.input:
                build_input_sheet(wb, ws, spec, styles, sheet_spec)

            elif sheet_spec.type == SheetType.engine:
                build_engine_sheet(wb, ws, spec, styles, sheet_spec)
                if sheet_spec.hidden:
                    ws.hide()

            elif sheet_spec.type == SheetType.dashboard:
                build_dashboard_sheet(wb, ws, spec, styles)

            elif sheet_spec.type == SheetType.guide:
                build_guide_sheet(wb, ws, spec, styles)

            # Protección de hoja
            if sheet_spec.protected:
                ws.protect(
                    protection_cfg["password"],
                    {
                        "select_locked_cells": protection_cfg["allow_select_locked"],
                        "select_unlocked_cells": protection_cfg["allow_select_unlocked"],
                        "sort": protection_cfg["allow_sort"],
                        "autofilter": protection_cfg["allow_filter"],
                    },
                )

        wb.close()
        return BuildResult(slug=spec.slug, output_path=str(output_path), success=True)

    except Exception as exc:
        return BuildResult(
            slug=spec.slug,
            output_path=str(output_path),
            success=False,
            error=str(exc),
        )


def _load_brand() -> dict:
    brand_path = Path(__file__).resolve().parents[2] / "assets" / "brand.json"
    with brand_path.open(encoding="utf-8") as f:
        return json.load(f)
