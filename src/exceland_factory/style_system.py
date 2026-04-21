"""
Style System centralizado de Exceland.

Construye todos los xlsxwriter format objects desde brand.json.
Un único punto de verdad para estilos; cero estilos en templates.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import xlsxwriter

_BRAND_PATH = Path(__file__).resolve().parents[2] / "assets" / "brand.json"


def _load_brand() -> dict[str, Any]:
    with _BRAND_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@dataclass
class StyleBook:
    """Contenedor de todos los formats de xlsxwriter para un workbook."""

    # -- Títulos y encabezados --
    title: Any = field(default=None)
    subtitle: Any = field(default=None)
    section_header: Any = field(default=None)
    col_header: Any = field(default=None)

    # -- Datos de input --
    input_text: Any = field(default=None)
    input_currency: Any = field(default=None)
    input_percentage: Any = field(default=None)
    input_integer: Any = field(default=None)

    # -- Datos calculados (locked) --
    locked_currency: Any = field(default=None)
    locked_percentage: Any = field(default=None)
    locked_integer: Any = field(default=None)
    locked_number: Any = field(default=None)
    locked_text: Any = field(default=None)

    # -- Alertas / KPI coloreados --
    kpi_positive: Any = field(default=None)
    kpi_negative: Any = field(default=None)
    kpi_neutral: Any = field(default=None)
    kpi_warning: Any = field(default=None)

    # -- Motor (hoja oculta) --
    engine_formula: Any = field(default=None)
    engine_label: Any = field(default=None)

    # -- Labels / etiquetas --
    label: Any = field(default=None)
    label_bold: Any = field(default=None)
    hint: Any = field(default=None)

    # -- Bienvenida --
    welcome_title: Any = field(default=None)
    welcome_subtitle: Any = field(default=None)
    welcome_body: Any = field(default=None)
    welcome_price: Any = field(default=None)

    # -- Guía --
    guide_step: Any = field(default=None)
    guide_body: Any = field(default=None)

    # -- Genérico --
    blank: Any = field(default=None)
    center_bold: Any = field(default=None)


def build_styles(workbook: xlsxwriter.Workbook) -> StyleBook:
    """
    Crea todos los formats para el workbook dado, a partir de brand.json.
    Retorna un StyleBook con todos los formats listos para usar.
    """
    brand = _load_brand()
    c = brand["colors"]
    font = brand["font"]
    fn = font["name"]
    fs = font["size"]

    def fmt(props: dict[str, Any]) -> Any:
        return workbook.add_format(props)

    # ---- Base commons ------
    base = {"font_name": fn, "font_size": fs, "valign": "vcenter"}
    base_border = {**base, "border": 1, "border_color": c["border"]}

    # ---- Titles / Headers --------------------------------------------------
    title = fmt({
        **base,
        "font_size": font["title"],
        "bold": True,
        "font_color": c["text_light"],
        "bg_color": c["primary"],
        "align": "left",
        "valign": "vcenter",
        "indent": 1,
    })
    subtitle = fmt({
        **base,
        "font_size": font["header"],
        "font_color": c["text_light"],
        "bg_color": c["primary_light"],
        "italic": True,
        "align": "left",
        "indent": 1,
    })
    section_header = fmt({
        **base,
        "font_size": font["header"],
        "bold": True,
        "font_color": c["text_light"],
        "bg_color": c["secondary"],
        "align": "left",
        "indent": 1,
        "top": 2, "bottom": 2,
        "top_color": c["secondary"],
        "bottom_color": c["secondary"],
    })
    col_header = fmt({
        **base_border,
        "bold": True,
        "font_color": c["text_light"],
        "bg_color": c["primary"],
        "align": "center",
        "text_wrap": True,
    })

    # ---- Input styles -------------------------------------------------------
    _input_base = {
        **base_border,
        "bg_color": c["input_bg"],
        "font_color": c["text_dark"],
        "locked": False,
    }
    input_text = fmt({**_input_base, "align": "left"})
    input_currency = fmt({**_input_base, "num_format": "#,##0.00", "align": "right"})
    input_percentage = fmt({**_input_base, "num_format": "0.00%", "align": "right"})
    input_integer = fmt({**_input_base, "num_format": "#,##0", "align": "right"})

    # ---- Locked / calculated ------------------------------------------------
    _locked_base = {
        **base_border,
        "bg_color": c["locked_bg"],
        "font_color": c["text_mid"],
        "locked": True,
        "italic": True,
    }
    locked_currency = fmt({**_locked_base, "num_format": "#,##0.00", "align": "right"})
    locked_percentage = fmt({**_locked_base, "num_format": "0.00%", "align": "right"})
    locked_integer = fmt({**_locked_base, "num_format": "#,##0", "align": "right"})
    locked_number = fmt({**_locked_base, "num_format": "0.00", "align": "right"})
    locked_text = fmt({**_locked_base, "align": "left"})

    # ---- KPI cards ----------------------------------------------------------
    kpi_positive = fmt({
        **base, "bold": True, "font_size": font["header"] + 2,
        "font_color": "#1B5E20", "bg_color": c["success_bg"],
        "border": 2, "border_color": c["secondary"],
        "num_format": "#,##0.00", "align": "right",
    })
    kpi_negative = fmt({
        **base, "bold": True, "font_size": font["header"] + 2,
        "font_color": "#B71C1C", "bg_color": c["danger_bg"],
        "border": 2, "border_color": "#E53935",
        "num_format": "#,##0.00", "align": "right",
    })
    kpi_neutral = fmt({
        **base, "bold": True, "font_size": font["header"] + 2,
        "font_color": c["text_dark"], "bg_color": c["section_bg"],
        "border": 2, "border_color": c["border"],
        "num_format": "#,##0.00", "align": "right",
    })
    kpi_warning = fmt({
        **base, "bold": True, "font_size": font["header"] + 2,
        "font_color": "#E65100", "bg_color": c["warning_bg"],
        "border": 2, "border_color": c["accent"],
        "num_format": "#,##0.00", "align": "right",
    })

    # ---- Engine sheet -------------------------------------------------------
    engine_formula = fmt({
        **base,
        "bg_color": c["engine_bg"],
        "font_color": c["engine_text"],
        "font_name": "Courier New",
        "font_size": font["small"],
        "align": "left",
        "locked": True,
    })
    engine_label = fmt({
        **base,
        "bg_color": c["engine_bg"],
        "font_color": "#AAAAAA",
        "font_size": font["small"],
        "align": "right",
        "locked": True,
    })

    # ---- Labels / hints -----------------------------------------------------
    label = fmt({
        **base,
        "font_color": c["text_dark"],
        "bg_color": c["section_bg"],
        "align": "right",
        "right": 1, "right_color": c["border"],
        "indent": 1,
    })
    label_bold = fmt({
        **base,
        "bold": True,
        "font_color": c["primary"],
        "bg_color": c["section_bg"],
        "align": "right",
        "right": 1, "right_color": c["border"],
        "indent": 1,
    })
    hint = fmt({
        **base,
        "font_size": font["small"],
        "font_color": "#6B7280",
        "italic": True,
        "align": "left",
        "indent": 1,
    })

    # ---- Welcome sheet ------------------------------------------------------
    welcome_title = fmt({
        **base,
        "font_size": 22,
        "bold": True,
        "font_color": c["text_light"],
        "bg_color": c["primary"],
        "align": "center",
        "valign": "vcenter",
    })
    welcome_subtitle = fmt({
        **base,
        "font_size": 13,
        "font_color": c["text_light"],
        "bg_color": c["primary_light"],
        "italic": True,
        "align": "center",
    })
    welcome_body = fmt({
        **base,
        "font_color": c["text_dark"],
        "align": "left",
        "text_wrap": True,
        "indent": 2,
    })
    welcome_price = fmt({
        **base,
        "font_size": 16,
        "bold": True,
        "font_color": c["secondary"],
        "align": "center",
        "num_format": '"ARS "#,##0',
    })

    # ---- Guide sheet --------------------------------------------------------
    guide_step = fmt({
        **base,
        "bold": True,
        "font_color": c["text_light"],
        "bg_color": c["secondary"],
        "align": "left",
        "indent": 1,
    })
    guide_body = fmt({
        **base,
        "font_color": c["text_dark"],
        "text_wrap": True,
        "align": "left",
        "indent": 2,
        "bottom": 1, "bottom_color": c["border"],
    })

    # ---- Generics -----------------------------------------------------------
    blank = fmt({**base, "bg_color": "#FFFFFF"})
    center_bold = fmt({**base, "bold": True, "align": "center"})

    return StyleBook(
        title=title,
        subtitle=subtitle,
        section_header=section_header,
        col_header=col_header,
        input_text=input_text,
        input_currency=input_currency,
        input_percentage=input_percentage,
        input_integer=input_integer,
        locked_currency=locked_currency,
        locked_percentage=locked_percentage,
        locked_integer=locked_integer,
        locked_number=locked_number,
        locked_text=locked_text,
        kpi_positive=kpi_positive,
        kpi_negative=kpi_negative,
        kpi_neutral=kpi_neutral,
        kpi_warning=kpi_warning,
        engine_formula=engine_formula,
        engine_label=engine_label,
        label=label,
        label_bold=label_bold,
        hint=hint,
        welcome_title=welcome_title,
        welcome_subtitle=welcome_subtitle,
        welcome_body=welcome_body,
        welcome_price=welcome_price,
        guide_step=guide_step,
        guide_body=guide_body,
        blank=blank,
        center_bold=center_bold,
    )
