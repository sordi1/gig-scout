"""Montagem e envio dos e-mails: resumo diário e alerta de quebra."""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_APP_PASSWORD, EMAIL_FROM, EMAIL_TO
from scraper import Projeto

logger = logging.getLogger(__name__)


def montar_email(projetos: list[Projeto]) -> str:
    """Versão em texto puro (usada como fallback e quando o e-mail não é enviado)."""
    if not projetos:
        return "Nenhum projeto novo desde a última verificação. Tudo funcionando normalmente."

    separador = "-" * 50
    blocos = [
        f"\n{separador}\n{p.titulo}\n"
        f"Categoria: {p.categoria} | Nível: {p.nivel}\n"
        f"Propostas: {p.propostas} | Interessados: {p.interessados}\n"
        f"Cliente: {p.cliente_nome or 'sem nome'} "
        f"({p.cliente_avaliacoes} avaliações, nota {p.cliente_nota})\n"
        f"Link: {p.link}\n{separador}\n"
        for p in projetos
    ]
    return "\n".join(blocos)


def _cor_propostas(propostas: int) -> str:
    if propostas <= 15:
        return "#16a34a"  # verde - pouca concorrência
    if propostas <= 30:
        return "#ca8a04"  # amarelo - concorrência média
    return "#dc2626"  # vermelho - concorrência alta


def montar_email_html(projetos: list[Projeto]) -> str:
    if not projetos:
        return "<p>Nenhum projeto novo desde a última verificação. Tudo funcionando normalmente.</p>"

    cards = []
    for p in projetos:
        cor = _cor_propostas(p.propostas)
        cliente = p.cliente_nome or "sem nome"
        avaliacao = (
            f"{p.cliente_avaliacoes} avaliações, nota {p.cliente_nota}"
            if p.cliente_avaliacoes
            else "sem avaliação ainda"
        )
        cards.append(f"""
        <div style="border:1px solid #e5e7eb; border-radius:8px; padding:16px;
                    margin-bottom:16px; font-family:Arial, sans-serif;">
          <a href="{p.link}" style="font-size:16px; font-weight:bold;
             color:#1d4ed8; text-decoration:none;">{p.titulo}</a>
          <div style="margin:8px 0; font-size:13px; color:#4b5563;">
            {p.categoria} · {p.nivel} · Cliente: {cliente} ({avaliacao})
          </div>
          <div style="display:inline-block; padding:2px 10px; border-radius:12px;
                      background:{cor}; color:white; font-size:13px; font-weight:bold;">
            {p.propostas} propostas
          </div>
        </div>
        """)

    return f"""
    <html><body style="font-family:Arial, sans-serif; max-width:640px; margin:0 auto;">
      <h2>Projetos novos no 99Freelas</h2>
      {''.join(cards)}
    </body></html>
    """


def enviar_email(corpo_texto: str, corpo_html: str | None = None, assunto: str = "Projetos novos no 99Freelas") -> None:
    if not EMAIL_APP_PASSWORD:
        logger.warning("EMAIL_SENHA_APP não configurada - exibindo no console.")
        print(corpo_texto)
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo_texto, "plain", "utf-8"))
    if corpo_html:
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    logger.info("E-mail enviado para %s", EMAIL_TO)


def alertar_quebra(urls: list[str]) -> None:
    """Avisa que a raspagem não encontrou nada em nenhuma URL - provável mudança no site."""
    lista_urls = "\n".join(f"- {u}" for u in urls)
    corpo = (
        "O gig-scout rodou, mas não encontrou nenhum projeto em nenhuma das "
        "URLs configuradas. Isso costuma acontecer quando o site muda a "
        "estrutura do HTML (os seletores em scraper.py deixam de bater) ou "
        "quando o site começa a exigir JavaScript para montar a listagem.\n\n"
        "URLs verificadas:\n"
        f"{lista_urls}\n\n"
        "Verifique manualmente uma dessas URLs no navegador. Se os projetos "
        "aparecerem normalmente lá, os seletores em scraper.py provavelmente "
        "precisam de ajuste."
    )
    enviar_email(corpo, assunto="[gig-scout] Preciso de manutenção - raspagem retornou vazia")
