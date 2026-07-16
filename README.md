# gig-scout

Monitor automático de projetos freelance. Raspa as listagens, filtra pelo que é relevante, ordena pelos projetos com menos concorrência e avisa por e-mail — pronto pra você revisar e decidir em segundos.

Roda sozinho, de 2 em 2 horas, via GitHub Actions.

## Por quê

Marketplaces de freelance publicam dezenas de projetos por dia, espalhados em várias categorias. Encontrar manualmente os que valem a pena — pouca concorrência, dentro do escopo certo, cliente com histórico — consome tempo que poderia ir para o trabalho em si. Este projeto automatiza essa triagem.

## Como funciona

```
buscar_projetos_paginado()  →  filtrar_e_ordenar()  →  enviar_email()
      (scraper.py)               (filters.py)          (notifier.py)
```

1. **Raspagem** (`scraper.py`) — baixa até `MAX_PAGINAS_POR_URL` páginas de cada listagem e extrai título, descrição completa, número de propostas/interessados e dados do cliente (nome, nota, quantidade de avaliações) — tudo já disponível na própria listagem, sem precisar abrir cada projeto individualmente.
2. **Filtro** (`filters.py`) — descarta projetos com mais propostas que o teto configurado, com cliente abaixo do mínimo de avaliações exigido (`MIN_AVALIACOES_CLIENTE`, 0 por padrão), e mantém só os que batem com um conjunto de palavras-chave usando limite de palavra via regex (evita falso positivo — por exemplo, `ia` não bate dentro de `residência`).
3. **Estado** (`state.py`) — guarda os IDs de projetos já notificados, para não repetir o mesmo projeto a cada execução.
4. **Notificação** (`notifier.py`) — monta e envia o e-mail em HTML (com fallback em texto puro) com o resumo. Se a raspagem retornar zero projetos em todas as URLs, envia um alerta de manutenção em vez de falhar silenciosamente.

O objetivo é reduzir o trabalho de garimpar projeto bom manualmente — a decisão de quais responder, e o texto da proposta, continuam sendo feitos por fora, sem automação.

## Rodando localmente

```bash
pip install -r requirements.txt
export EMAIL_REMETENTE="seu@gmail.com"
export EMAIL_SENHA_APP="sua-senha-de-app"        # não é a senha normal da conta
export EMAIL_DESTINATARIO="seu@email.com"
python main.py
```

## Rodando os testes

```bash
pip install -r requirements-dev.txt
pytest -v
```

Os testes de raspagem usam uma página real do site como fixture (`tests/fixture_listagem.html`), não HTML inventado — validam contra a estrutura de verdade.

## Rodando sozinho (GitHub Actions)

O workflow em `.github/workflows/monitor.yml`:
- roda os testes a cada push na branch `main`;
- executa o monitor a cada 2 horas, das 8h às 22h (horário de Brasília);
- guarda o estado (`vistos.json`) entre execuções via cache do Actions, sem poluir o histórico do repositório com commits automáticos.

Requer 3 secrets configurados em *Settings → Secrets and variables → Actions*: `EMAIL_REMETENTE`, `EMAIL_SENHA_APP`, `EMAIL_DESTINATARIO`.

## Stack

Python 3.12 · requests · BeautifulSoup4 · pytest · GitHub Actions
