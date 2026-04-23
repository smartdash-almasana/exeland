"""builders de hojas: welcome, input, engine, dashboard, guide."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import xlsxwriter

import re

from exceland_factory.models import FieldSpec, InputType, KpiSpec, ProductSpec, SheetSpec
from exceland_factory.registry import get_formula, resolve_formula
from exceland_factory.style_system import StyleBook


def _extract_placeholders(formula: str) -> set[str]:
    """Extrae todos los {placeholder} de una fórmula del catálogo."""
    return set(re.findall(r'\{(\w+)\}', formula))


def _validate_bindings(
    formula_ref: str,
    formula_str: str,
    bindings: dict[str, str],
    spec_slug: str,
) -> None:
    """
    Verifica que todos los placeholders requeridos estén cubiertos por bindings.
    Lanza ValueError con mensaje claro si falta alguno.
    """
    required = _extract_placeholders(formula_str)
    provided = set(bindings.keys())
    missing = required - provided
    if missing:
        raise ValueError(
            f"Spec '{spec_slug}': fórmula '{formula_ref}' tiene placeholders sin resolver.\n"
            f"  Requeridos : {sorted(required)}\n"
            f"  Recibidos  : {sorted(provided)}\n"
            f"  Faltantes  : {sorted(missing)}\n"
            f"  Fórmula    : {formula_str}"
        )

_BRAND_PATH = Path(__file__).resolve().parents[3] / "assets" / "brand.json"


def _brand() -> dict[str, Any]:
    with _BRAND_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_col_widths(ws: Any, widths: list[tuple[int, int, float]]) -> None:
    """widths: list of (first_col, last_col, width)"""
    for first, last, w in widths:
        ws.set_column(first, last, w)


def _input_style_for(field: FieldSpec, styles: StyleBook) -> Any:
    mapping = {
        InputType.currency: styles.input_currency,
        InputType.percentage: styles.input_percentage,
        InputType.integer: styles.input_integer,
        InputType.number: styles.input_currency,
        InputType.text: styles.input_text,
        InputType.date: styles.input_text,
    }
    return mapping.get(field.input_type, styles.input_text)


# ---------------------------------------------------------------------------
# BIENVENIDA
# ---------------------------------------------------------------------------

def build_welcome_sheet(
    workbook: xlsxwriter.Workbook,
    ws: Any,
    spec: ProductSpec,
    styles: StyleBook,
) -> None:
    brand = _brand()
    layout = brand["layout"]

    ws.set_column(0, 0, 2)
    ws.set_column(1, 4, 22)
    ws.set_row(0, 10)
    ws.set_row(1, layout["row_title_height"] * 1.5)
    ws.set_row(2, layout["row_header_height"])
    ws.set_row(3, 15)

    # Merge y título principal
    ws.merge_range("B2:E2", spec.title.upper(), styles.welcome_title)
    ws.merge_range("B3:E3", spec.subtitle, styles.welcome_subtitle)

    # Cuerpo
    body_items = [
        "✅  Plantilla lista para usar — solo completá los campos en azul.",
        "🔒  Las celdas grises están protegidas: los cálculos son automáticos.",
        "📊  El DASHBOARD muestra los resultados clave de tu negocio.",
        "📖  Ver la hoja GUIA para instrucciones detalladas.",
        "",
        f"💰  Precio de venta: ARS {spec.price_ars:,.0f}",
        "",
        "🌐  Compatible con Microsoft Excel y Google Sheets.",
        "📧  Soporte: soporte@exceland.com.ar",
    ]
    for i, line in enumerate(body_items):
        row = 5 + i
        ws.set_row(row, layout["row_default_height"] + 2)
        ws.merge_range(f"B{row}:E{row}", line, styles.welcome_body)

    ws.set_tab_color(brand["colors"]["primary"])


# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

def build_input_sheet(
    workbook: xlsxwriter.Workbook,
    ws: Any,
    spec: ProductSpec,
    styles: StyleBook,
    sheet_spec: SheetSpec,
) -> None:
    brand = _brand()
    layout = brand["layout"]

    ws.set_column(0, 0, 1)                              # margen
    ws.set_column(1, 1, layout["col_label_width"])       # etiqueta
    ws.set_column(2, 2, layout["col_value_width"])       # valor
    ws.set_column(3, 3, layout["col_note_width"])        # nota/hint

    # Header
    ws.set_row(0, 10)
    ws.set_row(1, layout["row_title_height"])
    ws.set_row(2, layout["row_header_height"])
    ws.merge_range("B2:D2", spec.title, styles.title)
    ws.merge_range("B3:D3", "📝  Completá los campos en azul", styles.subtitle)

    ws.set_row(3, 20)
    ws.merge_range("B4:D4", "DATOS DE ENTRADA", styles.section_header)

    # REGLA DE COMPATIBILIDAD:
    # - Si hay fields (legacy), usar fields
    # - Si no hay fields pero hay inputs (v2), usar inputs con layout automático
    # - Si hay ambos, priorizar fields (legacy tiene precedencia)
    
    if sheet_spec.fields:
        # Legacy: usar fields con row/col explícitos
        for fspec in sheet_spec.fields:
            r = fspec.row - 1       # 0-indexed
            ws.set_row(r, layout["row_default_height"] + 2)

            label_fmt = styles.label_bold if fspec.required else styles.label
            ws.write(r, 1, fspec.label, label_fmt)

            val_fmt = _input_style_for(fspec, styles)
            default = fspec.default if fspec.default is not None else ""
            ws.write(r, 2, default, val_fmt)

            if fspec.hint:
                ws.write(r, 3, f"ℹ  {fspec.hint}", styles.hint)

    elif sheet_spec.inputs:
        # V2: usar inputs con layout automático (row secuencial desde 5)
        start_row = 5
        for i, inp in enumerate(sheet_spec.inputs):
            r = start_row + i - 1  # 0-indexed, empieza en fila 5
            ws.set_row(r, layout["row_default_height"] + 2)

            label_fmt = styles.label_bold if inp.required else styles.label
            ws.write(r, 1, inp.label, label_fmt)

            val_fmt = _input_style_for_v2(inp, styles)
            default = inp.default if inp.default is not None else ""
            ws.write(r, 2, default, val_fmt)

            if inp.hint:
                ws.write(r, 3, f"ℹ  {inp.hint}", styles.hint)

    ws.set_tab_color(brand["colors"]["secondary"])


def _input_style_for_v2(inp: Any, styles: StyleBook) -> Any:
    """Helper para obtener estilo de input desde InputSpecV2."""
    mapping = {
        InputType.currency: styles.input_currency,
        InputType.percentage: styles.input_percentage,
        InputType.integer: styles.input_integer,
        InputType.number: styles.input_currency,
        InputType.text: styles.input_text,
        InputType.date: styles.input_text,
    }
    return mapping.get(inp.type, styles.input_text)


# ---------------------------------------------------------------------------
# ENGINE (hoja de motor — oculta)
# ---------------------------------------------------------------------------

def build_engine_sheet(
    workbook: xlsxwriter.Workbook,
    ws: Any,
    spec: ProductSpec,
    styles: StyleBook,
    sheet_spec: SheetSpec,
) -> None:
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 50)

    ws.write(0, 1, "ID", styles.engine_label)
    ws.write(0, 2, "FÓRMULA", styles.engine_label)

    # REGLA DE COMPATIBILIDAD:
    # - Si hay formulas (legacy), usar formulas
    # - Si no hay formulas pero hay derived (v2), usar derived
    # - Si hay ambos, priorizar formulas (legacy tiene precedencia)

    if sheet_spec.formulas:
        # Legacy: usar formulas con bindings explícitos
        row = 1
        for binding in sheet_spec.formulas:
            try:
                formula_def = get_formula(binding.formula_ref)
            except KeyError:
                ws.write(row, 1, binding.id, styles.engine_label)
                ws.write(row, 2, f"[FÓRMULA NO ENCONTRADA: {binding.formula_ref}]", styles.engine_label)
                row += 1
                continue

            # Construir formula con bindings o dejar template si no hay bindings
            if binding.bindings:
                # Validar que todos los placeholders estén cubiertos antes de escribir
                _validate_bindings(
                    binding.formula_ref,
                    formula_def.excel_formula,
                    binding.bindings,
                    spec.slug,
                )
                formula_str = resolve_formula(binding.formula_ref, binding.bindings)
            else:
                # Sin bindings: verificar que la fórmula no tenga placeholders requeridos
                required = _extract_placeholders(formula_def.excel_formula)
                if required:
                    raise ValueError(
                        f"Spec '{spec.slug}': fórmula '{binding.formula_ref}' requiere bindings "
                        f"pero no tiene ninguno definido.\n"
                        f"  Placeholders requeridos: {sorted(required)}\n"
                        f"  Fórmula: {formula_def.excel_formula}"
                    )
                formula_str = formula_def.excel_formula

            ws.write(row, 1, binding.id, styles.engine_label)
            ws.write(row, 2, formula_str, styles.engine_formula)
            row += 1

    elif sheet_spec.derived:
        # V2: usar derived con resolución simbólica mínima
        # Construir mapa de inputs → celdas (layout automático: columna C, fila 5+)
        input_to_cell = _build_input_cell_map(spec)
        
        # Construir mapa de derived → celdas (MOTOR columna C, fila 2+)
        derived_to_cell: dict[str, str] = {}
        for i, d in enumerate(sheet_spec.derived):
            derived_to_cell[d.id] = f"MOTOR!C{i + 2}"

        row = 1
        for derived in sheet_spec.derived:
            try:
                formula_def = get_formula(derived.formula)
            except KeyError:
                ws.write(row, 1, derived.id, styles.engine_label)
                ws.write(row, 2, f"[FÓRMULA NO ENCONTRADA: {derived.formula}]", styles.engine_label)
                row += 1
                continue

            # Resolver bindings desde derived.inputs
            if derived.inputs:
                bindings = _resolve_derived_inputs(
                    derived.inputs,
                    input_to_cell,
                    derived_to_cell,
                    spec.slug,
                    derived.id,
                )
                _validate_bindings(
                    derived.formula,
                    formula_def.excel_formula,
                    bindings,
                    spec.slug,
                )
                formula_str = resolve_formula(derived.formula, bindings)
            else:
                required = _extract_placeholders(formula_def.excel_formula)
                if required:
                    raise ValueError(
                        f"Spec '{spec.slug}': derived '{derived.id}' requiere inputs "
                        f"pero no tiene ninguno definido.\n"
                        f"  Placeholders requeridos: {sorted(required)}"
                    )
                formula_str = formula_def.excel_formula

            ws.write(row, 1, derived.id, styles.engine_label)
            ws.write(row, 2, formula_str, styles.engine_formula)
            row += 1

    ws.set_tab_color("#2D2D2D")


def _build_input_cell_map(spec: ProductSpec) -> dict[str, str]:
    """
    Construye un mapa de input_id → referencia de celda.
    Para inputs v2: columna C, filas secuenciales desde 5.
    Para fields legacy: respeta row/col del spec.
    """
    input_map: dict[str, str] = {}
    
    for sheet in spec.sheets:
        if sheet.type.value != "input":
            continue
        
        sheet_name = sheet.name
        
        # Fields legacy
        for fspec in sheet.fields:
            col_letter = _col_letter(fspec.col + 1)  # col es 0-indexed
            input_map[fspec.id] = f"{sheet_name}!{col_letter}{fspec.row}"
        
        # Inputs v2 (layout automático)
        start_row = 5
        for i, inp in enumerate(sheet.inputs):
            input_map[inp.id] = f"{sheet_name}!C{start_row + i}"
    
    return input_map


def _resolve_derived_inputs(
    derived_inputs: dict[str, str],
    input_to_cell: dict[str, str],
    derived_to_cell: dict[str, str],
    spec_slug: str,
    derived_id: str,
) -> dict[str, str]:
    """
    Resuelve los inputs de una fórmula derived a referencias de celda.
    
    derived_inputs: {placeholder: input_id o derived_id}
    Retorna: {placeholder: cell_ref}
    """
    bindings: dict[str, str] = {}
    
    for placeholder, ref_id in derived_inputs.items():
        # Primero buscar en inputs
        if ref_id in input_to_cell:
            bindings[placeholder] = input_to_cell[ref_id]
        # Luego buscar en derived (referencia a otra fórmula)
        elif ref_id in derived_to_cell:
            bindings[placeholder] = derived_to_cell[ref_id]
        else:
            raise ValueError(
                f"Spec '{spec_slug}': derived '{derived_id}' referencia '{ref_id}' "
                f"que no existe en inputs ni en derived."
            )
    
    return bindings


def _col_letter(n: int) -> str:
    """Convierte número de columna (1-indexed) a letra Excel. Ej: 1→A, 3→C."""
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

def build_dashboard_sheet(
    workbook: xlsxwriter.Workbook,
    ws: Any,
    spec: ProductSpec,
    styles: StyleBook,
    sheet_spec: SheetSpec | None = None,
) -> None:
    brand = _brand()
    layout = brand["layout"]

    ws.set_column(0, 0, 2)
    ws.set_column(1, 2, 26)
    ws.set_column(3, 4, 22)

    ws.set_row(0, 10)
    ws.set_row(1, layout["row_title_height"] * 1.2)
    ws.set_row(2, layout["row_header_height"])

    ws.merge_range("B2:E2", f"📊  {spec.title} — Resultados", styles.title)
    ws.merge_range("B3:E3", "Los valores se actualizan automáticamente al completar DATOS", styles.subtitle)

    ws.set_row(3, 18)
    ws.merge_range("B4:E4", "RESUMEN EJECUTIVO", styles.section_header)

    # REGLA DE COMPATIBILIDAD:
    # - Si hay kpis (legacy con ref), usar kpis
    # - Si no hay kpis pero hay outputs (v2), usar outputs con resolución simbólica
    # - Si hay ambos, priorizar kpis (legacy tiene precedencia)
    # - Si no hay ninguno, fallback legacy

    if sheet_spec and sheet_spec.kpis:
        # Legacy: usar kpis con ref explícito
        kpis = sheet_spec.kpis
        kpis_v2 = None
    elif sheet_spec and sheet_spec.outputs:
        # V2: usar outputs con resolución simbólica
        kpis = None
        kpis_v2 = sheet_spec.outputs
    else:
        # Fallback legacy para specs sin kpis ni outputs
        kpis = [
            KpiSpec(label="Ingresos totales", ref="MOTOR!C2", style="kpi_positive"),
            KpiSpec(label="Egresos totales", ref="MOTOR!C3", style="kpi_negative"),
            KpiSpec(label="Resultado neto", ref="MOTOR!C4", style="kpi_neutral"),
            KpiSpec(label="Punto de equilibrio (uds)", ref="MOTOR!C5", style="kpi_warning"),
        ]
        kpis_v2 = None

    # Map style names to StyleBook objects
    style_map = {
        "kpi_positive": styles.kpi_positive,
        "kpi_negative": styles.kpi_negative,
        "kpi_neutral": styles.kpi_neutral,
        "kpi_warning": styles.kpi_warning,
    }

    if kpis:
        # Renderizar KPIs legacy
        for i, kpi in enumerate(kpis):
            r = 4 + i * 2
            ws.set_row(r, 24)
            ws.write(r, 1, kpi.label, styles.label_bold)

            if not kpi.ref or "!" not in kpi.ref:
                raise ValueError(f"Referencia KPI inválida en dashboard: {kpi.ref!r}")

            kpi_style = style_map.get(kpi.style, styles.kpi_neutral)
            ws.write_formula(r, 2, f"={kpi.ref}", kpi_style)
            ws.set_row(r + 1, 6)

        total_kpis = len(kpis)

    elif kpis_v2:
        # Renderizar KPIs v2 con resolución simbólica
        # Construir mapa de derived → celdas desde el spec completo
        derived_to_cell = _build_derived_cell_map(spec)

        for i, kpi in enumerate(kpis_v2):
            r = 4 + i * 2
            ws.set_row(r, 24)
            ws.write(r, 1, kpi.label, styles.label_bold)

            # Resolver source contra derived_to_cell
            if kpi.source not in derived_to_cell:
                raise ValueError(
                    f"Spec '{spec.slug}': KPI '{kpi.id}' referencia source '{kpi.source}' "
                    f"que no existe en derived. Disponibles: {sorted(derived_to_cell.keys())}"
                )

            cell_ref = derived_to_cell[kpi.source]
            kpi_style = style_map.get(kpi.style, styles.kpi_neutral)
            ws.write_formula(r, 2, f"={cell_ref}", kpi_style)
            ws.set_row(r + 1, 6)

        total_kpis = len(kpis_v2)

    else:
        total_kpis = 0

    ws.set_row(4 + total_kpis * 2, 20)
    note_row = 4 + total_kpis * 2
    ws.merge_range(
        note_row, 1, note_row, 4,
        "💡  Para ver fórmulas específicas, desprotegé la hoja MOTOR con la contraseña.",
        styles.hint,
    )
    ws.set_tab_color(brand["colors"]["accent"])


def _build_derived_cell_map(spec: ProductSpec) -> dict[str, str]:
    """
    Construye un mapa de derived_id → referencia de celda en MOTOR.
    Para derived v2: columna C, filas secuenciales desde 2.
    Para formulas legacy: respeta el orden del spec.
    """
    derived_map: dict[str, str] = {}
    
    for sheet in spec.sheets:
        if sheet.type.value != "engine":
            continue
        
        # Formulas legacy
        for i, binding in enumerate(sheet.formulas):
            derived_map[binding.id] = f"MOTOR!C{i + 2}"
        
        # Derived v2
        for i, d in enumerate(sheet.derived):
            derived_map[d.id] = f"MOTOR!C{i + 2}"
    
    return derived_map


# ---------------------------------------------------------------------------
# GUIA
# ---------------------------------------------------------------------------

_GUIDE_STEPS = [
    ("PASO 1 — BIENVENIDA", "Leé la hoja BIENVENIDA para entender la plantilla."),
    (
        "PASO 2 — INGRESAR DATOS",
        "Completá todos los campos en azul en la hoja de datos. "
        "Los campos obligatorios están en negrita.",
    ),
    (
        "PASO 3 — VER RESULTADOS",
        "Los resultados se calculan automáticamente en el DASHBOARD. "
        "No modifiques las celdas grises.",
    ),
    (
        "PASO 4 — INTERPRETAR",
        "Un resultado neto positivo indica ganancia. "
        "El punto de equilibrio te dice cuántas unidades necesitás vender para cubrir costos.",
    ),
    (
        "PREGUNTAS FRECUENTES",
        "¿Puedo cambiar los nombres de las hojas? No, las fórmulas dependen de esos nombres.\n"
        "¿Funciona en Google Sheets? Sí, importá el archivo y activá los cálculos.",
    ),
    (
        "SOPORTE",
        "soporte@exceland.com.ar | @exceland_ar",
    ),
]


def build_guide_sheet(
    workbook: xlsxwriter.Workbook,
    ws: Any,
    spec: ProductSpec,
    styles: StyleBook,
) -> None:
    brand = _brand()
    layout = brand["layout"]

    ws.set_column(0, 0, 2)
    ws.set_column(1, 4, 28)

    ws.set_row(0, 10)
    ws.set_row(1, layout["row_title_height"])
    ws.merge_range("B2:E2", f"📖  Guía de uso — {spec.title}", styles.title)

    row = 3
    for step_title, step_body in _GUIDE_STEPS:
        ws.set_row(row, layout["row_header_height"])
        ws.merge_range(row, 1, row, 4, step_title, styles.guide_step)
        row += 1

        lines = step_body.split("\n")
        for line in lines:
            ws.set_row(row, layout["row_default_height"] + 4)
            ws.merge_range(row, 1, row, 4, line, styles.guide_body)
            row += 1

        row += 1  # espacio entre pasos

    ws.set_tab_color(brand["colors"]["text_mid"])
