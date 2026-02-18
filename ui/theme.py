"""
NetLoader-X Theme Definitions
"""

# Rich Theme Colors
class Theme:
    BLUE = "bold bright_blue"
    CYAN = "bright_cyan"
    GREEN = "bright_green"
    YELLOW = "yellow"
    RED = "bold red"
    ORANGE = "bold orange1"
    GRAY = "grey70"
    WHITE = "white"


# ANSI Color Codes (for direct terminal output without Rich)
class ANSIColor:
    """ANSI escape codes for terminal colors"""
    BLUE = "\033[94m"          # Bright Blue
    CYAN = "\033[96m"          # Bright Cyan
    GREEN = "\033[92m"         # Bright Green
    YELLOW = "\033[93m"        # Bright Yellow
    ORANGE = "\033[38;2;255;165;0m"        # Orange 
    GRAY = "\033[90m"          # Bright Gray
    RED = "\033[91m"           # Bright Red
    WHITE = "\033[97m"         # Bright White
    RESET = "\033[0m"          # Reset to default


def supports_color() -> bool:
    """
    Basic ANSI color support check.
    """
    import os
    if os.environ.get("NO_COLOR"):
        return False
    return True


def colorize(text: str, style: str = "info") -> str:
    """
    Simple text coloring utility using ANSI codes.
    Returns colored text for terminal output.
    """
    style_map = {
        "primary": ANSIColor.BLUE,
        "info": ANSIColor.CYAN,
        "success": ANSIColor.GREEN,
        "warning": ANSIColor.YELLOW,
        "error": ANSIColor.RED,
        "muted": ANSIColor.GRAY,
        "section": ANSIColor.BLUE,
        "prompt": ANSIColor.CYAN
    }
    
    if not supports_color():
        return text

    color = style_map.get(style, ANSIColor.WHITE)
    return f"{color}{text}{ANSIColor.RESET}"
