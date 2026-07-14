from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from state import carregar_vistos, salvar_vistos


def test_carregar_vistos_arquivo_inexistente(tmp_path):
    caminho = tmp_path / "vistos.json"
    assert carregar_vistos(str(caminho)) == set()


def test_salvar_e_carregar_vistos(tmp_path):
    caminho = tmp_path / "vistos.json"
    salvar_vistos({"1", "2", "3"}, str(caminho))
    assert carregar_vistos(str(caminho)) == {"1", "2", "3"}


def test_arquivo_corrompido_retorna_vazio(tmp_path):
    caminho = tmp_path / "vistos.json"
    caminho.write_text("isso não é json válido{{{", encoding="utf-8")
    assert carregar_vistos(str(caminho)) == set()


def test_arquivo_com_bytes_invalidos_retorna_vazio(tmp_path):
    caminho = tmp_path / "vistos.json"
    caminho.write_bytes(b"\xff\xfe isso n\xe3o \xe9 utf-8 v\xe1lido")
    assert carregar_vistos(str(caminho)) == set()
