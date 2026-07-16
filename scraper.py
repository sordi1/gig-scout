"""Raspagem e parsing das listagens de projetos do 99Freelas."""

from __future__ import annotations

import html
import logging
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import USER_AGENT

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": USER_AGENT}

# Sessão com retry automático (3 tentativas, com espera crescente) para
# falha transitória de rede - sem isso, uma falha passageira derrubava a
# URL inteira sem segunda chance.
_session = requests.Session()
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))


@dataclass
class Projeto:
    id: str
    titulo: str
    link: str
    categoria: str
    nivel: str
    propostas: int
    interessados: int
    descricao: str = ""
    cliente_nome: str = ""
    cliente_nota: float = 0.0
    cliente_avaliacoes: int = 0
    requer_filtro_palavra_chave: bool = True


def _extrair_numero(texto: str) -> int:
    if not texto:
        return 0
    digitos = "".join(c for c in texto if c.isdigit())
    return int(digitos) if digitos else 0


def _extrair_contador(card: Tag, rotulo: str) -> int:
    """Extrai o número que segue um rótulo tipo 'Propostas:' ou 'Interessados:'.

    O número fica num <b> como nó irmão do texto do rótulo, não dentro do
    próprio texto - por isso usamos find_next() em vez de regex no texto.
    """
    rotulo_tag = card.find(string=lambda t: t and rotulo in t)
    if not rotulo_tag:
        return 0
    numero_tag = rotulo_tag.find_next("b")
    return _extrair_numero(numero_tag.get_text()) if numero_tag else 0


def _extrair_cliente(card: Tag) -> tuple[str, float, int]:
    """Extrai nome, nota e número de avaliações do cliente a partir da listagem.

    Essa informação já vem na própria página de listagem (bloco
    <p class="item-text client">), sem precisar abrir o projeto individual.
    """
    cliente_tag = card.select_one("p.item-text.client")
    if not cliente_tag:
        return "", 0.0, 0

    nome_tag = cliente_tag.select_one("a")
    nome = nome_tag.get_text(strip=True) if nome_tag else ""

    nota_tag = cliente_tag.select_one(".avaliacoes-star")
    nota = float(nota_tag.get("data-score", 0) or 0) if nota_tag else 0.0

    avaliacoes_tag = cliente_tag.select_one(".avaliacoes-text")
    avaliacoes = _extrair_numero(avaliacoes_tag.get_text()) if avaliacoes_tag else 0

    return nome, nota, avaliacoes


def _parse_card(card: Tag) -> Projeto | None:
    try:
        titulo_tag = card.select_one("h1.title a")
        titulo = titulo_tag.get_text(strip=True)
        link = titulo_tag["href"]
        if not link.startswith("http"):
            link = "https://www.99freelas.com.br" + link

        info_tag = card.select_one("p.item-text.information")
        partes = (
            [p.strip() for p in info_tag.get_text(separator="|").split("|") if p.strip()]
            if info_tag
            else []
        )
        categoria = partes[0] if partes else ""
        nivel = partes[1] if len(partes) > 1 else ""

        desc_tag = card.select_one(".description")
        descricao = ""
        if desc_tag:
            descricao = desc_tag.get("data-content") or desc_tag.get_text(strip=True)
            descricao = html.unescape(descricao)

        cliente_nome, cliente_nota, cliente_avaliacoes = _extrair_cliente(card)

        return Projeto(
            id=card.get("data-id", ""),
            titulo=html.unescape(titulo),
            link=link,
            categoria=categoria,
            nivel=nivel,
            propostas=_extrair_contador(card, "Propostas"),
            interessados=_extrair_contador(card, "Interessados"),
            descricao=descricao,
            cliente_nome=cliente_nome,
            cliente_nota=cliente_nota,
            cliente_avaliacoes=cliente_avaliacoes,
        )
    except (AttributeError, KeyError):
        return None


def parse_listagem(html_bruto: str) -> list[Projeto]:
    """Extrai os projetos de um HTML de listagem já baixado."""
    soup = BeautifulSoup(html_bruto, "html.parser")
    cards = soup.select("li.result-item")
    projetos = [_parse_card(card) for card in cards]
    return [p for p in projetos if p is not None]


def buscar_projetos(url: str, requer_filtro_palavra_chave: bool = True) -> list[Projeto]:
    """Baixa e faz o parse de uma página de listagem do 99Freelas."""
    resp = _session.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    projetos = parse_listagem(resp.text)
    for p in projetos:
        p.requer_filtro_palavra_chave = requer_filtro_palavra_chave
    logger.info("%s -> %d projetos", url, len(projetos))
    return projetos


def buscar_projetos_paginado(url: str, max_paginas: int = 1, requer_filtro_palavra_chave: bool = True) -> list[Projeto]:
    """Busca as primeiras `max_paginas` páginas de uma URL de listagem.

    Para na primeira página que não trouxer nenhum projeto novo - tanto faz
    se foi porque acabaram os resultados ou porque o parâmetro de página
    não é o esperado (mais seguro que insistir em páginas vazias).
    """
    separador = "&" if "?" in url else "?"
    todos: list[Projeto] = []
    for pagina in range(1, max_paginas + 1):
        url_pagina = url if pagina == 1 else f"{url}{separador}page={pagina}"
        projetos_da_pagina = buscar_projetos(url_pagina, requer_filtro_palavra_chave)
        if not projetos_da_pagina:
            break
        todos.extend(projetos_da_pagina)
    return todos
