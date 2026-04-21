"""
NL Parser: normaliza texto libre y extrae señales semánticas.
Sin LLM — solo normalización, tokenización y keyword extraction.
"""
from __future__ import annotations

import re
import unicodedata


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    Convierte a minúsculas, elimina acentos y puntuación irrelevante.
    Retorna string limpio para matching.
    """
    # Lowercase
    text = text.lower()
    # Eliminar acentos (NFD → strip combining chars)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # Reemplazar puntuación por espacio
    text = re.sub(r"[^\w\s]", " ", text)
    # Colapsar espacios
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """Tokeniza texto normalizado en palabras."""
    return normalize(text).split()


# ---------------------------------------------------------------------------
# Stopwords en español (mínimas)
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con",
    "contra", "cual", "cuando", "de", "del", "desde", "donde", "durante",
    "e", "el", "ella", "ellas", "ellos", "en", "entre", "era", "es", "esa",
    "esas", "ese", "eso", "esos", "esta", "estas", "este", "esto", "estos",
    "estoy", "fue", "han", "hasta", "hay", "he", "la", "las", "le", "les",
    "lo", "los", "me", "mi", "mis", "muy", "mas", "no", "nos", "o", "para",
    "pero", "por", "que", "se", "si", "sin", "sobre", "su", "sus", "te",
    "tu", "tus", "un", "una", "unas", "uno", "unos", "y", "ya", "yo",
    "necesito", "quiero", "hacer", "tener", "saber", "ver", "poder",
    "planilla", "plantilla", "excel", "hoja", "calculo", "calcular",
    "ayuda", "ayudar", "crear", "armar", "hacer", "llevar",
}


def keywords(text: str) -> list[str]:
    """Extrae tokens significativos (sin stopwords)."""
    tokens = tokenize(text)
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 2]


# ---------------------------------------------------------------------------
# ParsedPrompt
# ---------------------------------------------------------------------------

class ParsedPrompt:
    """Resultado del parsing de un prompt de lenguaje natural."""

    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.normalized = normalize(raw)
        self.tokens = tokenize(raw)
        self.kw = keywords(raw)

    def contains(self, *words: str) -> bool:
        """True si alguna de las palabras (normalizadas) aparece en el texto."""
        norm_words = [normalize(w) for w in words]
        return any(w in self.normalized for w in norm_words)

    def __repr__(self) -> str:
        return f"ParsedPrompt(kw={self.kw})"
