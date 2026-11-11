"""
Automação de e-mail de cobrança.

Uso:
    python main.py              -> modo simulação (mostra o que seria enviado)
    python main.py --enviar     -> envia os e-mails de verdade
    python main.py --arquivo dados/outra_planilha.csv
"""

import argparse
import sys
from datetime import date

from cobranca.config import carregar_config
from cobranca.leitor import ler_clientes
from cobranca.mensagens import montar_mensagem
from cobranca.enviador import EnviadorEmail
from cobranca.registro import RegistroEnvios


def main() -> int:
    parser = argparse.ArgumentParser(description="Envio automático de e-mails de cobrança")
    parser.add_argument("--enviar", action="store_true", help="Envia de verdade (sem isso, apenas simula)")
    parser.add_argument("--arquivo", default="dados/clientes.csv", help="Planilha CSV de clientes")
    args = parser.parse_args()

    config = carregar_config()
    hoje = date.today()
    clientes = ler_clientes(args.arquivo)
    registro = RegistroEnvios("logs/envios.csv")

    modo = "ENVIO REAL" if args.enviar else "SIMULAÇÃO (use --enviar para enviar)"
    print(f"=== Cobrança {hoje:%d/%m/%Y} | {modo} ===\n")

    enviador = EnviadorEmail(config) if args.enviar else None
    enviados = ignorados = erros = 0

    for cliente in clientes:
        mensagem = montar_mensagem(cliente, hoje, config)
        if mensagem is None:
            ignorados += 1
            continue

        if registro.ja_enviado_hoje(cliente.email, cliente.fatura, hoje):
            print(f"[JÁ ENVIADO HOJE] {cliente.nome} - fatura {cliente.fatura}")
            ignorados += 1
            continue

        print(f"[{mensagem.tipo.upper()}] {cliente.nome} <{cliente.email}> - {mensagem.assunto}")

        if enviador is None:
            continue

        try:
            enviador.enviar(cliente.email, mensagem.assunto, mensagem.html, mensagem.texto)
            registro.registrar(cliente, mensagem.tipo, "enviado")
            enviados += 1
        except Exception as erro:  # noqa: BLE001 - registra qualquer falha e segue para o próximo
            print(f"   ERRO: {erro}")
            registro.registrar(cliente, mensagem.tipo, f"erro: {erro}")
            erros += 1

    if enviador:
        enviador.fechar()

    print(f"\nResumo: {enviados} enviados, {ignorados} ignorados, {erros} erros.")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
