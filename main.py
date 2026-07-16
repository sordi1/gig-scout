"""gig-scout: monitora projetos novos no 99Freelas e avisa por e-mail."""

from __future__ import annotations

import logging

from config import AVISAR_QUANDO_NAO_HOUVER_NOVIDADE, MAX_PAGINAS_POR_URL, SEARCH_URLS
from filters import filtrar_e_ordenar
from notifier import alertar_quebra, enviar_email, montar_email, montar_email_html
from scraper import buscar_projetos_paginado
from state import carregar_vistos, salvar_vistos

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    todos_os_projetos = []
    for url, requer_filtro_palavra_chave in SEARCH_URLS:
        try:
            todos_os_projetos.extend(
                buscar_projetos_paginado(url, MAX_PAGINAS_POR_URL, requer_filtro_palavra_chave)
            )
        except Exception:
            logger.exception("Falha ao buscar %s", url)

    if not todos_os_projetos:
        logger.error("Nenhum projeto encontrado em nenhuma URL - possível quebra na raspagem.")
        alertar_quebra([url for url, _ in SEARCH_URLS])
        return

    # Dedup por ID - o mesmo projeto pode, em tese, aparecer em mais de uma
    # URL de busca (categorias combinadas). Mantém a primeira ocorrência.
    vistos_nesta_execucao = set()
    projetos_unicos = []
    for p in todos_os_projetos:
        if p.id not in vistos_nesta_execucao:
            vistos_nesta_execucao.add(p.id)
            projetos_unicos.append(p)

    relevantes = filtrar_e_ordenar(projetos_unicos)

    vistos = carregar_vistos()
    vistos_set = set(vistos)  # set só pra checagem O(1), a ordem fica na lista `vistos`
    novos = [p for p in relevantes if p.id not in vistos_set]
    logger.info("%d relevantes, %d novos desde a última execução", len(relevantes), len(novos))

    if not novos:
        if AVISAR_QUANDO_NAO_HOUVER_NOVIDADE:
            enviar_email(
                montar_email(novos),
                montar_email_html(novos),
                assunto="gig-scout: nenhum projeto novo por enquanto",
            )
            logger.info("Nada novo - aviso enviado.")
        else:
            logger.info("Nada novo - e-mail não enviado (AVISAR_QUANDO_NAO_HOUVER_NOVIDADE=False).")
        return

    enviar_email(montar_email(novos), montar_email_html(novos))

    vistos.extend(p.id for p in novos)
    salvar_vistos(vistos)


if __name__ == "__main__":
    main()
