"""Configuração central do gig-scout, lida de variáveis de ambiente."""

import os

# Cada URL vem com uma flag: True = essa categoria é ampla/bagunçada,
# então precisa passar pelo filtro de palavra-chave. False = a categoria
# já é específica o suficiente (confiamos nela), então pulamos o filtro
# de palavra-chave para não descartar projeto bom só por causa de
# fraseado diferente na descrição.
SEARCH_URLS = [
    (
        "https://www.99freelas.com.br/projects?categoria=web-mobile-e-software"
        "&sub-categorias=criacao-e-integracao-com-ia+desenvolvimento-desktop+banco-de-dados"
        "&order=mais-recentes",
        False,
    ),
    (
        "https://www.99freelas.com.br/projects?categoria=suporte-administrativo"
        "&sub-categorias=pesquisa-online+planilhas-e-relatorios"
        "&order=mais-recentes",
        False,
    ),
    (
        "https://www.99freelas.com.br/projects?categoria=web-mobile-e-software"
        "&sub-categorias=outra-web-mobile-e-software"
        "&order=mais-recentes",
        True,
    ),
]

KEYWORDS = [
    "automação", "automatizar", "python", "planilha", "scraping",
    "raspagem", "bot", "chatbot", "whatsapp", "n8n", "ia", "openai",
    "agente", "relatório automático", "api", "integração",
]

MAX_PROPOSALS = 40
MAX_PROJECTS_PER_EMAIL = 8
MAX_PAGINAS_POR_URL = 5

# Mínimo de avaliações que o cliente precisa ter para o projeto não ser
# descartado. 0 = aceita cliente sem nenhuma avaliação também (padrão,
# comportamento igual ao de antes). Suba esse número se quiser ser mais
# rigoroso - o risco de projeto abandonado sem pagamento é maior com
# cliente sem histórico nenhum.
MIN_AVALIACOES_CLIENTE = 0

# Se True, manda um e-mail curto avisando "nada novo" quando não há
# projeto relevante desde a última execução - serve também como sinal de
# que a automação está rodando de verdade, não travada em silêncio.
# Se achar que virou muito e-mail (rodando de 2 em 2h, pode ser bastante),
# muda pra False que ele volta a ficar em silêncio quando não há novidade.
AVISAR_QUANDO_NAO_HOUVER_NOVIDADE = True

EMAIL_FROM = os.environ.get("EMAIL_REMETENTE", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_SENHA_APP", "")
EMAIL_TO = os.environ.get("EMAIL_DESTINATARIO", "")

STATE_FILE = "vistos.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
