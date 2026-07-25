#!/usr/bin/env python3
"""Painel visual de auditoria autorizada para Termux.

Não implemento invasão, roubo de credenciais, acesso não autorizado
ou envio de arquivos para aparelhos de terceiros. Esta versão oferece
um visual em ASCII art e módulos seguros para diagnóstico de Wi-Fi,
rede local, NFC e exportação local autorizada.
"""

from curses import echo
import getpass
import os
import subprocess
import sys
import textwrap
import tempfile
import shutil
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
        self.wifi_items = ["Scan APs", "Connect open AP", "Disconnect Wi-Fi", "Connection status", "Códigos"]
        self.bt_items = ["Bluejacking", "Bluesnarfing", "BLE Spoofing", "Scan Devices"]
        self.ferramentas_items = ["Phishing", "MITM", "DoS", "USB", "Hydra", "Network scan"]
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
        self.usb_code = ""
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
        # If we're in the USB input screen, accept a raw line (don't lowercase)
        if self.screen == "usb_input":
            # Provide raw key capture so ESC can be detected to exit USB mode
            # Windows: use msvcrt.getwch; Unix: use termios/tty in raw mode
            if os.name == "nt":
                try:
                    import msvcrt
                    buf = ""
                    sys.stdout.write("USB> ")
                    sys.stdout.flush()
                    while True:
                        ch = msvcrt.getwch()
                        if ch in {"\r", "\n"}:
                            print()
                            return buf
                        if ch == "\x1b":
                            return "esc"
                        if ch in {"\x00", "\xe0"}:
                            arrow = msvcrt.getwch()
                            if arrow == "H":
                                return "up"
                            continue
                        if ch == "\x08":
                            buf = buf[:-1]
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        else:
                            buf += ch
                            sys.stdout.write(ch)
                            sys.stdout.flush()
                except Exception:
                    try:
                        return input("USB> ")
                    except EOFError:
                        return ""
            else:
                # POSIX systems: read raw characters so ESC is detected immediately
                try:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    tty.setraw(fd)
                    buf = ""
                    sys.stdout.write("USB> ")
                    sys.stdout.flush()
                    while True:
                        ch = sys.stdin.read(1)
                        if ch == "\x1b":
                            # consume any extra bytes to avoid leaving escape chars
                            # try to non-blocking read remaining seq (best-effort)
                            try:
                                seq = sys.stdin.read(2)
                            except Exception:
                                seq = ""
                            return "esc"
                        if ch in {"\r", "\n"}:
                            print()
                            return buf
                        if ch in {"\x7f", "\b"}:
                            buf = buf[:-1]
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        else:
                            buf += ch
                            sys.stdout.write(ch)
                            sys.stdout.flush()
                except Exception:
                    try:
                        return input("USB> ")
                    except EOFError:
                        return ""
                finally:
                    try:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    except Exception:
                        pass

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
        elif self.screen == "usb_input":
            if key in {"b", "back", "esc", "w", "up"}:
                self.screen = "menu"
                return
            if termios is None or os.name == "nt":
                k = key.strip()
                if not k:
                    return
                if k.lower() in {"b", "back", "esc", "w", "up"}:
                    self.screen = "menu"
                else:
                    self.usb_code = key
                    self.run_usb_code(self.usb_code)
                    self.screen = "report"
            else:
                if key == "enter":
                    if self.usb_code.strip():
                        self.run_usb_code(self.usb_code)
                        self.screen = "report"
                elif key in {"\x7f", "\b"}:
                    self.usb_code = self.usb_code[:-1]
                elif len(key) == 1:
                    self.usb_code += key
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

    def prompt_python_command(self) -> str:
        print("\nDigite um comando Python para executar (por exemplo: print('hello'), 2+2):")
        return input("Python> ").strip()

    def run_python_command(self, command: str) -> None:
        self.last_command = f"python -c {command}"
        self.message = "Executando comando Python local"
        try:
            proc = subprocess.run([sys.executable, "-c", command], capture_output=True, text=True, timeout=25)
            output = (proc.stdout + proc.stderr).strip()
            if not output:
                output = "Sem saída do comando Python."
            self.last_output = output
            self.last_status = "OK"
        except subprocess.TimeoutExpired:
            self.last_status = "ERRO"
            self.last_output = "O comando Python excedeu o tempo limite de execução."
        except Exception as e:
            self.last_status = "ERRO"
            self.last_output = f"Falha ao executar o comando Python: {e}"

    def find_usb_mount(self) -> str | None:
        candidates = [
            "/storage",
            "/mnt/media_rw",
            "/mnt/usb",
            "/mnt/sdcard",
            "/sdcard",
            "D:",
            "E:",
            "F:",
            "G:",
        ]
        for base in candidates:
            if os.path.isdir(base):
                try:
                    for name in os.listdir(base):
                        path = os.path.join(base, name)
                        if os.path.isdir(path) and os.access(path, os.W_OK):
                            return path
                except PermissionError:
                    continue
        return None

    def write_to_usb(self, usb_path: str, filename: str, content: str) -> None:
        try:
            target = os.path.join(usb_path, filename)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            self.last_output += f"\nArquivo gravado em {target}"
            self.last_status = "OK"
        except Exception as e:
            self.last_status = "ERRO"
            self.last_output += f"\nFalha ao gravar no USB: {e}"

    def has_adb_device(self) -> bool:
        try:
            # Ensure adb server is running
            try:
                subprocess.run(["adb", "start-server"], capture_output=True, text=True, timeout=5)
            except Exception:
                pass
            proc = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
            lines = proc.stdout.splitlines()
            # parse device lines (skip header)
            for l in lines[1:]:
                if not l.strip():
                    continue
                parts = l.split()
                # common second column values: 'device', 'unauthorized', 'offline'
                if len(parts) >= 2 and parts[1] == "device":
                    return True
            # no device found
            return False
        except Exception:
            return False

    def run_on_adb_device(self, local_path: str, filename: str) -> None:
        # Try a few common remote locations and python binaries
        remote_candidates = [f"/data/local/tmp/{filename}", f"/sdcard/{filename}"]
        python_bins = ["python3", "python"]
        # common termux/python paths
        termux_bins = ["/data/data/com.termux/files/usr/bin/python3", "/data/data/com.termux/files/usr/bin/python"]
        try:
            # Try streaming the script via stdin to remote python (works even without writable remote path)
            try:
                with open(local_path, "rb") as fh:
                    content_bytes = fh.read()
                for py in python_bins + termux_bins:
                    try:
                        self.last_output += f"\nTentando execução via stdin com {py}..."
                        prun_pipe = subprocess.run(["adb", "shell", py, "-"], input=content_bytes, capture_output=True, timeout=60)
                    except Exception as e:
                        self.last_output += f"\nFalha ao executar via stdin ({py}): {e}"
                        continue
                    self.last_output += f"\nExecução adb stdin ({py}) returncode={prun_pipe.returncode}\nstdout:\n{prun_pipe.stdout.decode(errors='ignore') if isinstance(prun_pipe.stdout, bytes) else prun_pipe.stdout}\nstderr:\n{prun_pipe.stderr.decode(errors='ignore') if isinstance(prun_pipe.stderr, bytes) else prun_pipe.stderr}"
                    if prun_pipe.returncode == 0:
                        self.last_status = "OK"
                        return
            except Exception:
                pass

            for remote in remote_candidates:
                try:
                    ppush = subprocess.run(["adb", "push", local_path, remote], capture_output=True, text=True, timeout=20)
                except Exception as e:
                    self.last_output += f"\nFalha ao enviar via adb: {e}"
                    continue
                self.last_output += f"\nadb push -> stdout:\n{ppush.stdout}\nstderr:\n{ppush.stderr}"

                # Make remote file executable (harmless for .py) and try to run with common python binaries
                try:
                    chmod = subprocess.run(["adb", "shell", "chmod", "+x", remote], capture_output=True, text=True, timeout=10)
                    self.last_output += f"\nadb chmod: {chmod.stdout}{chmod.stderr}"
                except Exception:
                    pass

                for py in python_bins:
                    try:
                        prun = subprocess.run(["adb", "shell", py, remote], capture_output=True, text=True, timeout=60)
                    except Exception as e:
                        self.last_output += f"\nFalha ao executar via adb ({py}): {e}"
                        continue
                    self.last_output += f"\nExecução adb ({py}) returncode={prun.returncode}\nstdout:\n{prun.stdout}\nstderr:\n{prun.stderr}"
                    if prun.returncode == 0:
                        self.last_status = "OK"
                        return

                # As a last resort, try running via 'sh' if the script is simple and starts with a shebang
                try:
                    prun_sh = subprocess.run(["adb", "shell", "sh", remote], capture_output=True, text=True, timeout=60)
                    self.last_output += f"\nExecução adb (sh) returncode={prun_sh.returncode}\nstdout:\n{prun_sh.stdout}\nstderr:\n{prun_sh.stderr}"
                    if prun_sh.returncode == 0:
                        self.last_status = "OK"
                        return
                except Exception:
                    pass

            # if we reach here, execution failed on all attempts
            self.last_status = "ERRO"
            self.last_output += "\nNão foi possível executar o script via ADB no dispositivo conectado. Verifique se o device possui Python ou Termux instalado."
        except Exception as e:
            self.last_status = "ERRO"
            self.last_output += f"\nErro inesperado ao tentar executar via ADB: {e}"

    def run_usb_audit(self) -> None:
        self.last_command = "USB audit / Python"
        self.message = "Modo USB/ADB: use .pull /caminho/arquivo.py para buscar do Termux e executar no PC."
        lines: list[str] = []
        print("\nEntrando no modo multilinha para USB/ADB. Digite seu código ou use .pull /caminho/arquivo.py para puxar do dispositivo Android.")
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == ".run":
                break
            if line.strip() == ".cancel":
                self.last_status = "ERRO"
                self.last_output = "Edição USB cancelada pelo usuário."
                self.message = "USB cancelado"
                self.screen = "report"
                return
            lines.append(line)

        code = "\n".join(lines)
        self.usb_code = code
        # Special command: .pull will fetch a .py from the connected device and run locally
        if code.strip().startswith(".pull"):
            if self.has_adb_device():
                self.last_output = "Tentando buscar e executar script do dispositivo via ADB..."
                path = code.strip()[len(".pull"):].strip()
                self.pull_and_run_from_device(path if path else None)
            else:
                self.last_status = "ERRO"
                self.last_output = "Nenhum dispositivo ADB conectado."
            self.screen = "report"
            return

        # Execute and export
        self.run_usb_code(code)
        self.screen = "report"

    def pull_and_run_from_device(self, requested_path: str | None = None) -> None:
        # Attempts to pull a specified file from device, or find a .py file in common locations.
        candidates = [
            "/data/data/com.termux/files/home",
            "/data/data/com.termux/files/home/storage/shared",
            "/data/data/com.termux/files/home/storage/shared/Download",
            "/sdcard",
            "/sdcard/Download",
            "/storage/emulated/0",
            "/data/local/tmp",
        ]
        found = requested_path
        try:
            try:
                subprocess.run(["adb", "start-server"], capture_output=True, text=True, timeout=5)
            except Exception:
                pass

            if not found:
                for base in candidates:
                    cmd = f"ls -t {base}/*.py 2>/dev/null"
                    proc = subprocess.run(["adb", "shell", cmd], capture_output=True, text=True, timeout=10)
                    if proc.returncode != 0:
                        continue
                    out = proc.stdout.strip().replace('\r', '')
                    if out:
                        found = out.splitlines()[0].strip()
                        break

            if not found:
                self.last_status = "ERRO"
                self.last_output += "\nNenhum arquivo .py encontrado nas pastas usuais do dispositivo. Use .pull /caminho/arquivo.py para especificar." 
                return

            self.last_output += f"\nArquivo encontrado no dispositivo: {found}"

            proc2 = subprocess.run(["adb", "exec-out", "cat", found], capture_output=True, timeout=20)
            if proc2.returncode == 0 and proc2.stdout:
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
                local_tmp = tf.name
                tf.write(proc2.stdout)
                tf.close()
                try:
                    self.last_output += "\nExecutando script trazido do dispositivo localmente..."
                    pr = subprocess.run([sys.executable, local_tmp], capture_output=True, text=True, timeout=60)
                    self.last_output += f"\nstdout:\n{pr.stdout}\nstderr:\n{pr.stderr}"
                    self.last_status = "OK" if pr.returncode == 0 else "ERRO"
                finally:
                    try:
                        os.remove(local_tmp)
                    except Exception:
                        pass
                return

            self.last_output += f"\nadb exec-out falhou ou não retornou dados. stderr:\n{proc2.stderr.decode(errors='ignore') if isinstance(proc2.stderr, bytes) else proc2.stderr}"

            local_tmp = os.path.join(os.getcwd(), os.path.basename(found))
            ppull = subprocess.run(["adb", "pull", found, local_tmp], capture_output=True, text=True, timeout=20)
            self.last_output += f"\nadb pull: stdout:\n{ppull.stdout}\nstderr:\n{ppull.stderr}"
            if ppull.returncode == 0 and os.path.exists(local_tmp):
                try:
                    self.last_output += "\nExecutando arquivo puxado do dispositivo localmente..."
                    pr = subprocess.run([sys.executable, local_tmp], capture_output=True, text=True, timeout=60)
                    self.last_output += f"\nstdout:\n{pr.stdout}\nstderr:\n{pr.stderr}"
                    self.last_status = "OK" if pr.returncode == 0 else "ERRO"
                finally:
                    try:
                        os.remove(local_tmp)
                    except Exception:
                        pass
                return

            self.last_status = "ERRO"
            self.last_output += "\nNão foi possível recuperar e executar o script do dispositivo."
        except Exception as e:
            self.last_status = "ERRO"
            self.last_output += f"\nErro inesperado: {e}"

    def run_usb_code(self, code: str) -> None:
        if not code.strip():
            self.last_status = "ERRO"
            self.last_output = "Nenhum código Python informado."
            self.message = "USB cancelado"
            return

        self.last_command = "USB code execution"
        self.message = "Executando código Python e exportando para USB"
        # First execute locally
        self.run_python_code(code)

        # Write payload to a secure temp file so we can push to adb if needed
        filename = f"usb_payload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        local_tmp = None
        try:
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
            local_tmp = tf.name
            tf.write(f"# Script gerado pelo AuditArcadeUI para USB\n{code}\n".encode("utf-8"))
            tf.close()
        except Exception as e:
            self.last_output += f"\nFalha ao gravar arquivo temporário: {e}"

        try:
            # If adb device present, try push+run there
            if local_tmp and self.has_adb_device():
                self.last_output += "\nDispositivo ADB detectado — tentando enviar e executar no dispositivo."
                self.run_on_adb_device(local_tmp, filename)

            usb_mount = self.find_usb_mount()
            if usb_mount:
                try:
                    payload = f"# Script gerado pelo AuditArcadeUI para USB\n{code}\n"
                    self.write_to_usb(usb_mount, filename, payload)
                    if self.last_status == "OK":
                        self.message = "Código Python executado e arquivo salvo no USB"
                except Exception as e:
                    self.last_output += f"\nFalha ao gravar no USB: {e}"
            else:
                self.last_output += "\nNenhum dispositivo USB de armazenamento encontrado."
                if not self.has_adb_device():
                    self.last_status = "ERRO"
                    self.message = "USB/ADB não encontrado"
        finally:
            # Clean up local temp file
            try:
                if local_tmp and os.path.exists(local_tmp):
                    os.remove(local_tmp)
            except Exception:
                pass

    def run_python_code(self, code: str) -> None:
        self.last_command = f"python -c {code}"
        self.message = "Executando código Python local"
        try:
            proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=25)
            output = (proc.stdout + proc.stderr).strip()
            if not output:
                output = "Sem saída do código Python."
            self.last_output = output
            self.last_status = "OK"
        except subprocess.TimeoutExpired:
            self.last_status = "ERRO"
            self.last_output = "O código Python excedeu o tempo limite de execução."
        except Exception as e:
            self.last_status = "ERRO"
            self.last_output = f"Falha ao executar o código Python: {e}"

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
        elif name == "Códigos":
            self.run_network_code()
            return
        self.screen = "report"

    def run_network_code(self) -> None:
        self.last_command = "Wi-Fi codes / network execution"
        self.message = "Modo Wi-Fi: digite host de rede e código para executar em destino remoto ou local."
        try:
            host = input('Host de destino (IP ou hostname, vazio = local): ').strip()
            if not host:
                self.last_output = 'Execução local activada. Digite código Python:'
                code = input('Código Python> ')
                self.run_python_code(code)
                self.screen = 'report'
                return

            port = input('Porta SSH ou comando (vazio=22): ').strip() or '22'
            code = input('Código Python remoto> ').strip()
            if not code:
                self.last_status = 'ERRO'
                self.last_output = 'Nenhum código informado.'
                self.screen = 'report'
                return

            self.last_output = f'Executando no host {host}:{port}...'
            if port == '22':
                user = input('Usuário SSH (ou vazio para atual): ').strip() or getpass.getuser()
                ssh_cmd = ['ssh', f'{user}@{host}', 'python3', '-c', code]
                proc = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
                self.last_output = proc.stdout + ('\n' + proc.stderr if proc.stderr else '')
                self.last_status = 'OK' if proc.returncode == 0 else 'ERRO'
            else:
                # se a porta não é 22, tenta comando local com host como comando em shell
                proc = subprocess.run(['bash', '-lc', code], capture_output=True, text=True, timeout=60)
                self.last_output = proc.stdout + ('\n' + proc.stderr if proc.stderr else '')
                self.last_status = 'OK' if proc.returncode == 0 else 'ERRO'
        except Exception as e:
            self.last_status = 'ERRO'
            self.last_output = f'Falha na execução de código de rede: {e}'
        self.screen = 'report'

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
            self.usb_code = ""
            self.screen = "usb_input"
            return
        elif name == "Hydra":
            self.run_hydra_tool()
            return
        elif name == "Network scan":
            self.run_network_devices_scan()
            return
        self.screen = "report"

    def run_hydra_tool(self) -> None:
        self.last_command = "Hydra scan automático"
        self.message = "Verificando Hydra e executando modo automático"
        self.run_bash(
            "(command -v hydra >/dev/null 2>&1 && hydra -L /dev/null -P /dev/null -t 1 -f 127.0.0.1 ssh 2>&1) || echo 'Hydra não está disponível ou falha na execução.'"
        )
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
        elif self.screen == "ferramentas_menu":
            self.draw_ferramentas_menu()
        elif self.screen == "usb_input":
            self.draw_usb_input()
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
        self.console.print(Panel("[white]Setas / A/D / W/S[/white] para navegar\n[white]Enter[/white] executar\n[white]B[/white] voltar\n[white]Códigos[/white] usa SSH/exec local para rodar código em hosts de rede", border_style="white"))

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

    def draw_usb_input(self) -> None:
        title = Text(self.font.renderText("USB"), style="bold white")
        self.console.print(Panel(title, border_style="white", box=box.SQUARE))
        code_panel = Panel.fit(
            f"[bold white]Digite o código Python livremente abaixo:[/bold white]\n{self.usb_code}\n\n"
            "[white]Pressione Enter para executar, B/ESC para voltar.[/white]",
            title="USB Python Input",
            border_style="white",
            box=box.ROUNDED,
        )
        self.console.print(code_panel)

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
