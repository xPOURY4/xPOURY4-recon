"""
Domain reconnaissance module for xPOURY4 Recon
Author: xPOURY4
"""

import re
import socket
import asyncio
import whois
from typing import Dict, Any, List, Set
from .base_module import BaseReconModule
from ..core.config_manager import config
from ..core.logger import logger
from ..core.exceptions import ValidationException


class DomainRecon(BaseReconModule):
    """Enhanced domain reconnaissance module"""
    
    def __init__(self):
        super().__init__("domain_recon")
        self.subdomain_sources = config.get("modules.domain_recon.subdomain_sources", 
                                           ["crt.sh", "threatcrowd", "virustotal"])
        self.dns_servers = config.get("modules.domain_recon.dns_servers", 
                                    ["8.8.8.8", "1.1.1.1"])
        self.virustotal_api_key = config.get("api_keys.virustotal_api_key")
    
    def is_configured(self) -> bool:
        """Check if module is properly configured"""
        return True  # Basic functionality doesn't require API keys
    
    def _validate_domain(self, domain: str) -> bool:
        """Validate domain format"""
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    async def investigate(self, domain: str, **kwargs) -> Dict[str, Any]:
        """Investigate domain"""
        try:
            if not self.validate_input(domain, self._validate_domain):
                raise ValidationException(f"Invalid domain format: {domain}")
            
            async with self:
                # Get WHOIS information
                whois_data = await self._get_whois_info(domain)
                
                # Get DNS records
                dns_data = await self._get_dns_records(domain)
                
                # Get subdomains
                subdomains_data = await self._get_subdomains(domain)
                
                # Get SSL certificate information
                ssl_data = await self._get_ssl_info(domain)
                
                # Get domain reputation (if VirusTotal API is available)
                reputation_data = await self._get_domain_reputation(domain)
                
                result_data = {
                    'domain': domain,
                    'whois': whois_data,
                    'dns_records': dns_data,
                    'subdomains': subdomains_data,
                    'ssl_certificate': ssl_data,
                    'reputation': reputation_data,
                    'statistics': self._generate_statistics(subdomains_data, dns_data)
                }
                
                return self.format_result(True, result_data)
                
        except Exception as e:
            logger.error(f"Domain reconnaissance failed for {domain}: {e}")
            return self.format_result(False, error=str(e))
    
    async def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information"""
        try:
            # Run WHOIS lookup in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            whois_data = await loop.run_in_executor(None, whois.whois, domain)
            
            return {
                'domain_name': whois_data.domain_name,
                'registrar': whois_data.registrar,
                'creation_date': str(whois_data.creation_date) if whois_data.creation_date else None,
                'expiration_date': str(whois_data.expiration_date) if whois_data.expiration_date else None,
                'updated_date': str(whois_data.updated_date) if whois_data.updated_date else None,
                'name_servers': whois_data.name_servers,
                'status': whois_data.status,
                'emails': whois_data.emails,
                'country': getattr(whois_data, 'country', None),
                'org': getattr(whois_data, 'org', None)
            }
            
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")
            return {'error': str(e)}
    
    async def _get_dns_records(self, domain: str) -> Dict[str, List[str]]:
        """Get DNS records"""
        dns_records = {
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'CNAME': []
        }
        
        try:
            loop = asyncio.get_event_loop()
            
            # A records
            try:
                a_records = await loop.run_in_executor(None, socket.gethostbyname_ex, domain)
                dns_records['A'] = a_records[2]
            except:
                pass
            
            # Additional DNS lookups would require dnspython library
            # For now, we'll keep it simple with basic socket operations
            
        except Exception as e:
            logger.warning(f"DNS lookup failed for {domain}: {e}")
        
        return dns_records
    
    async def _get_subdomains(self, domain: str) -> Dict[str, Any]:
        """Get subdomains from multiple sources"""
        all_subdomains = set()
        sources_used = []
        
        # Certificate Transparency logs (crt.sh)
        if "crt.sh" in self.subdomain_sources:
            crt_subdomains = await self._get_crtsh_subdomains(domain)
            all_subdomains.update(crt_subdomains)
            sources_used.append("crt.sh")
        
        # ThreatCrowd
        if "threatcrowd" in self.subdomain_sources:
            tc_subdomains = await self._get_threatcrowd_subdomains(domain)
            all_subdomains.update(tc_subdomains)
            sources_used.append("threatcrowd")
        
        # VirusTotal (if API key is available)
        if "virustotal" in self.subdomain_sources and self.virustotal_api_key:
            vt_subdomains = await self._get_virustotal_subdomains(domain)
            all_subdomains.update(vt_subdomains)
            sources_used.append("virustotal")
        
        return {
            'subdomains': sorted(list(all_subdomains)),
            'count': len(all_subdomains),
            'sources_used': sources_used
        }
    
    async def _get_crtsh_subdomains(self, domain: str) -> Set[str]:
        """Get subdomains from Certificate Transparency logs"""
        subdomains = set()
        
        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            response = await self.make_request(url)
            
            for entry in response:
                name_value = entry.get('name_value', '')
                # Split by newlines as crt.sh can return multiple domains per entry
                for subdomain in name_value.split('\n'):
                    subdomain = subdomain.strip()
                    if subdomain and not subdomain.startswith('*'):
                        subdomains.add(subdomain)
            
        except Exception as e:
            logger.warning(f"crt.sh lookup failed for {domain}: {e}")
        
        return subdomains
    
    async def _get_threatcrowd_subdomains(self, domain: str) -> Set[str]:
        """Get subdomains from ThreatCrowd"""
        subdomains = set()
        
        try:
            url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"
            response = await self.make_request(url)
            
            if response.get('subdomains'):
                subdomains.update(response['subdomains'])
            
        except Exception as e:
            logger.warning(f"ThreatCrowd lookup failed for {domain}: {e}")
        
        return subdomains
    
    async def _get_virustotal_subdomains(self, domain: str) -> Set[str]:
        """Get subdomains from VirusTotal"""
        subdomains = set()
        
        if not self.virustotal_api_key:
            return subdomains
        
        try:
            url = f"https://www.virustotal.com/vtapi/v2/domain/report"
            params = {
                'apikey': self.virustotal_api_key,
                'domain': domain
            }
            
            response = await self.make_request(url, params=params)
            
            if response.get('subdomains'):
                subdomains.update(response['subdomains'])
            
        except Exception as e:
            logger.warning(f"VirusTotal lookup failed for {domain}: {e}")
        
        return subdomains
    
    async def _get_ssl_info(self, domain: str) -> Dict[str, Any]:
        """Get SSL certificate information"""
        try:
            import ssl
            import socket
            
            loop = asyncio.get_event_loop()
            
            def get_cert_info():
                context = ssl.create_default_context()
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        return cert
            
            cert_info = await loop.run_in_executor(None, get_cert_info)
            
            return {
                'subject': dict(x[0] for x in cert_info.get('subject', [])),
                'issuer': dict(x[0] for x in cert_info.get('issuer', [])),
                'version': cert_info.get('version'),
                'serial_number': cert_info.get('serialNumber'),
                'not_before': cert_info.get('notBefore'),
                'not_after': cert_info.get('notAfter'),
                'signature_algorithm': cert_info.get('signatureAlgorithm'),
                'subject_alt_names': [x[1] for x in cert_info.get('subjectAltName', [])]
            }
            
        except Exception as e:
            logger.warning(f"SSL certificate lookup failed for {domain}: {e}")
            return {'error': str(e)}
    
    async def _get_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Get domain reputation from VirusTotal"""
        if not self.virustotal_api_key:
            return {'error': 'VirusTotal API key not configured'}
        
        try:
            url = f"https://www.virustotal.com/vtapi/v2/domain/report"
            params = {
                'apikey': self.virustotal_api_key,
                'domain': domain
            }
            
            response = await self.make_request(url, params=params)
            
            return {
                'response_code': response.get('response_code'),
                'verbose_msg': response.get('verbose_msg'),
                'positives': response.get('positives', 0),
                'total': response.get('total', 0),
                'scan_date': response.get('scan_date'),
                'permalink': response.get('permalink')
            }
            
        except Exception as e:
            logger.warning(f"VirusTotal reputation lookup failed for {domain}: {e}")
            return {'error': str(e)}
    
    def _generate_statistics(self, subdomains_data: Dict, dns_data: Dict) -> Dict[str, Any]:
        """Generate statistics from collected data"""
        return {
            'total_subdomains': subdomains_data.get('count', 0),
            'subdomain_sources': subdomains_data.get('sources_used', []),
            'dns_records_found': sum(1 for records in dns_data.values() if records),
            'has_a_records': bool(dns_data.get('A')),
            'has_mx_records': bool(dns_data.get('MX')),
            'has_txt_records': bool(dns_data.get('TXT'))
        } 