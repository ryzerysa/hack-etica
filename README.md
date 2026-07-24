# Audit Arcade para Termux

Este projeto é uma ferramenta visual em Python para o Termux, com interface inspirada em um gabinete arcade e estilo ASCII art.

> Não implemento invasão, roubo de credenciais, acesso não autorizado ou envio de arquivos para aparelhos de terceiros. Esta versão é voltada para auditoria autorizada e diagnóstico seguro em ambientes com permissão.

## Requisitos
- Python 3
- Termux com suporte a terminal
- Comandos Bash como nmcli, iw, ip ou nfc-list podem estar disponíveis dependendo do ambiente

## Instalação
No Termux, rode:

```bash
pkg update && pkg upgrade
pkg install python
cd /path/para/o/projeto
python main.py
```

## Controles
- Setas: navegar
- Enter / A / Space: executar
- Esc / B: voltar
- Q: sair

## Funcionalidades
- Módulo Wi-Fi para consultar interfaces e status de rede
- Módulo Rede para listar dispositivos visíveis na rede local
- Módulo NFC para verificar a disponibilidade de hardware NFC
- Módulo Envio Local para gerar um relatório seguro no dispositivo
