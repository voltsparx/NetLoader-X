"""
Strict Validation Layer
"""

import socket
from core.config import GlobalConfig


def validate_target(host: str, port: int):
    if host not in GlobalConfig.ALLOWED_HOSTS:
        raise ValueError("Target host not allowed")

    low, high = GlobalConfig.ALLOWED_PORT_RANGE
    if not (low <= port <= high):
        raise ValueError("Target port out of safe range")


def resolve_localhost():
    return socket.gethostbyname("localhost")


def validate_numeric_choice(choice: str, num_options: int) -> int:
    """Validate user numeric menu choice"""
    try:
        num = int(choice)
        if 1 <= num <= num_options:
            return num
        raise ValueError(f"Please enter a number between 1 and {num_options}")
    except ValueError:
        raise ValueError("Invalid input. Please enter a number.")