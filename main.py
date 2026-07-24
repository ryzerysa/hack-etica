#!/usr/bin/env python3
"""Painel visual de auditoria autorizada para Termux.

Não implemento invasão, roubo de credenciais, acesso não autorizado
ou envio de arquivos para aparelhos de terceiros. Esta versão oferece
um visual em ASCII art e módulos seguros para diagnóstico de Wi-Fi,
rede local, NFC e exportação local autorizada.
"""

from curses import echo
import os
import subprocess
import sys
import textwrap
from datetime import datetime
from time import sleep

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
        self.wifi_items = ["Scan APs", "Connect open AP", "Disconnect Wi-Fi", "Connection status"]
        self.bt_items = ["Bluejacking", "Bluesnarfing", "BLE Spoofing", "Scan Devices"]
        self.ferramentas_items = ["Phishing", "MITM", "DoS", "USB", "Network scan"]
        self.bt_devices = []
        self.bt_device_selected = 0
        self.bt_action_items = ["Connect", "Pair", "Disconnect", "Info"]
        self.bt_action_selected = 0
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
            elif key in {"b", "back", "esc"}:
                self.screen = "menu"
        elif self.screen == "bluetooth_device_menu":
            if key in {"a", "left", "esquerda", "w", "up"}:
                self.bt_device_selected = (self.bt_device_selected - 1) % len(self.bt_devices)
            elif key in {"d", "right", "direita", "s", "down"}:
                self.bt_device_selected = (self.bt_device_selected + 1) % len(self.bt_devices)
            elif key in {"enter", "e", "selecionar", ""}:
                self.bt_action_selected = 0
                self.screen = "bluetooth_device_actions"
            elif key in {"b", "back", "esc"}:
                self.screen = "bluetooth_menu"
        elif self.screen == "bluetooth_device_actions":
            if key in {"a", "left", "esquerda", "w", "up"}:
                self.bt_action_selected = (self.bt_action_selected - 1) % len(self.bt_action_items)
            elif key in {"d", "right", "direita", "s", "down"}:
                self.bt_action_selected = (self.bt_action_selected + 1) % len(self.bt_action_items)
            elif key in {"enter", "e", "selecionar", ""}:
                self.run_bluetooth_device_action(self.bt_action_items[self.bt_action_selected])
            elif key in {"b", "back", "esc"}:
                self.screen = "bluetooth_device_menu"
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
        self.run_bash("chmod +x ~/conectar-pc.sh && ~/conectar-pc.sh ; (command -v lsusb >/dev/null 2>&1 && lsusb || true); echo '---'; (dmesg 2>/dev/null | tail -20 || true)")

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
                "(command -v termux-wifi-scaninfo >/dev/null 2>&1 && termux-wifi-scaninfo || command -v nmcli >/dev/null 2>&1 && nmcli device wifi list || command -v iwlist >/dev/null 2>&1 && iwlist scan 2>/dev/null || echo 'Nenhuma ferramenta Wi-Fi disponível.')"
            )
        elif name == "Connect open AP":
            self.run_bash(
                "(command -v termux-wifi-scaninfo >/dev/null 2>&1 && python3 - <<'PY'\nimport json, subprocess, sys\ntry:\n    data = json.load(sys.stdin)\n    ssid = next((ap.get('SSID') for ap in data if ap.get('SSID') and not ap.get('SECURITY')), None)\n    if ssid:\n        subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid])\n        print('Tentando conectar em', ssid)\n    else:\n        print('Nenhuma rede aberta encontrada.')\nexcept Exception as e:\n    print('Erro ao conectar:', e)\nPY\n || echo 'Não foi possível executar a conexão automática.')"
            )
        elif name == "Disconnect Wi-Fi":
            self.run_bash(
                "(command -v nmcli >/dev/null 2>&1 && nmcli device disconnect wlan0 || command -v termux-wifi-enable >/dev/null 2>&1 && termux-wifi-enable false || echo 'Desconectar Wi-Fi não suportado no ambiente.')"
            )
        elif name == "Connection status":
            self.run_bash(
                "(command -v termux-wifi-connectioninfo >/dev/null 2>&1 && termux-wifi-connectioninfo || command -v nmcli >/dev/null 2>&1 && nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes' || echo 'Status Wi-Fi não disponível.')"
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
                "(command -v bluetoothctl >/dev/null 2>&1 && bluetoothctl --timeout 5 scan on >/dev/null 2>&1 && sleep 2 && bluetoothctl devices || command -v hcitool >/dev/null 2>&1 && timeout 5 hcitool scan 2>/dev/null || echo 'Nenhuma ferramenta Bluetooth disponível.')"
            )
            self.last_status = "OK"
        elif name == "List paired devices":
            self.run_bash(
                "(command -v bluetoothctl >/dev/null 2>&1 && bluetoothctl paired-devices || echo 'bluetoothctl não disponível.')"
            )
            self.screen = "report"
        elif name == "Device actions":
            self.bt_devices = self.get_bluetooth_devices()
            if self.bt_devices:
                self.bt_device_selected = 0
                self.screen = "bluetooth_device_menu"
            else:
                self.last_output = "Nenhum dispositivo Bluetooth encontrado."
                self.last_status = "ERRO"
        self.screen = self.screen if self.screen != "report" else "report"

    def get_bluetooth_devices(self) -> list[str]:
        try:
            proc = subprocess.run(["bash", "-lc", "command -v bluetoothctl >/dev/null 2>&1 && bluetoothctl devices || true"], capture_output=True, text=True, timeout=15)
            lines = proc.stdout.splitlines()
            devices = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 3 and parts[0] == "Device":
                    addr = parts[1]
                    name = " ".join(parts[2:])
                    devices.append(f"{name} ({addr})")
            return devices
        except subprocess.TimeoutExpired:
            return []

    def run_bluetooth_device_action(self, action: str) -> None:
        if not self.bt_devices:
            self.last_output = "Nenhum dispositivo Bluetooth disponível."
            self.last_status = "ERRO"
            self.screen = "report"
            return
        selected = self.bt_devices[self.bt_device_selected]
        addr = selected.split("(")[-1].strip(")")
        if action == "Connect":
            self.run_bash(
                f"(command -v bluetoothctl >/dev/null 2>&1 && echo -e 'connect {addr}\nquit' | bluetoothctl || echo 'Falha ao conectar.')"
            )
        elif action == "Pair":
            self.run_bash(
                f"(command -v bluetoothctl >/dev/null 2>&1 && echo -e 'pair {addr}\nquit' | bluetoothctl || echo 'Falha ao parear.')"
            )
        elif action == "Disconnect":
            self.run_bash(
                f"(command -v bluetoothctl >/dev/null 2>&1 && echo -e 'disconnect {addr}\nquit' | bluetoothctl || echo 'Falha ao desconectar.')"
            )
        elif action == "Info":
            self.run_bash(
                f"(command -v bluetoothctl >/dev/null 2>&1 && echo -e 'info {addr}\nquit' | bluetoothctl || echo 'Falha ao obter informações.')"
            )
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
        elif name == "Network scan":
            self.run_network_devices_scan()
            return
        self.screen = "report"

    def run_network_devices_scan(self) -> None:
        self.last_command = "Network devices scan"
        self.run_bash(
            "(command -v nmap >/dev/null 2>&1 && nmap -sn \"$(ip -o -f inet addr show | awk '/scope global/ {print $4; exit}')\" 2>/dev/null || command -v arp >/dev/null 2>&1 && arp -n || command -v ip >/dev/null 2>&1 && ip neigh || echo 'Nenhuma ferramenta de descoberta de rede disponível.')"
        )
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
        title = Text(banner, style="bold white")
        self.console.print(Panel(title, border_style="white", box=box.DOUBLE))

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
        icon_panel = Panel(Text(icon, style="white"), title=selected_item, border_style="white", box=box.SQUARE)
        self.console.print(icon_panel)

        table = Table(title="Menu principal", box=box.SQUARE, show_header=False)
        table.add_column("Opção", style="bold white")
        for idx, item in enumerate(self.menu_items):
            style = "bold black on white" if idx == self.selected else "white"
            table.add_row(f"> {item}" if idx == self.selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[white]Setas / A/D / W/S[/white] para navegar\n[white]Enter[/white] para selecionar\n[white]Q[/white] para sair", border_style="white"))

    def draw_wifi_menu(self) -> None:
        selected = self.wifi_items[self.wifi_selected]
        title = Text(self.font.renderText(selected), style="bold white")
        self.console.print(Panel(title, border_style="white", box=box.SQUARE))
        table = Table(title="Wi‑Fi Ferramentas", box=box.SIMPLE, show_header=False)
        table.add_column("Opção", style="bold white")
        for idx, item in enumerate(self.wifi_items):
            style = "bold black on white" if idx == self.wifi_selected else "white"
            table.add_row(f"> {item}" if idx == self.wifi_selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[white]Setas / A/D / W/S[/white] para navegar\n[white]Enter[/white] executar\n[white]B[/white] voltar", border_style="white"))

    def draw_bluetooth_menu(self) -> None:
        selected = self.bt_items[self.bt_selected]
        title = Text(self.font.renderText(selected), style="bold white")
        self.console.print(Panel(title, border_style="white", box=box.SQUARE))
        table = Table(title="Bluetooth Ferramentas", box=box.SIMPLE, show_header=False)
        table.add_column("Opção", style="bold white")
        for idx, item in enumerate(self.bt_items):
            style = "bold black on white" if idx == self.bt_selected else "white"
            table.add_row(f"> {item}" if idx == self.bt_selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[white]Setas / A/D / W/S[/white] para navegar\n[white]Enter[/white] executar\n[white]B[/white] voltar", border_style="white"))

    def draw_ferramentas_menu(self) -> None:
        selected = self.ferramentas_items[self.ferramentas_selected]
        title = Text(self.font.renderText(selected), style="bold white")
        self.console.print(Panel(title, border_style="white", box=box.SQUARE))
        table = Table(title="Ferramentas", box=box.SIMPLE, show_header=False)
        table.add_column("Opção", style="bold white")
        for idx, item in enumerate(self.ferramentas_items):
            style = "bold black on white" if idx == self.ferramentas_selected else "white"
            table.add_row(f"> {item}" if idx == self.ferramentas_selected else f"  {item}", style=style)
        self.console.print(table)
        self.console.print(Panel("[white]Setas / A/D / W/S[/white] para navegar\n[white]Enter[/white] executar\n[white]B[/white] voltar", border_style="white"))

    def draw_report(self) -> None:
        panel = Panel.fit(
            f"[bold white]Comando:[/bold white] {self.last_command}\n[bold white]Status:[/bold white] {self.last_status}\n\n{self.last_output}",
            title="Relatório",
            border_style="white",
            box=box.ROUNDED,
        )
        self.console.print(panel)

    def draw_about(self) -> None:
        panel = Panel.fit(
            "Painel visual para auditoria autorizada.\nInclui módulos seguros de Wi-Fi, phishing awareness, MITM, DoS e USB audit.\nUse apenas em ambientes onde você tenha permissão.",
            title="Sobre",
            border_style="white",
            box=box.ROUNDED,
        )
        self.console.print(panel)


def main() -> None:
    app = AuditArcadeUI()
    app.run()


if __name__ == "__main__":
    main()

echo "Procurando o PC na rede USB..."

# Espera o tethering ativar
sleep 4

# Lista de IPs comuns de tethering USB
IPS=(
    "192.168.42.1"
    "192.168.42.129"
    "192.168.137.1"
    "192.168.137.129"
    "192.168.43.1"
)

USUARIO="seu_usuario"   # <--- TROQUE AQUI pelo usuário do seu PC

encontrado=false

for ip in "${IPS[@]}"; do
    echo -n "Testando $ip ... "
    if ping -c 1 -W 1 "$ip" >/dev/null 2>&1; then
        echo "encontrado!"
        echo "Conectando em $ip ..."
        ssh "$USUARIO@$ip"
        encontrado=true
        break
    else
        echo "não respondeu"
    fi
done

if [ "$encontrado" = false ]; then
    echo ""
    echo "Não encontrei o PC."
    echo "Verifique se:"
    echo "  1. O cabo USB está conectado"
    echo "  2. O Tethering USB está ativado no celular"
    echo "  3. O SSH está rodando no PC"
fi
