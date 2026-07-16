from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from notifier import montar_email_html
from scraper import Projeto


def _projeto(**kwargs) -> Projeto:
    base = dict(
        id="1", titulo="", link="", categoria="", nivel="",
        propostas=10, interessados=10, descricao="",
    )
    base.update(kwargs)
    return Projeto(**base)


def test_titulo_com_caractere_html_e_escapado():
    # Sem escape, um título com "<" ou "&" quebrava o layout do e-mail
    projeto = _projeto(titulo="Automação <script>alert(1)</script> & Cia")
    resultado = montar_email_html([projeto])
    assert "<script>alert(1)</script>" not in resultado
    assert "&lt;script&gt;" in resultado


def test_email_vazio_nao_quebra():
    assert "Nenhum projeto novo" in montar_email_html([])


def test_descricao_longa_e_truncada():
    projeto = _projeto(titulo="Projeto", descricao="x" * 300)
    resultado = montar_email_html([projeto])
    assert "…" in resultado
