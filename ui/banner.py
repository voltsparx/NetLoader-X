"""
NetLoader-X Banner Display
Uses metadata from core.metadata for dynamic content
"""

from ui.theme import ANSIColor
from core.metadata import (
    PROJECT_NAME,
    PROJECT_TAGLINE,
    VERSION_STRING,
    AUTHOR_NAME,
    AUTHOR_EMAIL,
    SAFETY_MODE,
)


def show_banner():
    """Display the NetLoader-X banner with metadata from core.metadata"""
    # Using ANSI color codes with f-strings for simple coloring
    # Using raw string with escaping to handle backslashes in ASCII art
    banner = f"""{ANSIColor.RESET}
{ANSIColor.BLUE} _   _      _   _                     _                    {ANSIColor.ORANGE}__   __{ANSIColor.RESET}
{ANSIColor.BLUE}| \\ | |    | | | |                   | |                   {ANSIColor.ORANGE}\\ \\ / /{ANSIColor.RESET}
{ANSIColor.BLUE}|  \\| | ___| |_| |     ___   __ _  __| | ___ _ __   ______ {ANSIColor.ORANGE} \\ V / {ANSIColor.RESET}
{ANSIColor.BLUE}| . ` |/ _ \\ __| |    / _ \\ / _` |/ _` |/ _ \\ '__| |______|{ANSIColor.ORANGE} /   \\ {ANSIColor.RESET}
{ANSIColor.BLUE}| |\\  |  __/ |_| |___| (_) | (_| | (_| |  __/ |            {ANSIColor.ORANGE}/ /^\\ \\{ANSIColor.RESET}
{ANSIColor.BLUE}\\_| \\_/\\___|\\__\\_____/\\___/ \\__,_|\\__,_|\\___|_|            {ANSIColor.ORANGE}\\/   \\/{ANSIColor.RESET}
{ANSIColor.ORANGE}                                                                {VERSION_STRING}{ANSIColor.RESET}

{ANSIColor.CYAN}{PROJECT_NAME} :: {PROJECT_TAGLINE}{ANSIColor.RESET}
{ANSIColor.CYAN}Author  : {ANSIColor.ORANGE}{AUTHOR_NAME}{ANSIColor.RESET}
{ANSIColor.GRAY}Contact : {AUTHOR_EMAIL}{ANSIColor.RESET}
{ANSIColor.GREEN}Mode    : {SAFETY_MODE}{ANSIColor.RESET}
"""
    print(banner)