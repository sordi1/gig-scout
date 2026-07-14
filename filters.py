"""Filtro por palavra-chave (com limite de palavra), qualidade do cliente e ranking."""

from __future__ import annotations

import re

from config import KEYWORDS, MAX_PROJECTS_PER_EMAIL, MAX_PROPOSALS, MIN_AVALIACOES_CLIENTE
from scraper import Projeto

_PATTERNS = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in KEYWORDS]


def _e_relevante(projeto: Projeto) -> bool:
    if projeto.propostas > MAX_PROPOSALS:
        return False
    if projeto.cliente_avaliacoes < MIN_AVALIACOES_CLIENTE:
        return False
    texto = f"{projeto.titulo} {projeto.descricao}"
    return any(padrao.search(texto) for padrao in _PATTERNS)


def filtrar_e_ordenar(projetos: list[Projeto]) -> list[Projeto]:
    relevantes = [p for p in projetos if _e_relevante(p)]
    relevantes.sort(key=lambda p: p.propostas)
    return relevantes[:MAX_PROJECTS_PER_EMAIL]
