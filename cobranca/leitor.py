"""Leitura da planilha CSV de clientes (formato Excel brasileiro, separador ';')."""

import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Cliente:
    nome: str
    email: str
    fatura: str
    valor: Decimal
    vencimento: date
    status: str  # "pendente" ou "pago"


def _converter_valor(texto: str) -> Decimal:
    # Aceita "1.234,56", "1234,56" ou "1234.56"
    texto = texto.replace("R$", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return Decimal(texto)


def _converter_data(texto: str) -> date:
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto.strip(), formato).date()
        except ValueError:
            pass
    raise ValueError(f"Data inválida: {texto!r} (use DD/MM/AAAA)")


def ler_clientes(caminho: str) -> list[Cliente]:
    clientes = []
    # utf-8-sig remove o BOM que o Excel coloca ao salvar CSV
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        for numero, linha in enumerate(csv.DictReader(arquivo, delimiter=";"), start=2):
            try:
                clientes.append(
                    Cliente(
                        nome=linha["nome"].strip(),
                        email=linha["email"].strip(),
                        fatura=linha["fatura"].strip(),
                        valor=_converter_valor(linha["valor"]),
                        vencimento=_converter_data(linha["vencimento"]),
                        status=linha["status"].strip().lower(),
                    )
                )
            except (KeyError, ValueError, ArithmeticError) as erro:
                print(f"[AVISO] Linha {numero} ignorada: {erro}")
    return clientes
