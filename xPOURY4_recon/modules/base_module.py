"""
Base module for all reconnaissance modules
Author: xPOURY4
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ..core.config_manager import config
from ..core.logger import logger
from ..core.exceptions import APIException, NetworkException


class BaseReconModule(ABC):
    """Base class for all reconnaissance modules"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.session = None
        self.timeout = config.get("settings.timeout", 30)
        self.max_retries = config.get("settings.max_retries", 3)
        self.rate_limit_delay = config.get("settings.rate_limit_delay", 1.0)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': 'xPOURY4-Recon/1.0.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def investigate(self, target: str, **kwargs) -> Dict[str, Any]:
        """Main investigation method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if module is properly configured"""
        pass
    
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling"""
        if not self.session:
            raise NetworkException("Session not initialized. Use async context manager.")
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        wait_time = self.rate_limit_delay * (2 ** attempt)
                        logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise APIException(
                            f"HTTP {response.status}: {await response.text()}",
                            status_code=response.status
                        )
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise NetworkException(f"Network error after {self.max_retries} attempts: {e}")
                await asyncio.sleep(self.rate_limit_delay * (attempt + 1))
        
        raise NetworkException(f"Failed to complete request after {self.max_retries} attempts")
    
    def format_result(self, success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
        """Format module result in standard format"""
        return {
            'module': self.module_name,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'data': data,
            'error': error
        }
    
    def validate_input(self, target: str, validation_func=None) -> bool:
        """Validate input target"""
        if not target or not target.strip():
            return False
        
        if validation_func:
            return validation_func(target)
        
        return True
    
    async def rate_limit(self):
        """Apply rate limiting"""
        await asyncio.sleep(self.rate_limit_delay) 