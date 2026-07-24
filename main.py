#!/usr/bin/env python3
"""Painel visual de auditoria autorizada para Termux.

Não implemento invasão, roubo de credenciais, acesso não autorizado
ou envio de arquivos para aparelhos de terceiros. Esta versão oferece
um visual em ASCII art e módulos seguros para diagnóstico de Wi-Fi,
rede local, NFC e exportação local autorizada.
"""

import os
import subprocess
import sys
import textwrap
from datetime import datetime

try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None

from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


class AuditArcadeUI:
    def __init__(self):
        self.running = True
        self.screen = "menu"
        self.selected = 0
        self.menu_items = ["Wi-Fi", "Bluetooth", "Ferramentas", "Relatório", "Sobre"]
        # submenus
        self.wifi_items = ["Scan APs", "Clients", "WPS check", "Channel usage"]
        self.bt_items = ["Bluejacking", "Bluesnarfing", "BLE Spoofing", "Scan Devices"]
        self.ferramentas_items = ["Phishing", "MITM", "DoS", "USB"]
        self.wifi_selected = 0
        self.bt_selected = 0
        self.ferramentas_selected = 0
        self.last_status = "Pronto"
        self.last_output = "Selecione um módulo para iniciar uma análise autorizada."
        self.last_command = ""
        self.message = "Modo seguro ativado"
        self.font = Figlet(font="banner3")
        self.console = Console()

        # ASCII-art icons based on provided image bases (pixel-like blocks)
        self.icons = {
            "Wi-Fi": (
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%@%%%%%%%%%%%%%@%%%%%@%%@%@%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@....*..........:::=....:..::::..-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@....*.........:...-....::.......-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@..:....:........+.....:.......-...::......:.=:.......*..=@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@...:............*.............=....:........=........+..+@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@:...:.::-==--==--++++%+++++++++++++#++++*++++++++*----:--=*::+.:::@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@....-:...........@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#......:.+..=....@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@#....+--:=..:...::....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*........+..=----..::.@@@@@@@@@@@\n"
                "@@@@@@@@@@@@#....-....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:.::..:...@@@@@@@@@@@\n"
                "@@@@@@@@... ::.:.=....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-........-...:@@@@@@@\n"
                "@@@@@@@@....:...:+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:..:*:.:.@@@@@@@\n"
                "@@@@@@@@....::..:+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...:+....@@@@@@@\n"
                "@@@@@@@@.....@@@@@@@@@@@@@@@@@@@@@@@@@@.:::=:..:::::=.:..::::*@@@@@@@@@@@@@@@@@@@@@@@@@:....@@@@@@@\n"
                "@@@@@@@@.....@@@@@@@@@@@@@@@@@@@@@@@@@@....=...::...-...:::..+@@@@@@@@@@@@@@@@@@@@@@@@@:...:@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-...:+........-:.......-.....:..=....-:...@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=....+........-......:.=........=:...-....@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@....=....*....@@@@@@@@@@@@@@@@@@@@@@+....-...-:...*@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@ ..:+....*..:.@@@@@@@@@@@@@@@@@@@@@@+:...-...-::..+@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@:....----+....*....@@@@@@@@@@@@@@@@@@@@@@=....-:..:-----....%@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@:.........@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%....-....%@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@:..::...:.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#...::....%@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@:....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@....:%@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@:....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....%@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            ),
            "Bluetooth": (
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=:::=.:.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.:.=...=..:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=...=.:..::.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=...=.......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@::.=...=...:.......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=...=........:..@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-==#=--+%%%-=---==-====*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=...+@@@...........:+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@--=*=--*@@@@@@@...:+===*+++*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.:.=...+@@@@@@@....:...=...:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=..:+@@@@@@@@@@@...:+---=++++@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@@@@@@...=...+@@@@@@@@@@@:...-...=....@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@@@@@@...=...+@@@@@@@@@@@@@@@*...=....@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@@@@@@...=:..+@@@@@@@@@@@@@@@#.:.=:...@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...:.@@@@@@@@.:.=...+@@@@@@@@@@@.:.:=...-....@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@...=...+@@@@@@@@@@@....=..:.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-----::::=@@@...=::.+@@@@@@%:.:.:---=::--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+..:..=@@@..:=::.+@@@@@@%.....:..:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%**+..-::....=...+@@@......:.###*#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#..-...::.=...=.:...:..::.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@......=...=...:...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...:::=...=.....::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=...=::.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..:=:..=.::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:::=..:=:::...:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@::..:.=.::=:......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%:.:.:::::+:::+:::::::....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:::::.:.:=...+.........:.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*..===*:--===#===*@@@....-==-....-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*..=..-@@@...=:::+@@@@@@@.......::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..::..:::=@@@...=:::+@@@@@@@.:......=:..:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@..:=...+@@@@@@@@@@@.::.=...:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:....@@@@@@@@.::=...+@@@@@@@@@@@.:..=...=....@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@@@@@@..:+...+@@@@@@@@@@@@@@@*...-....@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@.....@@@@@@@@@@@@@...=..:+@@@@@@@@@@@@@@@#...-...:@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..:=..:+@@@@@@@@@@@....=...=....@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..:+:.:+@@@@@@@@@@@....=...-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-=+#==-*@@@@@@%::::====+.:..@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...+.::+@@@@@@@........-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=.::+@@@.:...::.....-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=..:*%%%........@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@...=...=...........@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...+...=...:::.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=...=.:.....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:..=...=...%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...=::.=...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@%@%@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            ),
            "Ferramentas": (
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+=====+=+==+==+===@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...::.........:..:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=..:...:..........:......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+...::...:...:::..:....::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:..:.::.@@@@@@@@@@@@@@@@...:.:.%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@===-::-:...@@@@@@@@@@@@@@@@:...:::+===@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..:-...@@@@@@@@@@@@@@@@@@@@@@@@..:-...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-::=:-:@@@@@@@@@@@@@@@@@@@@@@@@:--=::-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..:-...@@@@@@@@@@@@@@@@@@@@@@@@...-...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..:-...@@@@@@@@@@@@@@@@@@@@@@@@.::-...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...-..:@@@@@@@@@@@@@@@@@@@@@@@@...-..:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...-...@@@@@@@@@@@@@@@@@@@@@@@@..:=::.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:::-:..@@@@@@@@@@@@@@@@@@@@@@@@:.:-...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...-::.@@@@@@@@@@@@@@@@@@@@@@@@...-...@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%:..-...-...:...-...........-:..:...::..-:::...:.@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...-...-...::..:...........:....::.:...-......::@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#...:...-...-...:...:......:....:...........-......:....:@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...:...-...-...-.......:...........-.......:...-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%::.:...-::.-:..:..::.:::%@@@@@@@:::.::.::::-....:::...:.@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#...:...-...-...:........@@@@@@@@...........-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.......-...-........*@@@@@@@@@@@@@@:.......-..........:.@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...:...-...-...:....*@@@@@@@@@@@@@@....::..-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%=++++++*+++*===+++=-#@@@@@@@@@@@@@@-=====++*++++=++=+++-@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...:...-...-...:....*@@@@@@@@@@@@@@....:...-:.........:.@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...:...-...-.........::.@@@@@@@@:::........-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.:.:...-...-...::.......@@@@@@@%.......:...-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.......-...-...:........@@@@@@@%.......:...-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...:...-...-...:........@@@@@@@%...........-......:.....@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%-------+---+---=-----%%%@@@@@@@@@@#--------+-------:---:@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...::..-...-...:...:.@@@@@@@@@@@@@#....:...-............@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%:::-:::=:::=:::::::-:......::..-:.::.::::::=::::::::::-:@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%...:...-...-...:...:.......:...-.......::..-..........:.@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*##%*++#*++#+++*+++****+*+++****+**+++++*++#******+=**#*@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...-:..-...:...-:..........:...........=......::@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%:::=:::-:::-:::-:::::::::::-::.::::::::-::::::::@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            ),
            "Phishing": (
                "  ██████   \n"
                " █      █  \n"
                " █  ██  █  \n"
                " █  ██  █  \n"
                " █      █  \n"
                "  ██████   \n"
                "    ██     \n"
            ),
            "MITM": (
                "   ██  ██  \n"
                "  █  ██  █ \n"
                " █   ██   █\n"
                "  █     █  \n"
                "   █   █   \n"
                "    █ █    \n"
                "     █     \n"
            ),
            "DoS": (
                "    █   █   \n"
                "   █ █ █ █  \n"
                "  █  █ █  █ \n"
                "   █     █  \n"
                "    █   █   \n"
                "     █ █    \n"
                "      █     \n"
            ),
            "USB": (
                "    █████   \n"
                "   █     █  \n"
                "   █ USB █  \n"
                "   █     █  \n"
                "    █████   \n"
                "      █     \n"
                "      █     \n"
            ),
            "Relatório": (
                "  █████████ \n"
                "  █ REPORT █ \n"
                "  █████████ \n"
            ),
            "Sobre": (
                "  █████████ \n"
                "  █  INFO █  \n"
                "  █████████ \n"
            ),
        }

    def run(self) -> None:
        while self.running:
            self.draw()
            key = self.read_key()
            self.handle_key(key)

    def read_key(self) -> str:
        if os.name == "nt" or termios is None or tty is None:
            return input("Escolha: ").strip().lower()

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    return "up"
                if seq == "[B":
                    return "down"
                if seq == "[C":
                    return "right"
                if seq == "[D":
                    return "left"
                return ""
            if ch in {"\r", "\n"}:
                return "enter"
            if ch == "\x03":
                raise KeyboardInterrupt
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_key(self, key: str) -> None:
        if key in {"q", "quit", "sair"}:
            self.running = False
            return

        if self.screen == "menu":
            if key in {"a", "left", "esquerda", "w", "up"}:
                self.selected = (self.selected - 1) % len(self.menu_items)
            elif key in {"d", "right", "direita", "s", "down"}:
                self.selected = (self.selected + 1) % len(self.menu_items)
            elif key in {"enter", "e", "selecionar", ""}:
                self.enter_menu_option()
        elif self.screen == "wifi_menu":
            if key in {"a", "left", "esquerda", "w", "up"}:
                self.wifi_selected = (self.wifi_selected - 1) % len(self.wifi_items)
            elif key in {"d", "right", "direita", "s", "down"}:
                self.wifi_selected = (self.wifi_selected + 1) % len(self.wifi_items)
            elif key in {"enter", "e", "selecionar", ""}:
                self.run_wifi_tool(self.wifi_items[self.wifi_selected])
                self.screen = "report"
            elif key in {"b", "back", "esc"}:
                self.screen = "menu"
        elif self.screen == "bluetooth_menu":
            if key in {"a", "left", "esquerda", "w", "up"}:
                self.bt_selected = (self.bt_selected - 1) % len(self.bt_items)
            elif key in {"d", "right", "direita", "s", "down"}:
                self.bt_selected = (self.bt_selected + 1) % len(self.bt_items)
            elif key in {"enter", "e", "selecionar", ""}:
                self.run_bluetooth_tool(self.bt_items[self.bt_selected])
                self.screen = "report"
            elif key in {"b", "back", "esc"}:
                self.screen = "menu"
        elif self.screen == "ferramentas_menu":
            if key in {"a", "left", "esquerda", "w", "up"}:
                self.ferramentas_selected = (self.ferramentas_selected - 1) % len(self.ferramentas_items)
            elif key in {"d", "right", "direita", "s", "down"}:
                self.ferramentas_selected = (self.ferramentas_selected + 1) % len(self.ferramentas_items)
            elif key in {"enter", "e", "selecionar", ""}:
                self.run_ferramentas_tool(self.ferramentas_items[self.ferramentas_selected])
                self.screen = "report"
            elif key in {"b", "back", "esc"}:
                self.screen = "menu"
        elif self.screen in {"report", "about"}:
            if key in {"enter", "e", "", "b", "back"}:
                self.screen = "menu"

    def enter_menu_option(self) -> None:
        option = self.menu_items[self.selected]
        if option == "Wi-Fi":
            # open Wi-Fi submenu
            self.wifi_selected = 0
            self.screen = "wifi_menu"
            return
        
        if option == "Bluetooth":
            self.bt_selected = 0
            self.screen = "bluetooth_menu"
            return
        if option == "Ferramentas":
            self.ferramentas_selected = 0
            self.screen = "ferramentas_menu"
            return
        elif option == "Relatório":
            self.run_local_export()
        elif option == "Sobre":
            self.screen = "about"
            return
        self.screen = "report"

    def run_phishing_awareness(self) -> None:
        self.last_command = "Checklist de phishing"
        self.last_status = "OK"
        self.last_output = (
            "Checklist seguro de phishing:\n"
            "- Verifique o domínio do remetente\n"
            "- Não clique em links suspeitos\n"
            "- Ative MFA e autenticação forte\n"
            "- Denuncie mensagens suspeitas ao time de segurança"
        )
        self.message = "Treinamento de phishing ativado"
        self.screen = "report"

    def run_mitm_check(self) -> None:
        self.run_bash("(ip neigh 2>/dev/null || arp -n 2>/dev/null || true); echo '---'; (route -n 2>/dev/null || true)")

    def run_dos_guard(self) -> None:
        self.run_bash("(ss -tuln 2>/dev/null || netstat -tuln 2>/dev/null || true); echo '---'; (curl -I -L --max-time 10 https://example.com 2>/dev/null | head -20 || true)")

    def run_usb_audit(self) -> None:
        self.run_bash("(command -v lsusb >/dev/null 2>&1 && lsusb || true); echo '---'; (dmesg 2>/dev/null | tail -20 || true)")

    def run_local_export(self) -> None:
        os.makedirs("exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join("exports", "audit_report.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"Relatório local gerado em {timestamp}\n")
            f.write("Módulo: exportação segura local\n")
            f.write("Este arquivo é salvo apenas no dispositivo local.\n")
        self.last_command = f"salvar em {path}"
        self.last_status = "OK"
        self.last_output = f"Arquivo salvo com sucesso em {path}"
        self.message = "Exportação local concluída"
        self.screen = "report"

    def run_wifi_tool(self, name: str) -> None:
        self.last_command = f"Wi-Fi tool: {name}"
        if name == "Scan APs":
            self.run_bash(
                "(command -v nmcli >/dev/null 2>&1 && nmcli device wifi list || command -v iwlist >/dev/null 2>&1 && iwlist scan 2>/dev/null || true)"
            )
        elif name == "Clients":
            self.run_bash("(arp -a 2>/dev/null || ip neigh 2>/dev/null || true)")
        elif name == "WPS check":
            self.run_bash(
                "(command -v wash >/dev/null 2>&1 && wash --scan 2>/dev/null | head -20 || echo 'WPS scan não disponível. Instale wash ou use reaver em laboratório autorizado.')"
            )
        elif name == "Channel usage":
            self.run_bash(
                "(command -v iw >/dev/null 2>&1 && iw dev wlan0 scan dump 2>/dev/null | grep -E 'frequency|channel' || command -v iwlist >/dev/null 2>&1 && iwlist wlan0 channel 2>/dev/null | grep -E 'Channel|Frequency' || true)"
            )
        self.screen = "report"

    def run_bluetooth_tool(self, name: str) -> None:
        self.last_command = f"Bluetooth tool: {name}"
        if name == "Bluejacking":
            self.run_bash(
                "(command -v bluetoothctl >/dev/null 2>&1 && bluetoothctl --timeout 5 scan on >/dev/null 2>&1 && bluetoothctl devices || echo 'bluetoothctl não disponível.')"
            )
            self.last_status = "INFO"
        elif name == "Bluesnarfing":
            self.run_bash(
                "(command -v sdptool >/dev/null 2>&1 && sdptool browse || echo 'sdptool não disponível para descobrir serviços Bluetooth.')"
            )
            self.last_status = "INFO"
        elif name == "BLE Spoofing":
            self.run_bash(
                "(command -v hcitool >/dev/null 2>&1 && timeout 5 hcitool lescan 2>/dev/null || echo 'hcitool não disponível.')"
            )
            self.last_status = "INFO"
        elif name == "Scan Devices":
            self.run_bash(
                "(command -v bluetoothctl >/dev/null 2>&1 && bluetoothctl --timeout 5 scan on >/dev/null 2>&1 && bluetoothctl devices || command -v hcitool >/dev/null 2>&1 && timeout 5 hcitool scan 2>/dev/null || echo 'Nenhuma ferramenta Bluetooth disponível.')"
            )
            self.last_status = "OK"
        self.screen = "report"

    def run_ferramentas_tool(self, name: str) -> None:
        self.last_command = f"Ferramentas tool: {name}"
        if name == "Phishing":
            self.run_phishing_awareness()
            return
        elif name == "MITM":
            self.run_mitm_check()
            return
        elif name == "DoS":
            self.run_dos_guard()
            return
        elif name == "USB":
            self.run_usb_audit()
            return
        self.screen = "report"

    def run_bash(self, command: str) -> None:
        self.last_command = command
        self.message = "Executando diagnóstico seguro"
        try:
            proc = subprocess.run(["bash", "-lc", command], capture_output=True, text=True, timeout=25)
            output = (proc.stdout + proc.stderr).strip()
            if not output:
                output = "Sem saída do comando."
            self.last_output = output
            self.last_status = "OK"
        except FileNotFoundError:
            self.last_status = "ERRO"
            self.last_output = "O ambiente não possui o comando bash necessário."
        except subprocess.TimeoutExpired:
            self.last_status = "ERRO"
            self.last_output = "O comando excedeu o tempo limite de execução."

    def draw(self) -> None:
        self.console.clear()
        banner = self.font.renderText("ARCADE")
        title = Text(banner, style="bold yellow")
        self.console.print(Panel(title, border_style="yellow", box=box.DOUBLE))

        if self.screen == "menu":
            self.draw_menu()
        elif self.screen == "wifi_menu":
            self.draw_wifi_menu()
        elif self.screen == "bluetooth_menu":
            self.draw_bluetooth_menu()
        elif self.screen == "report":
            self.draw_report()
        elif self.screen == "about":
            self.draw_about()

    def draw_menu(self) -> None:
        # show ASCII icon for selected item
        selected_item = self.menu_items[self.selected]
        icon = self.icons.get(selected_item, "")
        icon_panel = Panel(Text(icon, style="yellow"), title=selected_item, border_style="yellow", box=box.SQUARE)
        self.console.print(icon_panel)

        table = Table(title="Menu principal", box=box.SQUARE, show_header=False)
        table.add_column("Opção", style="bold yellow")
        for idx, item in enumerate(self.menu_items):
            style = "bold black on yellow" if idx == self.selected else "white"
            table.add_row(f"> {item}" if idx == self.selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[yellow]Setas / A/D / W/S[/yellow] para navegar\n[yellow]Enter[/yellow] para selecionar\n[yellow]Q[/yellow] para sair", border_style="yellow"))

    def draw_wifi_menu(self) -> None:
        selected = self.wifi_items[self.wifi_selected]
        title = Text(self.font.renderText(selected), style="bold yellow")
        self.console.print(Panel(title, border_style="yellow", box=box.SQUARE))
        table = Table(title="Wi‑Fi Ferramentas", box=box.SIMPLE, show_header=False)
        table.add_column("Opção", style="bold yellow")
        for idx, item in enumerate(self.wifi_items):
            style = "bold black on yellow" if idx == self.wifi_selected else "white"
            table.add_row(f"> {item}" if idx == self.wifi_selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[yellow]Setas / A/D / W/S[/yellow] para navegar\n[yellow]Enter[/yellow] executar\n[yellow]B[/yellow] voltar", border_style="yellow"))

    def draw_bluetooth_menu(self) -> None:
        selected = self.bt_items[self.bt_selected]
        title = Text(self.font.renderText(selected), style="bold yellow")
        self.console.print(Panel(title, border_style="yellow", box=box.SQUARE))
        table = Table(title="Bluetooth Ferramentas", box=box.SIMPLE, show_header=False)
        table.add_column("Opção", style="bold yellow")
        for idx, item in enumerate(self.bt_items):
            style = "bold black on yellow" if idx == self.bt_selected else "white"
            table.add_row(f"> {item}" if idx == self.bt_selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[yellow]Setas / A/D / W/S[/yellow] para navegar\n[yellow]Enter[/yellow] executar\n[yellow]B[/yellow] voltar", border_style="yellow"))

    def draw_ferramentas_menu(self) -> None:
        selected = self.ferramentas_items[self.ferramentas_selected]
        title = Text(self.font.renderText(selected), style="bold yellow")
        self.console.print(Panel(title, border_style="yellow", box=box.SQUARE))
        table = Table(title="Ferramentas", box=box.SIMPLE, show_header=False)
        table.add_column("Opção", style="bold yellow")
        for idx, item in enumerate(self.ferramentas_items):
            style = "bold black on yellow" if idx == self.ferramentas_selected else "white"
            table.add_row(f"> {item}" if idx == self.ferramentas_selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[yellow]Setas / A/D / W/S[/yellow] para navegar\n[yellow]Enter[/yellow] executar\n[yellow]B[/yellow] voltar", border_style="yellow"))

    def draw_report(self) -> None:
        panel = Panel.fit(
            f"[bold yellow]Comando:[/bold yellow] {self.last_command}\n[bold yellow]Status:[/bold yellow] {self.last_status}\n\n{self.last_output}",
            title="Relatório",
            border_style="yellow",
            box=box.ROUNDED,
        )
        self.console.print(panel)

    def draw_about(self) -> None:
        panel = Panel.fit(
            "Painel visual para auditoria autorizada.\nInclui módulos seguros de Wi-Fi, phishing awareness, MITM, DoS e USB audit.\nUse apenas em ambientes onde você tenha permissão.",
            title="Sobre",
            border_style="yellow",
            box=box.ROUNDED,
        )
        self.console.print(panel)


def main() -> None:
    app = AuditArcadeUI()
    app.run()


if __name__ == "__main__":
    main()
