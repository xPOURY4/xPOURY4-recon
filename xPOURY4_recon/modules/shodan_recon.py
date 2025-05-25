"""
Shodan reconnaissance module for xPOURY4 Recon
Author: xPOURY4
"""

import re
import socket
from typing import Dict, Any, List
from .base_module import BaseReconModule
from ..core.config_manager import config
from ..core.logger import logger
from ..core.exceptions import ValidationException, APIException


class ShodanRecon(BaseReconModule):
    """Enhanced Shodan reconnaissance module"""
    
    def __init__(self):
        super().__init__("shodan_recon")
        self.api_key = config.get("api_keys.shodan_api_key")
        self.base_url = "https://api.shodan.io"
    
    def is_configured(self) -> bool:
        """Check if Shodan API key is configured"""
        return bool(self.api_key and self.api_key != "")
    
    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    def _validate_domain(self, domain: str) -> bool:
        """Validate domain format"""
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    async def investigate(self, target: str, **kwargs) -> Dict[str, Any]:
        """Investigate target using Shodan"""
        try:
            if not self.is_configured():
                return self.format_result(False, error="Shodan API key not configured")
            
            # Determine if target is IP or domain
            is_ip = self._validate_ip(target)
            is_domain = self._validate_domain(target)
            
            if not is_ip and not is_domain:
                raise ValidationException(f"Invalid target format: {target}")
            
            async with self:
                result_data = {}
                
                if is_ip:
                    # Direct IP lookup
                    result_data = await self._investigate_ip(target)
                elif is_domain:
                    # Domain lookup - first resolve to IP, then investigate
                    ips = await self._resolve_domain(target)
                    result_data = await self._investigate_domain(target, ips)
                
                return self.format_result(True, result_data)
                
        except Exception as e:
            logger.error(f"Shodan reconnaissance failed for {target}: {e}")
            return self.format_result(False, error=str(e))
    
    async def _investigate_ip(self, ip: str) -> Dict[str, Any]:
        """Investigate specific IP address"""
        # Get host information
        host_info = await self._get_host_info(ip)
        
        # Get host history
        host_history = await self._get_host_history(ip)
        
        return {
            'target': ip,
            'type': 'ip',
            'host_info': host_info,
            'host_history': host_history,
            'statistics': self._generate_ip_statistics(host_info)
        }
    
    async def _investigate_domain(self, domain: str, ips: List[str]) -> Dict[str, Any]:
        """Investigate domain and its associated IPs"""
        domain_data = {
            'target': domain,
            'type': 'domain',
            'resolved_ips': ips,
            'hosts': [],
            'dns_info': await self._get_dns_info(domain)
        }
        
        # Investigate each resolved IP
        for ip in ips[:5]:  # Limit to 5 IPs to avoid rate limiting
            try:
                host_info = await self._get_host_info(ip)
                domain_data['hosts'].append({
                    'ip': ip,
                    'info': host_info
                })
                await self.rate_limit()  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to get info for IP {ip}: {e}")
        
        domain_data['statistics'] = self._generate_domain_statistics(domain_data)
        return domain_data
    
    async def _resolve_domain(self, domain: str) -> List[str]:
        """Resolve domain to IP addresses"""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            _, _, ips = await loop.run_in_executor(None, socket.gethostbyname_ex, domain)
            return ips
        except Exception as e:
            logger.warning(f"Failed to resolve domain {domain}: {e}")
            return []
    
    async def _get_host_info(self, ip: str) -> Dict[str, Any]:
        """Get host information from Shodan"""
        try:
            url = f"{self.base_url}/shodan/host/{ip}"
            params = {'key': self.api_key}
            
            response = await self.make_request(url, params=params)
            
            return {
                'ip': response.get('ip_str'),
                'hostnames': response.get('hostnames', []),
                'country_name': response.get('country_name'),
                'country_code': response.get('country_code'),
                'city': response.get('city'),
                'region_code': response.get('region_code'),
                'postal_code': response.get('postal_code'),
                'latitude': response.get('latitude'),
                'longitude': response.get('longitude'),
                'organization': response.get('org'),
                'isp': response.get('isp'),
                'asn': response.get('asn'),
                'last_update': response.get('last_update'),
                'ports': response.get('ports', []),
                'vulns': list(response.get('vulns', [])),
                'tags': response.get('tags', []),
                'services': self._extract_services(response.get('data', []))
            }
            
        except APIException as e:
            if e.status_code == 404:
                return {'error': 'No information available for this IP'}
            raise
    
    async def _get_host_history(self, ip: str) -> Dict[str, Any]:
        """Get host history from Shodan"""
        try:
            url = f"{self.base_url}/shodan/host/{ip}/history"
            params = {'key': self.api_key}
            
            response = await self.make_request(url, params=params)
            
            return {
                'total_records': len(response),
                'first_seen': response[0].get('timestamp') if response else None,
                'last_seen': response[-1].get('timestamp') if response else None,
                'scan_history': [
                    {
                        'timestamp': record.get('timestamp'),
                        'port': record.get('port'),
                        'transport': record.get('transport'),
                        'product': record.get('product'),
                        'version': record.get('version')
                    }
                    for record in response[:10]  # Limit to 10 most recent
                ]
            }
            
        except APIException as e:
            if e.status_code == 404:
                return {'error': 'No history available for this IP'}
            return {'error': str(e)}
    
    async def _get_dns_info(self, domain: str) -> Dict[str, Any]:
        """Get DNS information for domain"""
        try:
            url = f"{self.base_url}/dns/domain/{domain}"
            params = {'key': self.api_key}
            
            response = await self.make_request(url, params=params)
            
            return {
                'domain': response.get('domain'),
                'tags': response.get('tags', []),
                'data': response.get('data', []),
                'subdomains': response.get('subdomains', []),
                'more': response.get('more', False)
            }
            
        except APIException as e:
            if e.status_code == 404:
                return {'error': 'No DNS information available for this domain'}
            return {'error': str(e)}
    
    def _extract_services(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """Extract service information from Shodan data"""
        services = []
        
        for service in data:
            services.append({
                'port': service.get('port'),
                'transport': service.get('transport'),
                'product': service.get('product'),
                'version': service.get('version'),
                'banner': service.get('data', '')[:200],  # Limit banner length
                'timestamp': service.get('timestamp'),
                'ssl': bool(service.get('ssl')),
                'location': {
                    'country': service.get('location', {}).get('country_name'),
                    'city': service.get('location', {}).get('city')
                }
            })
        
        return services
    
    def _generate_ip_statistics(self, host_info: Dict) -> Dict[str, Any]:
        """Generate statistics for IP investigation"""
        if host_info.get('error'):
            return {'error': host_info['error']}
        
        return {
            'total_ports': len(host_info.get('ports', [])),
            'total_services': len(host_info.get('services', [])),
            'total_vulnerabilities': len(host_info.get('vulns', [])),
            'has_ssl_services': any(service.get('ssl') for service in host_info.get('services', [])),
            'organization': host_info.get('organization'),
            'country': host_info.get('country_name'),
            'last_seen': host_info.get('last_update')
        }
    
    def _generate_domain_statistics(self, domain_data: Dict) -> Dict[str, Any]:
        """Generate statistics for domain investigation"""
        total_ports = 0
        total_services = 0
        total_vulns = 0
        countries = set()
        
        for host in domain_data.get('hosts', []):
            host_info = host.get('info', {})
            if not host_info.get('error'):
                total_ports += len(host_info.get('ports', []))
                total_services += len(host_info.get('services', []))
                total_vulns += len(host_info.get('vulns', []))
                if host_info.get('country_name'):
                    countries.add(host_info['country_name'])
        
        return {
            'total_ips': len(domain_data.get('resolved_ips', [])),
            'total_ports': total_ports,
            'total_services': total_services,
            'total_vulnerabilities': total_vulns,
            'countries': list(countries),
            'subdomains_found': len(domain_data.get('dns_info', {}).get('subdomains', []))
        } 