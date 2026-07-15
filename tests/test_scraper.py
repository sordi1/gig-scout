from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scraper import _extrair_numero, parse_listagem

FIXTURE = Path(__file__).parent / "fixture_listagem.html"


def test_extrair_numero_com_digitos():
    assert _extrair_numero("Propostas: 85") == 85


def test_extrair_numero_sem_digitos():
    assert _extrair_numero("nenhum número aqui") == 0


def test_extrair_numero_vazio():
    assert _extrair_numero("") == 0


def test_parse_listagem_extrai_projetos_reais():
    html_bruto = FIXTURE.read_text(encoding="utf-8")
    projetos = parse_listagem(html_bruto)

    assert len(projetos) == 3
    assert projetos[0].titulo == "Pesquisador de pautas Youtube"
    assert projetos[0].propostas == 85
    assert projetos[0].categoria == "Pesquisa Online"
    assert projetos[0].nivel == "Iniciante"


def test_parse_listagem_extrai_dados_do_cliente():
    html_bruto = FIXTURE.read_text(encoding="utf-8")
    projetos = parse_listagem(html_bruto)

    primeiro = projetos[0]
    assert primeiro.cliente_nome == "Kaua L."
    assert primeiro.cliente_nota == 5.0
    assert primeiro.cliente_avaliacoes == 1


def test_parse_listagem_html_vazio_nao_quebra():
    assert parse_listagem("<html></html>") == []


def test_paginacao_para_quando_pagina_vem_vazia(monkeypatch):
    import scraper

    paginas_chamadas = []

    def fake_buscar_projetos(url, requer_filtro_palavra_chave=True):
        paginas_chamadas.append(url)
        if "page=3" in url:
            return []
        return [scraper.Projeto(id=url, titulo="x", link="", categoria="", nivel="", propostas=1, interessados=1)]

    monkeypatch.setattr(scraper, "buscar_projetos", fake_buscar_projetos)
    resultado = scraper.buscar_projetos_paginado("https://exemplo.com/projects", max_paginas=5)

    assert len(resultado) == 2
    assert len(paginas_chamadas) == 3
