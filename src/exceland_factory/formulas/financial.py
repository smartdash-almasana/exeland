"""Módulo de fórmulas financieras — helpers Python (no Excel)."""
from __future__ import annotations


def margen_bruto(precio_venta: float, costo_unitario: float) -> float:
    """Margen bruto como fracción (0–1)."""
    if precio_venta == 0:
        raise ValueError("precio_venta no puede ser cero")
    return (precio_venta - costo_unitario) / precio_venta


def precio_venta_con_margen(costo_unitario: float, margen_objetivo: float) -> float:
    """Precio de venta dado costo y margen objetivo (fracción)."""
    if margen_objetivo >= 1:
        raise ValueError("margen_objetivo debe ser menor que 1")
    return costo_unitario / (1 - margen_objetivo)


def punto_equilibrio_unidades(
    costos_fijos: float,
    precio_venta: float,
    costo_variable_unitario: float,
) -> float:
    """Unidades mínimas para cubrir costos fijos."""
    contribucion = precio_venta - costo_variable_unitario
    if contribucion <= 0:
        raise ValueError("La contribución marginal debe ser positiva")
    return costos_fijos / contribucion


def punto_equilibrio_pesos(costos_fijos: float, margen_contribucion: float) -> float:
    """Ingresos mínimos para cubrir costos fijos."""
    if margen_contribucion <= 0:
        raise ValueError("margen_contribucion debe ser positivo")
    return costos_fijos / margen_contribucion


def resultado_neto(ingresos: float, egresos: float) -> float:
    """Resultado neto del período."""
    return ingresos - egresos


def ingresos_totales(precio_venta: float, unidades: float) -> float:
    """Ingresos totales del período."""
    return precio_venta * unidades


def egresos_totales(
    costos_fijos: float,
    costo_variable_unitario: float,
    unidades: float,
) -> float:
    """Total de egresos del período."""
    return costos_fijos + (costo_variable_unitario * unidades)
