"""Helpers genéricos para fórmulas Excel."""
from __future__ import annotations


def col_to_letter(n: int) -> str:
    """Convierte número de columna 1-indexed a letra Excel. Ej: 1→A, 28→AB."""
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def cell_ref(row: int, col: int, absolute: bool = False) -> str:
    """
    Genera referencia de celda Excel.
    row y col son 1-indexed.
    Ej: cell_ref(3, 2) → 'B3'; cell_ref(3, 2, absolute=True) → '$B$3'
    """
    letter = col_to_letter(col)
    if absolute:
        return f"${letter}${row}"
    return f"{letter}{row}"


def range_ref(
    row1: int,
    col1: int,
    row2: int,
    col2: int,
    sheet: str | None = None,
) -> str:
    """
    Genera referencia de rango Excel.
    Ej: range_ref(2, 1, 10, 3, 'DATOS') → 'DATOS!A2:C10'
    """
    ref = f"{cell_ref(row1, col1)}:{cell_ref(row2, col2)}"
    if sheet:
        return f"{sheet}!{ref}"
    return ref


def sum_range(row1: int, col1: int, row2: int, col2: int, sheet: str | None = None) -> str:
    """Retorna fórmula SUM sobre el rango. Ej: '=SUM(DATOS!A2:A10)'"""
    return f"=SUM({range_ref(row1, col1, row2, col2, sheet)})"
