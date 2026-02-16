"""
NetLoader-X Banner & Metadata
Author  : voltsparx
Contact : voltsparx@gmail.com
"""

from ui.theme import ANSIColor


def show_banner():
    # Using ANSI color codes with f-strings for simple coloring
    # Using raw string with escaping to handle backslashes in ASCII art
    banner = f"""{ANSIColor.RESET}
{ANSIColor.BLUE} _   _      _   _                     _                    {ANSIColor.ORANGE}__   __{ANSIColor.RESET}
{ANSIColor.BLUE}| \\ | |    | | | |                   | |                   {ANSIColor.ORANGE}\\ \\ / /{ANSIColor.RESET}
{ANSIColor.BLUE}|  \\| | ___| |_| |     ___   __ _  __| | ___ _ __   ______ {ANSIColor.ORANGE} \\ V / {ANSIColor.RESET}
{ANSIColor.BLUE}| . ` |/ _ \\ __| |    / _ \\ / _` |/ _` |/ _ \\ '__| |______|{ANSIColor.ORANGE} /   \\ {ANSIColor.RESET}
{ANSIColor.BLUE}| |\\  |  __/ |_| |___| (_) | (_| | (_| |  __/ |            {ANSIColor.ORANGE}/ /^\\ \\{ANSIColor.RESET}
{ANSIColor.BLUE}\\_| \\_/\\___|\\__\\_____/\\___/ \\__,_|\\__,_|\\___|_|            {ANSIColor.ORANGE}\\/   \\/{ANSIColor.RESET}

{ANSIColor.CYAN}NetLoader-X :: Defensive Load Simulation Framework{ANSIColor.RESET}
{ANSIColor.CYAN}Author  : {ANSIColor.ORANGE}voltsparx{ANSIColor.RESET}
{ANSIColor.GRAY}Contact : voltsparx@gmail.com{ANSIColor.RESET}
{ANSIColor.GREEN}Mode    : SAFE / LOCAL / DEFENSIVE ONLY{ANSIColor.RESET}
"""
    print(banner)