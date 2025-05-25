"""
LinkedIn reconnaissance module for xPOURY4 Recon
Author: xPOURY4
"""

import webbrowser
import urllib.parse
from typing import Dict, Any
from .base_module import BaseReconModule
from ..core.config_manager import config
from ..core.logger import logger
from ..core.exceptions import ValidationException


class LinkedInRecon(BaseReconModule):
    """Enhanced LinkedIn reconnaissance module"""
    
    def __init__(self):
        super().__init__("linkedin_recon")
        self.auto_open_browser = config.get("modules.linkedin_recon.auto_open_browser", True)
    
    def is_configured(self) -> bool:
        """Check if module is properly configured"""
        return True  # No API keys required for basic LinkedIn search
    
    def _validate_name(self, name: str) -> bool:
        """Validate name format"""
        return bool(name and name.strip() and len(name.strip()) >= 2)
    
    async def investigate(self, first_name: str, last_name: str, **kwargs) -> Dict[str, Any]:
        """Investigate LinkedIn profiles"""
        try:
            if not self._validate_name(first_name) or not self._validate_name(last_name):
                raise ValidationException("Invalid name format")
            
            # Get additional search parameters
            company = kwargs.get('company', '')
            location = kwargs.get('location', '')
            keywords = kwargs.get('keywords', [])
            
            # Generate search queries
            search_queries = self._generate_search_queries(
                first_name, last_name, company, location, keywords
            )
            
            # Generate search URLs
            search_urls = []
            for query in search_queries:
                url = self._generate_search_url(query)
                search_urls.append({
                    'query': query,
                    'url': url,
                    'description': self._describe_query(query)
                })
            
            # Open browser if configured
            if self.auto_open_browser and search_urls:
                try:
                    webbrowser.open(search_urls[0]['url'])
                    logger.info(f"Opened LinkedIn search in browser for: {first_name} {last_name}")
                except Exception as e:
                    logger.warning(f"Failed to open browser: {e}")
            
            result_data = {
                'target': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'company': company,
                    'location': location,
                    'keywords': keywords
                },
                'search_queries': search_queries,
                'search_urls': search_urls,
                'recommendations': self._generate_recommendations(first_name, last_name, company)
            }
            
            return self.format_result(True, result_data)
            
        except Exception as e:
            logger.error(f"LinkedIn reconnaissance failed for {first_name} {last_name}: {e}")
            return self.format_result(False, error=str(e))
    
    def _generate_search_queries(self, first_name: str, last_name: str, 
                                company: str = '', location: str = '', 
                                keywords: list = None) -> list:
        """Generate multiple search queries for LinkedIn"""
        keywords = keywords or []
        queries = []
        
        # Basic name search
        base_query = f'site:linkedin.com/in "{first_name} {last_name}"'
        queries.append(base_query)
        
        # Name with company
        if company:
            company_query = f'site:linkedin.com/in "{first_name} {last_name}" "{company}"'
            queries.append(company_query)
        
        # Name with location
        if location:
            location_query = f'site:linkedin.com/in "{first_name} {last_name}" "{location}"'
            queries.append(location_query)
        
        # Name with keywords
        if keywords:
            for keyword in keywords[:3]:  # Limit to 3 keywords
                keyword_query = f'site:linkedin.com/in "{first_name} {last_name}" "{keyword}"'
                queries.append(keyword_query)
        
        # Combined search
        if company and location:
            combined_query = f'site:linkedin.com/in "{first_name} {last_name}" "{company}" "{location}"'
            queries.append(combined_query)
        
        # Alternative name formats
        queries.append(f'site:linkedin.com/in "{first_name[0]}. {last_name}"')  # F. Lastname
        queries.append(f'site:linkedin.com/in "{first_name} {last_name[0]}."')  # Firstname L.
        
        return queries
    
    def _generate_search_url(self, query: str) -> str:
        """Generate Google search URL for LinkedIn"""
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/search?q={encoded_query}"
    
    def _describe_query(self, query: str) -> str:
        """Generate description for search query"""
        if '"' in query:
            # Extract quoted terms
            quoted_terms = []
            parts = query.split('"')[1::2]  # Get every other element starting from index 1
            quoted_terms.extend(parts)
            
            if len(quoted_terms) == 1:
                return f"Basic search for {quoted_terms[0]}"
            elif len(quoted_terms) == 2:
                return f"Search for {quoted_terms[0]} at {quoted_terms[1]}"
            else:
                return f"Advanced search with multiple criteria"
        
        return "LinkedIn profile search"
    
    def _generate_recommendations(self, first_name: str, last_name: str, company: str = '') -> list:
        """Generate search recommendations"""
        recommendations = [
            "Try searching with different name variations (nicknames, middle names)",
            "Search for the person's company or organization separately",
            "Look for mutual connections who might know the target",
            "Check for the person's presence on other social media platforms",
            "Search for professional associations or groups they might belong to"
        ]
        
        if company:
            recommendations.append(f"Search for other employees at {company} who might be connected")
        
        recommendations.extend([
            "Use LinkedIn's advanced search filters if you have a premium account",
            "Look for the person in LinkedIn groups related to their industry",
            "Check for any published articles or posts by the person",
            "Search for the person's email address or phone number if available"
        ])
        
        return recommendations 