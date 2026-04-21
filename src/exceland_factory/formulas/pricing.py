"""Módulo de fórmulas de pricing — helpers Python."""
from __future__ import annotations


def margen_bruto_pesos(precio_venta: float, costo_unitario: float) -> float:
    """Margen bruto en moneda."""
    return precio_venta - costo_unitario


def markup(precio_venta: float, costo_unitario: float) -> float:
    """Markup sobre costo (fracción)."""
    if costo_unitario == 0:
        raise ValueError("costo_unitario no puede ser cero")
    return (precio_venta / costo_unitario) - 1


def precio_con_descuento(precio_base: float, descuento: float) -> float:
    """Precio final con descuento aplicado (fracción 0–1)."""
    if not 0 <= descuento < 1:
        raise ValueError("descuento debe estar entre 0 y 1")
    return precio_base * (1 - descuento)
