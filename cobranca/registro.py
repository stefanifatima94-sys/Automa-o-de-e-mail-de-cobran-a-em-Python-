"""Histórico de envios em CSV — evita mandar o mesmo e-mail duas vezes no mesmo dia."""

import csv
from datetime import date, datetime
from pathlib import Path

from cobranca.leitor import Cliente

CAMPOS = ["data_hora", "email", "nome", "fatura", "tipo", "resultado"]


class RegistroEnvios:
    def __init__(self, caminho: str):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._enviados: set[tuple[str, str, str]] = set()
        if self.caminho.exists():
            with open(self.caminho, encoding="utf-8", newline="") as arquivo:
                for linha in csv.DictReader(arquivo, delimiter=";"):
                    if linha["resultado"] == "enviado":
                        dia = linha["data_hora"][:10]
                        self._enviados.add((linha["email"], linha["fatura"], dia))

    def ja_enviado_hoje(self, email: str, fatura: str, hoje: date) -> bool:
        return (email, fatura, hoje.isoformat()) in self._enviados

    def registrar(self, cliente: Cliente, tipo: str, resultado: str) -> None:
        novo = not self.caminho.exists()
        agora = datetime.now()
        with open(self.caminho, "a", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS, delimiter=";")
            if novo:
                escritor.writeheader()
            escritor.writerow({
                "data_hora": agora.isoformat(timespec="seconds"),
                "email": cliente.email,
                "nome": cliente.nome,
                "fatura": cliente.fatura,
                "tipo": tipo,
                "resultado": resultado,
            })
        if resultado == "enviado":
            self._enviados.add((cliente.email, cliente.fatura, agora.date().isoformat()))
