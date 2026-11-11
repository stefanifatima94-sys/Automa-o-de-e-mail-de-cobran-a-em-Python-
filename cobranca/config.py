"""Carrega as configurações do arquivo .env (sem dependências externas)."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    smtp_host: str
    smtp_porta: int
    smtp_usuario: str
    smtp_senha: str
    remetente_nome: str
    remetente_email: str
    empresa: str
    chave_pix: str
    telefone: str
    dias_lembrete: int  # quantos dias antes do vencimento enviar o lembrete


def _ler_env(caminho: str = ".env") -> None:
    arquivo = Path(caminho)
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def carregar_config() -> Config:
    _ler_env()
    return Config(
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_porta=int(os.getenv("SMTP_PORTA", "587")),
        smtp_usuario=os.getenv("SMTP_USUARIO", ""),
        smtp_senha=os.getenv("SMTP_SENHA", ""),
        remetente_nome=os.getenv("REMETENTE_NOME", "Financeiro"),
        remetente_email=os.getenv("REMETENTE_EMAIL", os.getenv("SMTP_USUARIO", "")),
        empresa=os.getenv("EMPRESA", "Minha Empresa"),
        chave_pix=os.getenv("CHAVE_PIX", ""),
        telefone=os.getenv("TELEFONE", ""),
        dias_lembrete=int(os.getenv("DIAS_LEMBRETE", "3")),
    )
