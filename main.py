"""gig-scout: monitora projetos novos no 99Freelas e avisa por e-mail."""

from __future__ import annotations

import logging

from config import MAX_PAGINAS_POR_URL, SEARCH_URLS
from filters import filtrar_e_ordenar
from notifier import alertar_quebra, enviar_email, montar_email, montar_email_html
from scraper import buscar_projetos_paginado
from state import carregar_vistos, salvar_vistos

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    todos_os_projetos = []
    for url in SEARCH_URLS:
        try:
            todos_os_projetos.extend(buscar_projetos_paginado(url, MAX_PAGINAS_POR_URL))
        except Exception:
            logger.exception("Falha ao buscar %s", url)

    if not todos_os_projetos:
        logger.error("Nenhum projeto encontrado em nenhuma URL - possível quebra na raspagem.")
        alertar_quebra(SEARCH_URLS)
        return

    relevantes = filtrar_e_ordenar(todos_os_projetos)

    vistos = carregar_vistos()
    novos = [p for p in relevantes if p.id not in vistos]
    logger.info("%d relevantes, %d novos desde a última execução", len(relevantes), len(novos))

    if not novos:
        logger.info("Nada novo - e-mail não enviado.")
        return

    enviar_email(montar_email(novos), montar_email_html(novos))

    vistos.update(p.id for p in novos)
    salvar_vistos(vistos)


if __name__ == "__main__":
    main()
