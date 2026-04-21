"""
Spec Compiler: genera un spec YAML válido y buildable desde un IntentConfig.
El YAML generado es compatible con ProductSpec y pasa el hardening de bindings.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from exceland_factory.matcher import IntentConfig, MatchResult, match_intent
from exceland_factory.models import ProductSpec
from exceland_factory.validators import load_spec


# ---------------------------------------------------------------------------
# Field templates por intent
# ---------------------------------------------------------------------------

# Cada intent define sus campos de input con row/col/tipo/validación
_INTENT_FIELDS: dict[str, list[dict[str, Any]]] = {
    "caja": [
        {"id": "nombre_negocio", "label": "Nombre del negocio", "row": 5, "col": 2,
         "input_type": "text", "example": "Mi Comercio", "required": True},
        {"id": "mes_anio", "label": "Mes / Año", "row": 6, "col": 2,
         "input_type": "text", "example": "Enero 2025", "required": True},
        {"id": "saldo_inicial", "label": "Saldo inicial (ARS)", "row": 8, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number", "required": True},
        {"id": "ingresos_ventas", "label": "Ingresos por ventas", "row": 10, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "ingresos_otros", "label": "Otros ingresos", "row": 11, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "egresos_proveedores", "label": "Pago a proveedores", "row": 13, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "egresos_sueldos", "label": "Sueldos y cargas", "row": 14, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "egresos_alquiler", "label": "Alquiler / Expensas", "row": 15, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "egresos_servicios", "label": "Servicios (luz, internet, etc.)", "row": 16, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "egresos_otros", "label": "Otros egresos", "row": 17, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
    ],
    "precios": [
        {"id": "nombre_producto", "label": "Nombre del producto", "row": 5, "col": 2,
         "input_type": "text", "example": "Mi Producto", "required": True},
        {"id": "costo_unitario", "label": "Costo unitario (ARS)", "row": 7, "col": 2,
         "input_type": "currency", "default": 0, "validation": "positive_number", "required": True},
        {"id": "margen_objetivo", "label": "Margen objetivo (%)", "row": 8, "col": 2,
         "input_type": "percentage", "default": 0.40, "validation": "percentage_0_1",
         "required": True, "hint": "Ejemplo: 0.40 = 40%"},
        {"id": "unidades_estimadas", "label": "Unidades a vender (mes)", "row": 10, "col": 2,
         "input_type": "integer", "default": 0, "validation": "integer_non_negative"},
    ],
    "stock": [
        {"id": "nombre_producto", "label": "Nombre del producto", "row": 5, "col": 2,
         "input_type": "text", "example": "Producto A", "required": True},
        {"id": "stock_actual", "label": "Stock actual (unidades)", "row": 7, "col": 2,
         "input_type": "integer", "default": 0, "validation": "integer_non_negative", "required": True},
        {"id": "stock_minimo", "label": "Stock mínimo de alerta", "row": 8, "col": 2,
         "input_type": "integer", "default": 5, "validation": "integer_non_negative", "required": True},
        {"id": "ventas_diarias", "label": "Ventas promedio diarias (uds)", "row": 9, "col": 2,
         "input_type": "number", "default": 0, "validation": "non_negative_number"},
        {"id": "costo_actual", "label": "Costo unitario actual (ARS)", "row": 11, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "unidades_reponer", "label": "Unidades a reponer", "row": 12, "col": 2,
         "input_type": "integer", "default": 0, "validation": "integer_non_negative"},
        {"id": "costo_reposicion", "label": "Costo unitario reposición (ARS)", "row": 13, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "costo_mercaderia_vendida", "label": "CMV del período (ARS)", "row": 15, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
        {"id": "inventario_promedio", "label": "Inventario promedio período (ARS)", "row": 16, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number"},
    ],
    "punto_equilibrio": [
        {"id": "nombre_negocio", "label": "Nombre del negocio / producto", "row": 5, "col": 2,
         "input_type": "text", "example": "Mi Negocio", "required": True},
        {"id": "precio_venta", "label": "Precio de venta unitario (ARS)", "row": 7, "col": 2,
         "input_type": "currency", "default": 0, "validation": "positive_number", "required": True},
        {"id": "costo_variable_unitario", "label": "Costo variable por unidad (ARS)", "row": 8, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number", "required": True},
        {"id": "costos_fijos", "label": "Costos fijos del mes (ARS)", "row": 9, "col": 2,
         "input_type": "currency", "default": 0, "validation": "non_negative_number", "required": True},
        {"id": "unidades_estimadas", "label": "Unidades que estimás vender", "row": 11, "col": 2,
         "input_type": "integer", "default": 0, "validation": "integer_non_negative"},
    ],
}

# Bindings del MOTOR por intent — mapeados a las celdas de input reales
_INTENT_MOTOR_FORMULAS: dict[str, list[dict[str, Any]]] = {
    "caja": [
        {"id": "ingresos_totales", "formula_ref": "ingresos_totales",
         "bindings": {"precio_venta": "SUM(CAJA!C10:C11)", "unidades_vendidas": "1"}},
        {"id": "egresos_totales", "formula_ref": "egresos_totales",
         "bindings": {"costos_fijos": "SUM(CAJA!C13:C17)", "costo_variable_unitario": "0", "unidades_vendidas": "1"}},
        {"id": "flujo_caja_neto", "formula_ref": "flujo_caja_neto",
         "bindings": {"ingresos": "MOTOR!C2", "egresos": "MOTOR!C3"}},
        {"id": "saldo_acumulado", "formula_ref": "saldo_acumulado",
         "bindings": {"saldo_anterior": "CAJA!C8", "flujo_neto": "MOTOR!C4"}},
    ],
    "precios": [
        {"id": "precio_venta_con_margen", "formula_ref": "precio_venta_con_margen",
         "bindings": {"costo_unitario": "DATOS!C7", "margen_objetivo": "DATOS!C8"}},
        {"id": "margen_bruto", "formula_ref": "margen_bruto",
         "bindings": {"precio_venta": "MOTOR!C2", "costo_unitario": "DATOS!C7"}},
        {"id": "margen_bruto_pesos", "formula_ref": "margen_bruto_pesos",
         "bindings": {"precio_venta": "MOTOR!C2", "costo_unitario": "DATOS!C7"}},
        {"id": "markup", "formula_ref": "markup",
         "bindings": {"precio_venta": "MOTOR!C2", "costo_unitario": "DATOS!C7"}},
    ],
    "stock": [
        {"id": "alerta_stock_minimo", "formula_ref": "alerta_stock_minimo",
         "bindings": {"stock_actual": "STOCK!C7", "stock_minimo": "STOCK!C8"}},
        {"id": "dias_stock_restante", "formula_ref": "dias_stock_restante",
         "bindings": {"stock_actual": "STOCK!C7", "ventas_diarias_promedio": "STOCK!C9"}},
        {"id": "costo_reposicion_promedio", "formula_ref": "costo_reposicion_promedio",
         "bindings": {"stock_actual": "STOCK!C7", "costo_actual": "STOCK!C11",
                      "unidades_nuevas": "STOCK!C12", "costo_nuevo": "STOCK!C13"}},
        {"id": "rotacion_inventario", "formula_ref": "rotacion_inventario",
         "bindings": {"costo_mercaderia_vendida": "STOCK!C15", "inventario_promedio": "STOCK!C16"}},
    ],
    "punto_equilibrio": [
        {"id": "punto_equilibrio_unidades", "formula_ref": "punto_equilibrio_unidades",
         "bindings": {"costos_fijos": "DATOS!C9", "precio_venta": "DATOS!C7",
                      "costo_variable_unitario": "DATOS!C8"}},
        {"id": "margen_bruto", "formula_ref": "margen_bruto",
         "bindings": {"precio_venta": "DATOS!C7", "costo_unitario": "DATOS!C8"}},
        {"id": "punto_equilibrio_pesos", "formula_ref": "punto_equilibrio_pesos",
         "bindings": {"costos_fijos": "DATOS!C9", "margen_contribucion": "MOTOR!C3"}},
        {"id": "resultado_neto", "formula_ref": "resultado_neto",
         "bindings": {"ingresos_totales": "DATOS!C7", "egresos_totales": "DATOS!C9"}},
    ],
}


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convierte texto a slug válido."""
    import unicodedata
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:40]


# ---------------------------------------------------------------------------
# YAML builder
# ---------------------------------------------------------------------------

def _build_spec_dict(
    intent: IntentConfig,
    slug: str,
    title: str | None = None,
) -> dict[str, Any]:
    """Construye el dict del spec completo listo para serializar a YAML."""
    final_title = title or intent.title
    input_name = intent.input_sheet_name
    fields = _INTENT_FIELDS[intent.intent]
    motor_formulas = _INTENT_MOTOR_FORMULAS[intent.intent]

    spec: dict[str, Any] = {
        "slug": slug,
        "title": final_title,
        "subtitle": intent.subtitle,
        "version": "1.0.0",
        "price_ars": intent.price_ars,
        "category": intent.category,
        "branding": {
            "primary_color": "#1A3C5E",
            "secondary_color": "#00A36C",
            "accent_color": "#F4A01C",
        },
        "sheets": [
            {"name": "BIENVENIDA", "type": "welcome", "protected": True},
            {
                "name": input_name,
                "type": "input",
                "protected": False,
                "fields": fields,
            },
            {
                "name": "MOTOR",
                "type": "engine",
                "protected": True,
                "hidden": True,
                "formulas": motor_formulas,
            },
            {"name": "DASHBOARD", "type": "dashboard", "protected": True},
            {"name": "GUIA", "type": "guide", "protected": True},
        ],
        "formulas": intent.formulas,
    }
    return spec


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class CompileResult:
    """Resultado de la compilación de un prompt a spec YAML."""

    def __init__(
        self,
        success: bool,
        spec_path: str = "",
        intent: str = "",
        confidence: float = 0.0,
        error: str | None = None,
        suggestions: list[str] | None = None,
    ) -> None:
        self.success = success
        self.spec_path = spec_path
        self.intent = intent
        self.confidence = confidence
        self.error = error
        self.suggestions = suggestions or []


def compile_prompt(
    prompt: str,
    output_path: Path,
    slug: str | None = None,
    title: str | None = None,
) -> CompileResult:
    """
    Compila un prompt de lenguaje natural a un spec YAML válido y buildable.

    Args:
        prompt: texto libre del usuario.
        output_path: path donde guardar el YAML generado.
        slug: slug personalizado (opcional, se genera desde el título si no se da).
        title: título personalizado (opcional).

    Returns:
        CompileResult con resultado de la operación.
    """
    match = match_intent(prompt)

    if not match.matched or match.primary is None:
        suggestions = [
            "Intentá con palabras como: caja, ingresos, egresos, flujo",
            "O: precio, margen, costo, markup",
            "O: stock, inventario, reponer, alertas",
            "O: equilibrio, break even, costos fijos, cuánto vender",
        ]
        return CompileResult(
            success=False,
            error=f"No pude identificar el tipo de planilla para: '{prompt}'",
            suggestions=suggestions,
        )

    intent = match.primary
    final_slug = slug or _slugify(title or intent.title)
    spec_dict = _build_spec_dict(intent, final_slug, title)

    # Serializar a YAML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(
            spec_dict,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )

    # Validar que el YAML generado sea parseable por ProductSpec
    try:
        load_spec(output_path)
    except (FileNotFoundError, ValueError) as exc:
        return CompileResult(
            success=False,
            error=f"El spec generado no pasó validación: {exc}",
            intent=intent.intent,
            confidence=intent.confidence,
        )

    return CompileResult(
        success=True,
        spec_path=str(output_path),
        intent=intent.intent,
        confidence=intent.confidence,
    )


def suggest_prompt(prompt: str) -> dict[str, Any]:
    """
    Analiza un prompt y retorna sugerencias sin generar archivos.

    Returns:
        Dict con intent detectado, confianza, fórmulas sugeridas y alternativas.
    """
    match = match_intent(prompt)

    if not match.matched or match.primary is None:
        return {
            "matched": False,
            "message": f"No pude identificar el tipo de planilla para: '{prompt}'",
            "suggestions": [
                "caja / flujo de caja / ingresos y egresos",
                "precio / margen / costo / markup",
                "stock / inventario / reposición",
                "equilibrio / break even / costos fijos",
            ],
            "scores": match.raw_scores,
        }

    p = match.primary
    return {
        "matched": True,
        "intent": p.intent,
        "confidence": round(p.confidence, 2),
        "title": p.title,
        "subtitle": p.subtitle,
        "category": p.category,
        "formulas": p.formulas,
        "kpis": [label for label, _ in p.kpi_refs],
        "tags": p.tags,
        "alternatives": [
            {"intent": a.intent, "confidence": round(a.confidence, 2), "title": a.title}
            for a in match.alternatives
        ],
        "scores": {k: round(v, 3) for k, v in match.raw_scores.items()},
    }
