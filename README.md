# Automação de e-mail de cobrança

Lê uma planilha de clientes e envia automaticamente e-mails de cobrança:

| Situação da fatura                         | E-mail enviado       |
|--------------------------------------------|----------------------|
| Vence nos próximos `DIAS_LEMBRETE` dias     | Lembrete             |
| Vence hoje                                 | Vence hoje           |
| Vencida                                    | Cobrança de atraso   |
| Paga, ou vence depois do prazo de lembrete | Nada                 |

O mesmo e-mail nunca é enviado duas vezes no mesmo dia (o histórico fica em `logs/envios.csv`).

## 1. Instalar o Python

1. Baixe em <https://www.python.org/downloads/> (versão 3.10 ou superior).
2. Na instalação, **marque "Add python.exe to PATH"**.
3. No VS Code, instale a extensão **Python** (o VS Code vai sugerir automaticamente).

Não é preciso instalar nenhuma biblioteca: o projeto usa só a biblioteca padrão do Python.

## 2. Configurar

1. Copie `.env.example` para `.env` e preencha com seus dados de e-mail.
2. **Gmail:** é preciso ativar a verificação em duas etapas e criar uma
   [Senha de app](https://myaccount.google.com/apppasswords). Use essa senha em `SMTP_SENHA`.
3. Edite `dados/clientes.csv` (pode abrir no Excel; salve como *CSV separado por ponto e vírgula*).

Colunas da planilha: `nome;email;fatura;valor;vencimento;status`
- `valor`: `1.250,00`
- `vencimento`: `DD/MM/AAAA`
- `status`: `pendente` ou `pago`

## 3. Executar

No terminal do VS Code:

```bash
python main.py            # simulação: mostra o que seria enviado, sem enviar
python main.py --enviar   # envia de verdade
```

> Se o comando `python` não for reconhecido no Windows, use `py` no lugar (ex.: `py main.py`).

Ou pressione **F5** e escolha "Cobrança: simular" ou "Cobrança: ENVIAR e-mails".

**Dica:** teste primeiro colocando o seu próprio e-mail na planilha.

## 4. Personalizar

Os textos dos e-mails ficam em `modelos/` (`lembrete.html`, `vence_hoje.html`, `atraso.html`).
Variáveis disponíveis: `$nome`, `$fatura`, `$valor`, `$vencimento`, `$dias_atraso`,
`$empresa`, `$chave_pix`, `$telefone`.

## 5. Rodar automaticamente todo dia (opcional)

Use o **Agendador de Tarefas do Windows**:
1. Criar Tarefa Básica → Diariamente → horário desejado.
2. Ação: Iniciar um programa → Programa: `python` → Argumentos: `main.py --enviar`
   → Iniciar em: a pasta deste projeto.

## Estrutura

```
main.py                 # ponto de entrada
cobranca/
  config.py             # lê o .env
  leitor.py             # lê a planilha CSV
  mensagens.py          # escolhe o tipo de e-mail e preenche o modelo
  enviador.py           # envio via SMTP
  registro.py           # histórico de envios (evita duplicados)
modelos/                # textos HTML dos e-mails
dados/clientes.csv      # planilha de exemplo
```
