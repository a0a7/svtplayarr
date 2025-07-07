import re
import requests
import logging
from typing import Optional, List, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ContentMatcher:
    def __init__(self):
        self.svt_patterns = [
            r'svtplay\.se',
            r'svt\.se/video',
            r'oppetarkiv\.se'
        ]
        self.nrk_patterns = [
            r'nrk\.no',
            r'tv\.nrk\.no'
        ]
    
    def extract_urls_from_justwatch(self, items: List[Dict], provider: str) -> List[str]:
        urls = []
        
        for item in items:
            # Extract URLs from JustWatch item
            offers = item.get('offers', [])
            for offer in offers:
                if provider.lower() in offer.get('provider_id', '').lower():
                    url = offer.get('urls', {}).get('standard_web', '')
                    if url:
                        urls.append(url)
        
        return urls
    
    def find_direct_urls(self, title: str, provider: str) -> List[str]:
        urls = []
        
        if provider == 'svt':
            urls.extend(self._search_svt_direct(title))
        elif provider == 'nrk':
            urls.extend(self._search_nrk_direct(title))
        
        return urls
    
    def _search_svt_direct(self, title: str) -> List[str]:
        try:
            # Search SVT Play directly
            search_url = f"https://www.svtplay.se/sok?q={title.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse HTML for video URLs
                urls = re.findall(r'href="(/video/[^"]+)"', response.text)
                return [f"https://www.svtplay.se{url}" for url in urls[:5]]
                
        except Exception as e:
            logger.error(f"SVT direct search error: {e}")
        
        return []
    
    def _search_nrk_direct(self, title: str) -> List[str]:
        try:
            # Search NRK directly
            search_url = f"https://tv.nrk.no/sok?q={title.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse HTML for video URLs
                urls = re.findall(r'href="(/serie/[^"]+|/program/[^"]+)"', response.text)
                return [f"https://tv.nrk.no{url}" for url in urls[:5]]
                
        except Exception as e:
            logger.error(f"NRK direct search error: {e}")
        
        return []
    
    def validate_url(self, url: str, provider: str) -> bool:
        patterns = self.svt_patterns if provider == 'svt' else self.nrk_patterns
        
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def get_best_match_url(self, urls: List[str], title: str) -> Optional[str]:
        if not urls:
            return None
        
        # Simple scoring based on URL content
        scored_urls = []
        title_words = title.lower().split()
        
        for url in urls:
            score = 0
            url_lower = url.lower()
            
            for word in title_words:
                if word in url_lower:
                    score += 1
            
            scored_urls.append((score, url))
        
        # Sort by score and return best match
        scored_urls.sort(key=lambda x: x[0], reverse=True)
        return scored_urls[0][1] if scored_urls else urls[0]
