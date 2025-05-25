"""
Configuration management for xPOURY4 Recon
Author: xPOURY4
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigurationException
from .logger import logger


class ConfigManager:
    """Advanced configuration manager for xPOURY4 Recon"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.yaml"
        self.config_path = Path(self.config_file)
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix.lower() == '.yaml':
                        self._config = yaml.safe_load(f) or {}
                    else:
                        self._config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self._create_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self._config = {
            "api_keys": {
                "github_token": os.getenv("GITHUB_TOKEN", ""),
                "shodan_api_key": os.getenv("SHODAN_API_KEY", ""),
                "virustotal_api_key": os.getenv("VIRUSTOTAL_API_KEY", "")
            },
            "settings": {
                "timeout": 30,
                "max_retries": 3,
                "rate_limit_delay": 1.0,
                "output_format": "json",
                "save_results": True,
                "results_directory": "results"
            },
            "modules": {
                "github_recon": {
                    "enabled": True,
                    "include_repos": True,
                    "include_gists": True,
                    "max_repos": 100
                },
                "domain_recon": {
                    "enabled": True,
                    "subdomain_sources": ["crt.sh", "threatcrowd", "virustotal"],
                    "dns_servers": ["8.8.8.8", "1.1.1.1"]
                },
                "phone_recon": {
                    "enabled": True,
                    "include_carrier": True,
                    "include_location": True
                },
                "linkedin_recon": {
                    "enabled": True,
                    "auto_open_browser": True
                }
            },
            "web_ui": {
                "host": "127.0.0.1",
                "port": 5000,
                "debug": False,
                "secret_key": os.urandom(24).hex()
            }
        }
        self.save_config()
        logger.info("Default configuration created")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.yaml':
                    yaml.dump(self._config, f, default_flow_style=False, indent=2)
                else:
                    json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            raise ConfigurationException(f"Failed to save configuration: {e}")
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_sections = ["api_keys", "settings", "modules", "web_ui"]
        
        for section in required_sections:
            if section not in self._config:
                raise ConfigurationException(f"Missing required section: {section}")
        
        return True
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration"""
        return self._config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration with new values"""
        self._config.update(new_config)
        self.save_config()


# Global config manager instance
config = ConfigManager() 