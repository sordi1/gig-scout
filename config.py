"""Configuração central do gig-scout, lida de variáveis de ambiente."""

import os

SEARCH_URLS = [
    "https://www.99freelas.com.br/projects?categoria=web-mobile-e-software"
    "&sub-categorias=criacao-e-integracao-com-ia+desenvolvimento-desktop+banco-de-dados",
    "https://www.99freelas.com.br/projects?categoria=suporte-administrativo"
    "&sub-categorias=pesquisa-online+planilhas-e-relatorios",
]

KEYWORDS = [
    "automação", "automatizar", "python", "planilha", "scraping",
    "raspagem", "bot", "chatbot", "whatsapp", "n8n", "ia", "openai",
    "agente", "relatório automático", "api", "integração",
]

MAX_PROPOSALS = 40
MAX_PROJECTS_PER_EMAIL = 8
MAX_PAGINAS_POR_URL = 3

# Mínimo de avaliações que o cliente precisa ter para o projeto não ser
# descartado. 0 = aceita cliente sem nenhuma avaliação também (padrão,
# comportamento igual ao de antes). Suba esse número se quiser ser mais
# rigoroso - o risco de projeto abandonado sem pagamento é maior com
# cliente sem histórico nenhum.
MIN_AVALIACOES_CLIENTE = 0

EMAIL_FROM = os.environ.get("EMAIL_REMETENTE", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_SENHA_APP", "")
EMAIL_TO = os.environ.get("EMAIL_DESTINATARIO", "")

STATE_FILE = "vistos.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
