"""
NetLoader-X Theme Definitions
"""

class Theme:
    BLUE = "bold bright_blue"
    CYAN = "bright_cyan"
    GREEN = "bright_green"
    YELLOW = "yellow"
    RED = "bold red"
    ORANGE = "bold orange1"
    GRAY = "grey70"
    WHITE = "white"


def colorize(text: str, style: str = "info") -> str:
    """
    Simple text coloring utility.
    Returns colored text for terminal output.
    """
    try:
        from rich.console import Console
        from rich.style import Style
        console = Console()
        
        style_map = {
            "primary": "bold bright_blue",
            "info": "bright_cyan",
            "success": "bright_green",
            "warning": "yellow",
            "error": "bold red",
            "muted": "grey70",
            "section": "bold bright_blue",
            "prompt": "bright_cyan"
        }
        
        actual_style = style_map.get(style, "white")
        return f"[{actual_style}]{text}[/]"
    except:
        # Fallback if rich is not available
        return text