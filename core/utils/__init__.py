"""
Shared utilities used across multiple apps.
"""
from core.utils.notifications import notify_silent
from core.utils.http import get_client_ip

__all__ = [
    "notify_silent",
    "get_client_ip",
]
