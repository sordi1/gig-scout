"""Persistência dos IDs de projetos já notificados, para evitar e-mail duplicado."""

from __future__ import annotations

import json
import os

from config import STATE_FILE

MAX_STORED_IDS = 500


def carregar_vistos(caminho: str = STATE_FILE) -> set[str]:
    if not os.path.exists(caminho):
        return set()
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return set()


def salvar_vistos(ids: set[str], caminho: str = STATE_FILE) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(list(ids)[-MAX_STORED_IDS:], f)
