"""
NetLoader-X Banner & Metadata
Author  : voltsparx
Contact : voltsparx@gmail.com
"""

from rich.console import Console
from rich.text import Text
from ui.theme import Theme

console = Console()


def show_banner():
    banner = Text()

    banner.append("\n")
    banner.append("[bold bright_blue]  _   _      _   _                     _                     [/][bold orange1]__   __ \n[/]")
    banner.append("[bold bright_blue] | \ | |    | | | |                   | |                    [/][bold orange1]\ \ / / \n[/]")
    banner.append("[bold bright_blue] |  \| | ___| |_| |     ___   __ _  __| | ___ _ __   ______  [/][bold orange1] \ V /  \n[/]")
    banner.append("[bold bright_blue] | . ` |/ _ \ __| |    / _ \ / _` |/ _` |/ _ \ '__| |______| [/][bold orange1] /   \  \n[/]")
    banner.append("[bold bright_blue] | |\  |  __/ |_| |___| (_) | (_| | (_| |  __/ |             [/][bold orange1]/ /^\ \ \n[/]")
    banner.append("[bold bright_blue] \_| \_/\___|\__\_____/\___/ \__,_|\__,_|\___|_|             [/][bold orange1]\/   \/ \n[/]")

    banner.append("\n")
    banner.append(" NetLoader-X :: Defensive Load Simulation Framework\n", Theme.CYAN)
    banner.append("[cyan] Author  : [/][bold orange1]voltsparx[/]\n")
    banner.append(" Contact : voltsparx@gmail.com\n", Theme.GRAY)
    banner.append(" Mode    : SAFE / LOCAL / DEFENSIVE ONLY\n", Theme.GREEN)
    banner.append("\n")

    console.print(banner)