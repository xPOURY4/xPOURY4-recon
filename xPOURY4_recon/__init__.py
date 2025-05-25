"""
xPOURY4 Recon - Elite Cyber Intelligence & Digital Forensics Platform
Author: xPOURY4
Version: 1.0.0

Next-generation OSINT framework engineered for cybersecurity professionals,
digital investigators, and ethical hackers seeking comprehensive target analysis.
"""

__version__ = "1.0.0"
__author__ = "xPOURY4"
__email__ = "contact@xPOURY4.dev"

from .core.recon_engine import ReconEngine
from .core.config_manager import ConfigManager

__all__ = ["ReconEngine", "ConfigManager"] 