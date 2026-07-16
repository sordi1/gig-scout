"""Persistência dos IDs de projetos já notificados, para evitar e-mail duplicado."""

from __future__ import annotations

import json
import os

from config import STATE_FILE

MAX_STORED_IDS = 500


def carregar_vistos(caminho: str = STATE_FILE) -> list[str]:
    """Retorna os IDs já vistos, em ordem (mais antigo primeiro)."""
    if not os.path.exists(caminho):
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return list(json.load(f))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []


def salvar_vistos(ids: list[str], caminho: str = STATE_FILE) -> None:
    """Salva mantendo ordem - trunca os MAIS ANTIGOS quando passa do limite,
    nunca os mais recentes (era esse o bug: usar set() perdia a ordem e
    podia descartar exatamente os IDs vistos há pouco tempo)."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(ids[-MAX_STORED_IDS:], f)
