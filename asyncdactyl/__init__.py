"""
Asynchronous Pterodactyl API Wrapper.

This wrapper is inspired on the synchronous wrapper, py-dactyl.
Link: https://github.com/iamkubi/pydactyl
"""

from .client import AsyncPterodactylClient
from .exceptions import *
from .constants import *

__version__ = "0.1.0-alpha"
__author__ = "Shibzel"
__github__ = "https://github.com/Shibzel/aiohttp"