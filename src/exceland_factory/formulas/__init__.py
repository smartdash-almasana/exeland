"""Paquete de fórmulas Python."""
from exceland_factory.formulas.financial import (
    egresos_totales,
    ingresos_totales,
    margen_bruto,
    precio_venta_con_margen,
    punto_equilibrio_pesos,
    punto_equilibrio_unidades,
    resultado_neto,
)
from exceland_factory.formulas.pricing import markup, margen_bruto_pesos, precio_con_descuento
from exceland_factory.formulas.stock import (
    alerta_stock_minimo,
    costo_reposicion_promedio,
    dias_stock_restante,
    rotacion_inventario,
)

__all__ = [
    "margen_bruto",
    "precio_venta_con_margen",
    "punto_equilibrio_unidades",
    "punto_equilibrio_pesos",
    "resultado_neto",
    "ingresos_totales",
    "egresos_totales",
    "markup",
    "margen_bruto_pesos",
    "precio_con_descuento",
    "alerta_stock_minimo",
    "costo_reposicion_promedio",
    "dias_stock_restante",
    "rotacion_inventario",
]
