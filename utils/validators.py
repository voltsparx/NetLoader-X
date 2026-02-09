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