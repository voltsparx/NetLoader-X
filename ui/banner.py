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
    banner.append(" ███╗   ██╗███████╗████████╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗ \n", Theme.BLUE)
    banner.append(" ████╗  ██║██╔════╝╚══██╔══╝██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗\n", Theme.BLUE)
    banner.append(" ██╔██╗ ██║█████╗     ██║   ██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝\n", Theme.BLUE)
    banner.append(" ██║╚██╗██║██╔══╝     ██║   ██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗\n", Theme.BLUE)
    banner.append(" ██║ ╚████║███████╗   ██║   ███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║\n", Theme.BLUE)
    banner.append(" ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝\n", Theme.BLUE)

    banner.append("\n")
    banner.append(" NetLoader-X :: Defensive Load Simulation Framework\n", Theme.CYAN)
    banner.append(" Author  : voltsparx\n", Theme.GRAY)
    banner.append(" Contact : voltsparx@gmail.com\n", Theme.GRAY)
    banner.append(" Mode    : SAFE / LOCAL / DEFENSIVE ONLY\n", Theme.GREEN)
    banner.append("\n")

    console.print(banner)