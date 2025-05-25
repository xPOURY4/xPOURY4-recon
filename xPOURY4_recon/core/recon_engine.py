"""
Main reconnaissance engine for xPOURY4 Recon
Author: xPOURY4
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config_manager import config
from .logger import logger
from .exceptions import ReconException
from ..modules import (
    GitHubRecon,
    DomainRecon,
    PhoneRecon,
    LinkedInRecon,
    ShodanRecon
)


class ReconEngine:
    """Advanced reconnaissance engine for xPOURY4 Recon"""
    
    def __init__(self):
        self.modules = {
            'github': GitHubRecon(),
            'domain': DomainRecon(),
            'phone': PhoneRecon(),
            'linkedin': LinkedInRecon(),
            'shodan': ShodanRecon()
        }
        self.results = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory
        self.results_dir = Path(config.get("settings.results_directory", "results"))
        self.results_dir.mkdir(exist_ok=True)
        
        logger.info(f"ReconEngine initialized with session ID: {self.session_id}")
    
    async def run_github_recon(self, username: str, **kwargs) -> Dict[str, Any]:
        """Run GitHub reconnaissance"""
        try:
            logger.info(f"Starting GitHub reconnaissance for: {username}")
            result = await self.modules['github'].investigate(username, **kwargs)
            self.results['github'] = result
            logger.info("GitHub reconnaissance completed successfully")
            return result
        except Exception as e:
            logger.error(f"GitHub reconnaissance failed: {e}")
            raise ReconException(f"GitHub recon failed: {e}")
    
    async def run_domain_recon(self, domain: str, **kwargs) -> Dict[str, Any]:
        """Run domain reconnaissance"""
        try:
            logger.info(f"Starting domain reconnaissance for: {domain}")
            result = await self.modules['domain'].investigate(domain, **kwargs)
            self.results['domain'] = result
            logger.info("Domain reconnaissance completed successfully")
            return result
        except Exception as e:
            logger.error(f"Domain reconnaissance failed: {e}")
            raise ReconException(f"Domain recon failed: {e}")
    
    async def run_phone_recon(self, phone_number: str, **kwargs) -> Dict[str, Any]:
        """Run phone number reconnaissance"""
        try:
            logger.info(f"Starting phone reconnaissance for: {phone_number}")
            result = await self.modules['phone'].investigate(phone_number, **kwargs)
            self.results['phone'] = result
            logger.info("Phone reconnaissance completed successfully")
            return result
        except Exception as e:
            logger.error(f"Phone reconnaissance failed: {e}")
            raise ReconException(f"Phone recon failed: {e}")
    
    async def run_linkedin_recon(self, first_name: str, last_name: str, **kwargs) -> Dict[str, Any]:
        """Run LinkedIn reconnaissance"""
        try:
            logger.info(f"Starting LinkedIn reconnaissance for: {first_name} {last_name}")
            result = await self.modules['linkedin'].investigate(first_name, last_name, **kwargs)
            self.results['linkedin'] = result
            logger.info("LinkedIn reconnaissance completed successfully")
            return result
        except Exception as e:
            logger.error(f"LinkedIn reconnaissance failed: {e}")
            raise ReconException(f"LinkedIn recon failed: {e}")
    
    async def run_shodan_recon(self, target: str, **kwargs) -> Dict[str, Any]:
        """Run Shodan reconnaissance"""
        try:
            logger.info(f"Starting Shodan reconnaissance for: {target}")
            result = await self.modules['shodan'].investigate(target, **kwargs)
            self.results['shodan'] = result
            logger.info("Shodan reconnaissance completed successfully")
            return result
        except Exception as e:
            logger.error(f"Shodan reconnaissance failed: {e}")
            raise ReconException(f"Shodan recon failed: {e}")
    
    async def run_comprehensive_recon(self, targets: Dict[str, str]) -> Dict[str, Any]:
        """Run comprehensive reconnaissance on multiple targets"""
        logger.info("Starting comprehensive reconnaissance")
        
        tasks = []
        
        if 'github_username' in targets:
            tasks.append(self.run_github_recon(targets['github_username']))
        
        if 'domain' in targets:
            tasks.append(self.run_domain_recon(targets['domain']))
        
        if 'phone_number' in targets:
            tasks.append(self.run_phone_recon(targets['phone_number']))
        
        if 'linkedin_name' in targets:
            names = targets['linkedin_name'].split(' ', 1)
            if len(names) >= 2:
                tasks.append(self.run_linkedin_recon(names[0], names[1]))
        
        if 'shodan_target' in targets:
            tasks.append(self.run_shodan_recon(targets['shodan_target']))
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        comprehensive_results = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'targets': targets,
            'results': self.results,
            'summary': self._generate_summary()
        }
        
        # Save results if configured
        if config.get("settings.save_results", True):
            await self._save_results(comprehensive_results)
        
        logger.info("Comprehensive reconnaissance completed")
        return comprehensive_results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of reconnaissance results"""
        summary = {
            'total_modules_run': len(self.results),
            'successful_modules': [],
            'failed_modules': [],
            'key_findings': []
        }
        
        for module, result in self.results.items():
            if result.get('success', False):
                summary['successful_modules'].append(module)
                
                # Extract key findings
                if module == 'github' and result.get('data'):
                    data = result['data']
                    if data.get('public_repos', 0) > 0:
                        summary['key_findings'].append(f"GitHub: {data.get('public_repos')} public repositories found")
                
                elif module == 'domain' and result.get('data'):
                    data = result['data']
                    if data.get('subdomains'):
                        summary['key_findings'].append(f"Domain: {len(data['subdomains'])} subdomains discovered")
                
                elif module == 'phone' and result.get('data'):
                    data = result['data']
                    if data.get('carrier'):
                        summary['key_findings'].append(f"Phone: Carrier identified as {data['carrier']}")
            else:
                summary['failed_modules'].append(module)
        
        return summary
    
    async def _save_results(self, results: Dict[str, Any]):
        """Save results to file"""
        try:
            filename = f"recon_results_{self.session_id}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Results saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def get_module_status(self) -> Dict[str, bool]:
        """Get status of all modules"""
        status = {}
        for name, module in self.modules.items():
            try:
                status[name] = module.is_configured()
            except:
                status[name] = False
        return status
    
    def clear_results(self):
        """Clear current results"""
        self.results.clear()
        logger.info("Results cleared")
    
    def get_results(self) -> Dict[str, Any]:
        """Get current results"""
        return self.results.copy() 