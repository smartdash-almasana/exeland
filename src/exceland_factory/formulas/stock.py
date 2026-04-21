"""Módulo de fórmulas de stock — helpers Python."""
from __future__ import annotations


def alerta_stock_minimo(stock_actual: float, stock_minimo: float) -> bool:
    """True si el stock está en o por debajo del mínimo."""
    return stock_actual <= stock_minimo


def dias_stock_restante(stock_actual: float, ventas_diarias: float) -> float | str:
    """Días de stock restante. Retorna 'Sin datos' si ventas_diarias es 0."""
    if ventas_diarias == 0:
        return "Sin datos"
    return stock_actual / ventas_diarias


def costo_reposicion_promedio(
    stock_actual: float,
    costo_actual: float,
    unidades_nuevas: float,
    costo_nuevo: float,
) -> float:
    """Costo promedio ponderado tras reposición."""
    total_units = stock_actual + unidades_nuevas
    if total_units == 0:
        raise ValueError("No hay unidades para calcular el promedio")
    return (stock_actual * costo_actual + unidades_nuevas * costo_nuevo) / total_units


def rotacion_inventario(costo_mercaderia_vendida: float, inventario_promedio: float) -> float:
    """Rotación de inventario en el período."""
    if inventario_promedio == 0:
        return 0.0
    return costo_mercaderia_vendida / inventario_promedio
