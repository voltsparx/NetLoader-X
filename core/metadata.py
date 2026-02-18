"""
NetLoader-X Project Metadata
Central location for project information
"""

# Project Information
PROJECT_NAME = "NetLoader-X"
PROJECT_TAGLINE = "Defensive Load & Failure Simulation Framework"
PROJECT_DESCRIPTION = "Safe, educational tool for stress-testing and resilience learning"

# Version Information
VERSION_MAJOR = 3
VERSION_MINOR = 7
VERSION_PATCH = 0
# If patch is 0, use a short "major.minor" version for cleaner display (v3.7).
VERSION_FULL = (
    f"{VERSION_MAJOR}.{VERSION_MINOR}"
    if VERSION_PATCH == 0
    else f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
)
VERSION_STRING = f"v{VERSION_FULL}"

# Author Information
AUTHOR_NAME = "voltsparx"
AUTHOR_EMAIL = "voltsparx@gmail.com"

# Repository Information
GITHUB_URL = "https://github.com/voltsparx/NetLoader-X"

# License
LICENSE = "Educational & Defensive Simulation Only"

# Status
STATUS = "PRODUCTION-READY"
LAST_UPDATED = "2026-02-18"

# Safety Information
SAFETY_MODE = "SAFE / LOCAL / DEFENSIVE ONLY"

# Environment
ENVIRONMENT = "Python 3.8+"

# Formatted Strings for Easy Access
def get_version_string() -> str:
    """Return formatted version string"""
    return VERSION_STRING


def get_author_string() -> str:
    """Return formatted author string"""
    return f"{AUTHOR_NAME} <{AUTHOR_EMAIL}>"


def get_project_header() -> str:
    """Return formatted project header"""
    return f"{PROJECT_NAME} {VERSION_STRING} - {PROJECT_TAGLINE}"


def get_banner_info() -> dict:
    """Return all banner information as dictionary"""
    return {
        "project_name": PROJECT_NAME,
        "version": VERSION_STRING,
        "tagline": PROJECT_TAGLINE,
        "author": AUTHOR_NAME,
        "email": AUTHOR_EMAIL,
        "github": GITHUB_URL,
        "safety_mode": SAFETY_MODE,
    }
