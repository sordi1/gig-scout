from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from filters import filtrar_e_ordenar
from scraper import Projeto


def _projeto(**kwargs) -> Projeto:
    base = dict(
        id="1", titulo="", link="", categoria="", nivel="",
        propostas=10, interessados=10, descricao="",
    )
    base.update(kwargs)
    return Projeto(**base)


def test_projeto_com_palavra_chave_passa():
    projetos = [_projeto(titulo="Criar agente de IA para WhatsApp")]
    assert len(filtrar_e_ordenar(projetos)) == 1


def test_projeto_sem_palavra_chave_e_descartado():
    projetos = [_projeto(titulo="Editar vídeo institucional")]
    assert filtrar_e_ordenar(projetos) == []


def test_falso_positivo_ia_dentro_de_residencia_nao_bate():
    # "residência" contém "ia" como substring - não deve bater sem \b
    projetos = [_projeto(titulo="Modelagem 3D para residência", descricao="projeto arquitetônico")]
    assert filtrar_e_ordenar(projetos) == []


def test_falso_positivo_api_dentro_de_capital_nao_bate():
    projetos = [_projeto(titulo="Assessoria de capital de giro")]
    assert filtrar_e_ordenar(projetos) == []


def test_acima_do_teto_de_propostas_e_descartado():
    projetos = [_projeto(titulo="Automação em Python", propostas=999)]
    assert filtrar_e_ordenar(projetos) == []


def test_ordena_por_menos_propostas_primeiro():
    projetos = [
        _projeto(id="a", titulo="Python bot", propostas=30),
        _projeto(id="b", titulo="Python bot", propostas=5),
        _projeto(id="c", titulo="Python bot", propostas=15),
    ]
    resultado = filtrar_e_ordenar(projetos)
    assert [p.id for p in resultado] == ["b", "c", "a"]


def test_cliente_sem_avaliacao_e_descartado_quando_exigido(monkeypatch):
    import filters

    monkeypatch.setattr(filters, "MIN_AVALIACOES_CLIENTE", 1)
    projetos = [_projeto(titulo="Automação Python", cliente_avaliacoes=0)]
    assert filtrar_e_ordenar(projetos) == []


def test_cliente_sem_avaliacao_passa_por_padrao():
    # MIN_AVALIACOES_CLIENTE = 0 por padrão - não deve excluir ninguém por isso
    projetos = [_projeto(titulo="Automação Python", cliente_avaliacoes=0)]
    assert len(filtrar_e_ordenar(projetos)) == 1


def test_categoria_confiavel_pula_filtro_de_palavra_chave():
    # requer_filtro_palavra_chave=False = categoria específica (ex: Criação
    # & Integração com IA) - confiamos nela mesmo sem bater keyword no texto
    projetos = [_projeto(
        titulo="Preciso de ajuda com um sistema",
        descricao="nada aqui bate com nenhuma palavra-chave da lista",
        requer_filtro_palavra_chave=False,
    )]
    assert len(filtrar_e_ordenar(projetos)) == 1


def test_categoria_outra_exige_palavra_chave():
    # requer_filtro_palavra_chave=True (padrão) = categoria "Outra", ampla
    # demais - só passa se bater alguma palavra-chave de verdade
    projetos = [_projeto(
        titulo="Preciso de ajuda com um sistema",
        descricao="nada aqui bate com nenhuma palavra-chave da lista",
        requer_filtro_palavra_chave=True,
    )]
    assert filtrar_e_ordenar(projetos) == []


def test_categoria_confiavel_ainda_respeita_teto_de_propostas():
    # Pular o filtro de palavra-chave não deve pular os outros filtros
    projetos = [_projeto(
        titulo="Qualquer coisa", propostas=999, requer_filtro_palavra_chave=False,
    )]
    assert filtrar_e_ordenar(projetos) == []


def test_cliente_com_nota_baixa_e_descartado_quando_exigido(monkeypatch):
    import filters

    monkeypatch.setattr(filters, "MIN_NOTA_CLIENTE", 4.0)
    projetos = [_projeto(
        titulo="Automação Python", cliente_avaliacoes=50, cliente_nota=2.0,
    )]
    assert filtrar_e_ordenar(projetos) == []


def test_cliente_sem_nenhuma_avaliacao_nao_e_penalizado_pela_nota(monkeypatch):
    # cliente novo (nota 0.0 porque nunca foi avaliado) não deveria ser
    # tratado como se tivesse nota ruim
    import filters

    monkeypatch.setattr(filters, "MIN_NOTA_CLIENTE", 4.0)
    projetos = [_projeto(
        titulo="Automação Python", cliente_avaliacoes=0, cliente_nota=0.0,
    )]
    assert len(filtrar_e_ordenar(projetos)) == 1
