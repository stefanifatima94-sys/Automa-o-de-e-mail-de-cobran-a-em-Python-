"""Envio de e-mails via SMTP."""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from cobranca.config import Config


class EnviadorEmail:
    def __init__(self, config: Config):
        if not config.smtp_usuario or not config.smtp_senha:
            raise SystemExit("Configure SMTP_USUARIO e SMTP_SENHA no arquivo .env antes de enviar.")
        self.config = config
        contexto = ssl.create_default_context()
        if config.smtp_porta == 465:
            self.servidor = smtplib.SMTP_SSL(config.smtp_host, config.smtp_porta, context=contexto, timeout=30)
        else:
            self.servidor = smtplib.SMTP(config.smtp_host, config.smtp_porta, timeout=30)
            self.servidor.starttls(context=contexto)
        self.servidor.login(config.smtp_usuario, config.smtp_senha)

    def enviar(self, destinatario: str, assunto: str, html: str, texto: str) -> None:
        msg = EmailMessage()
        msg["From"] = formataddr((self.config.remetente_nome, self.config.remetente_email))
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(texto)
        msg.add_alternative(html, subtype="html")
        self.servidor.send_message(msg)

    def fechar(self) -> None:
        try:
            self.servidor.quit()
        except smtplib.SMTPException:
            pass
