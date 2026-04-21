"""Paquete de templates de productos."""
from exceland_factory.templates.caja_diaria import build as build_caja_diaria
from exceland_factory.templates.precio_margen import build as build_precio_margen
from exceland_factory.templates.punto_equilibrio import build as build_punto_equilibrio
from exceland_factory.templates.stock_control import build as build_stock_control

__all__ = [
    "build_caja_diaria",
    "build_precio_margen",
    "build_stock_control",
    "build_punto_equilibrio",
]
