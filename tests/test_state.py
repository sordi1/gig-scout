from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from state import carregar_vistos, salvar_vistos


def test_carregar_vistos_arquivo_inexistente(tmp_path):
    caminho = tmp_path / "vistos.json"
    assert carregar_vistos(str(caminho)) == []


def test_salvar_e_carregar_vistos(tmp_path):
    caminho = tmp_path / "vistos.json"
    salvar_vistos(["1", "2", "3"], str(caminho))
    assert carregar_vistos(str(caminho)) == ["1", "2", "3"]


def test_arquivo_corrompido_retorna_vazio(tmp_path):
    caminho = tmp_path / "vistos.json"
    caminho.write_text("isso não é json válido{{{", encoding="utf-8")
    assert carregar_vistos(str(caminho)) == []


def test_arquivo_com_bytes_invalidos_retorna_vazio(tmp_path):
    caminho = tmp_path / "vistos.json"
    caminho.write_bytes(b"\xff\xfe isso n\xe3o \xe9 utf-8 v\xe1lido")
    assert carregar_vistos(str(caminho)) == []


def test_trunca_descartando_os_mais_antigos_nao_os_mais_recentes(tmp_path, monkeypatch):
    # Este é o bug que o Cursor apontou: usar set() perdia a ordem, e o
    # corte de MAX_STORED_IDS podia descartar IDs vistos há pouco tempo em
    # vez dos mais antigos. Com lista ordenada, o corte é sempre no início.
    import state
    monkeypatch.setattr(state, "MAX_STORED_IDS", 3)

    caminho = tmp_path / "vistos.json"
    ids_em_ordem = ["antigo-1", "antigo-2", "recente-1", "recente-2", "recente-3"]
    salvar_vistos(ids_em_ordem, str(caminho))

    resultado = carregar_vistos(str(caminho))
    assert resultado == ["recente-1", "recente-2", "recente-3"]
    assert "antigo-1" not in resultado
    assert "antigo-2" not in resultado
