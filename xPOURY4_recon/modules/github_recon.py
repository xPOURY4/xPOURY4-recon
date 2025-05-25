"""
GitHub reconnaissance module for xPOURY4 Recon
Author: xPOURY4
"""

import re
from typing import Dict, Any, List
from .base_module import BaseReconModule
from ..core.config_manager import config
from ..core.logger import logger
from ..core.exceptions import ValidationException


class GitHubRecon(BaseReconModule):
    """Enhanced GitHub reconnaissance module"""
    
    def __init__(self):
        super().__init__("github_recon")
        self.api_token = config.get("api_keys.github_token")
        self.base_url = "https://api.github.com"
        self.include_repos = config.get("modules.github_recon.include_repos", True)
        self.include_gists = config.get("modules.github_recon.include_gists", True)
        self.max_repos = config.get("modules.github_recon.max_repos", 100)
    
    def is_configured(self) -> bool:
        """Check if GitHub token is configured"""
        return bool(self.api_token and self.api_token != "")
    
    def _validate_username(self, username: str) -> bool:
        """Validate GitHub username format"""
        pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$'
        return bool(re.match(pattern, username))
    
    async def investigate(self, username: str, **kwargs) -> Dict[str, Any]:
        """Investigate GitHub user"""
        try:
            if not self.validate_input(username, self._validate_username):
                raise ValidationException(f"Invalid GitHub username: {username}")
            
            if not self.is_configured():
                logger.warning("GitHub token not configured. Some features may be limited.")
            
            async with self:
                # Get user profile
                user_data = await self._get_user_profile(username)
                
                # Get repositories if enabled
                repos_data = []
                if self.include_repos:
                    repos_data = await self._get_user_repositories(username)
                
                # Get gists if enabled
                gists_data = []
                if self.include_gists:
                    gists_data = await self._get_user_gists(username)
                
                # Get organizations
                orgs_data = await self._get_user_organizations(username)
                
                # Get events (recent activity)
                events_data = await self._get_user_events(username)
                
                result_data = {
                    'profile': user_data,
                    'repositories': repos_data,
                    'gists': gists_data,
                    'organizations': orgs_data,
                    'recent_activity': events_data,
                    'statistics': self._generate_statistics(user_data, repos_data, gists_data)
                }
                
                return self.format_result(True, result_data)
                
        except Exception as e:
            logger.error(f"GitHub reconnaissance failed for {username}: {e}")
            return self.format_result(False, error=str(e))
    
    async def _get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile information"""
        url = f"{self.base_url}/users/{username}"
        headers = {}
        
        if self.api_token:
            headers['Authorization'] = f"token {self.api_token}"
        
        response = await self.make_request(url, headers=headers)
        
        return {
            'username': response.get('login'),
            'name': response.get('name'),
            'bio': response.get('bio'),
            'location': response.get('location'),
            'company': response.get('company'),
            'email': response.get('email'),
            'blog': response.get('blog'),
            'twitter_username': response.get('twitter_username'),
            'avatar_url': response.get('avatar_url'),
            'html_url': response.get('html_url'),
            'created_at': response.get('created_at'),
            'updated_at': response.get('updated_at'),
            'public_repos': response.get('public_repos', 0),
            'public_gists': response.get('public_gists', 0),
            'followers': response.get('followers', 0),
            'following': response.get('following', 0),
            'hireable': response.get('hireable'),
            'type': response.get('type'),
            'site_admin': response.get('site_admin', False)
        }
    
    async def _get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get user repositories"""
        url = f"{self.base_url}/users/{username}/repos"
        headers = {}
        
        if self.api_token:
            headers['Authorization'] = f"token {self.api_token}"
        
        params = {
            'sort': 'updated',
            'per_page': min(self.max_repos, 100)
        }
        
        try:
            response = await self.make_request(url, headers=headers, params=params)
            
            repos = []
            for repo in response[:self.max_repos]:
                repos.append({
                    'name': repo.get('name'),
                    'full_name': repo.get('full_name'),
                    'description': repo.get('description'),
                    'html_url': repo.get('html_url'),
                    'clone_url': repo.get('clone_url'),
                    'language': repo.get('language'),
                    'size': repo.get('size'),
                    'stargazers_count': repo.get('stargazers_count', 0),
                    'watchers_count': repo.get('watchers_count', 0),
                    'forks_count': repo.get('forks_count', 0),
                    'open_issues_count': repo.get('open_issues_count', 0),
                    'created_at': repo.get('created_at'),
                    'updated_at': repo.get('updated_at'),
                    'pushed_at': repo.get('pushed_at'),
                    'private': repo.get('private', False),
                    'fork': repo.get('fork', False),
                    'archived': repo.get('archived', False),
                    'disabled': repo.get('disabled', False),
                    'topics': repo.get('topics', [])
                })
            
            return repos
            
        except Exception as e:
            logger.warning(f"Failed to get repositories for {username}: {e}")
            return []
    
    async def _get_user_gists(self, username: str) -> List[Dict[str, Any]]:
        """Get user gists"""
        url = f"{self.base_url}/users/{username}/gists"
        headers = {}
        
        if self.api_token:
            headers['Authorization'] = f"token {self.api_token}"
        
        try:
            response = await self.make_request(url, headers=headers)
            
            gists = []
            for gist in response[:50]:  # Limit to 50 gists
                gists.append({
                    'id': gist.get('id'),
                    'description': gist.get('description'),
                    'html_url': gist.get('html_url'),
                    'public': gist.get('public', False),
                    'created_at': gist.get('created_at'),
                    'updated_at': gist.get('updated_at'),
                    'files': list(gist.get('files', {}).keys()),
                    'comments': gist.get('comments', 0)
                })
            
            return gists
            
        except Exception as e:
            logger.warning(f"Failed to get gists for {username}: {e}")
            return []
    
    async def _get_user_organizations(self, username: str) -> List[Dict[str, Any]]:
        """Get user organizations"""
        url = f"{self.base_url}/users/{username}/orgs"
        headers = {}
        
        if self.api_token:
            headers['Authorization'] = f"token {self.api_token}"
        
        try:
            response = await self.make_request(url, headers=headers)
            
            orgs = []
            for org in response:
                orgs.append({
                    'login': org.get('login'),
                    'description': org.get('description'),
                    'html_url': org.get('html_url'),
                    'avatar_url': org.get('avatar_url')
                })
            
            return orgs
            
        except Exception as e:
            logger.warning(f"Failed to get organizations for {username}: {e}")
            return []
    
    async def _get_user_events(self, username: str) -> List[Dict[str, Any]]:
        """Get user recent events"""
        url = f"{self.base_url}/users/{username}/events/public"
        headers = {}
        
        if self.api_token:
            headers['Authorization'] = f"token {self.api_token}"
        
        try:
            response = await self.make_request(url, headers=headers)
            
            events = []
            for event in response[:20]:  # Limit to 20 recent events
                events.append({
                    'type': event.get('type'),
                    'repo': event.get('repo', {}).get('name'),
                    'created_at': event.get('created_at'),
                    'public': event.get('public', False)
                })
            
            return events
            
        except Exception as e:
            logger.warning(f"Failed to get events for {username}: {e}")
            return []
    
    def _generate_statistics(self, profile: Dict, repos: List, gists: List) -> Dict[str, Any]:
        """Generate statistics from collected data"""
        stats = {
            'total_repos': len(repos),
            'total_gists': len(gists),
            'total_stars': sum(repo.get('stargazers_count', 0) for repo in repos),
            'total_forks': sum(repo.get('forks_count', 0) for repo in repos),
            'languages': {},
            'most_starred_repo': None,
            'account_age_days': None
        }
        
        # Language statistics
        for repo in repos:
            lang = repo.get('language')
            if lang:
                stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
        
        # Most starred repository
        if repos:
            most_starred = max(repos, key=lambda x: x.get('stargazers_count', 0))
            if most_starred.get('stargazers_count', 0) > 0:
                stats['most_starred_repo'] = {
                    'name': most_starred.get('name'),
                    'stars': most_starred.get('stargazers_count'),
                    'url': most_starred.get('html_url')
                }
        
        # Account age
        if profile.get('created_at'):
            from datetime import datetime
            created = datetime.fromisoformat(profile['created_at'].replace('Z', '+00:00'))
            age = datetime.now(created.tzinfo) - created
            stats['account_age_days'] = age.days
        
        return stats 