"""Decide qual e-mail enviar para cada cliente e preenche o modelo."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from html import escape
from pathlib import Path
from string import Template

from cobranca.config import Config
from cobranca.leitor import Cliente

PASTA_MODELOS = Path(__file__).resolve().parent.parent / "modelos"


@dataclass
class Mensagem:
    tipo: str  # "lembrete", "vence_hoje" ou "atraso"
    assunto: str
    html: str
    texto: str


def formatar_reais(valor: Decimal) -> str:
    texto = f"{valor:,.2f}"  # 1,234.56
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _escolher_tipo(cliente: Cliente, hoje: date, config: Config) -> str | None:
    if cliente.status != "pendente":
        return None
    dias = (cliente.vencimento - hoje).days
    if dias < 0:
        return "atraso"
    if dias == 0:
        return "vence_hoje"
    if dias <= config.dias_lembrete:
        return "lembrete"
    return None


ASSUNTOS = {
    "lembrete": "Lembrete: sua fatura $fatura vence em $vencimento",
    "vence_hoje": "Sua fatura $fatura vence hoje",
    "atraso": "Fatura $fatura em atraso há $dias_atraso dia(s)",
}


def montar_mensagem(cliente: Cliente, hoje: date, config: Config) -> Mensagem | None:
    tipo = _escolher_tipo(cliente, hoje, config)
    if tipo is None:
        return None

    dados = {
        "nome": cliente.nome,
        "fatura": cliente.fatura,
        "valor": formatar_reais(cliente.valor),
        "vencimento": cliente.vencimento.strftime("%d/%m/%Y"),
        "dias_atraso": str(max((hoje - cliente.vencimento).days, 0)),
        "empresa": config.empresa,
        "chave_pix": config.chave_pix,
        "telefone": config.telefone,
    }

    modelo = Template((PASTA_MODELOS / f"{tipo}.html").read_text(encoding="utf-8"))
    corpo_html = modelo.safe_substitute({k: escape(v) for k, v in dados.items()})

    texto = (
        f"Olá, {dados['nome']}.\n\n"
        f"Fatura: {dados['fatura']}\nValor: {dados['valor']}\nVencimento: {dados['vencimento']}\n\n"
        f"Chave PIX: {dados['chave_pix']}\nDúvidas: {dados['telefone']}\n\n{dados['empresa']}"
    )

    return Mensagem(
        tipo=tipo,
        assunto=Template(ASSUNTOS[tipo]).safe_substitute(dados),
        html=corpo_html,
        texto=texto,
    )
