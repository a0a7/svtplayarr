import requests
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ArrIntegration:
    def __init__(self):
        self.sonarr_url = os.environ.get('SONARR_URL')
        self.sonarr_api_key = os.environ.get('SONARR_API_KEY')
        self.radarr_url = os.environ.get('RADARR_URL')
        self.radarr_api_key = os.environ.get('RADARR_API_KEY')
    
    def notify_sonarr_download(self, title: str, path: str) -> bool:
        if not self.sonarr_url or not self.sonarr_api_key:
            logger.warning("Sonarr configuration missing")
            return False
        
        try:
            # Trigger Sonarr to scan the download folder
            url = f"{self.sonarr_url}/api/v3/command"
            headers = {'X-Api-Key': self.sonarr_api_key}
            
            payload = {
                'name': 'DownloadedEpisodesScan',
                'path': path
            }
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                logger.info(f"Sonarr scan triggered for: {path}")
                return True
            else:
                logger.error(f"Sonarr notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Sonarr notification error: {e}")
            return False
    
    def notify_radarr_download(self, title: str, path: str) -> bool:
        if not self.radarr_url or not self.radarr_api_key:
            logger.warning("Radarr configuration missing")
            return False
        
        try:
            # Trigger Radarr to scan the download folder
            url = f"{self.radarr_url}/api/v3/command"
            headers = {'X-Api-Key': self.radarr_api_key}
            
            payload = {
                'name': 'DownloadedMoviesScan',
                'path': path
            }
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                logger.info(f"Radarr scan triggered for: {path}")
                return True
            else:
                logger.error(f"Radarr notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Radarr notification error: {e}")
            return False
    
    def get_sonarr_series(self, title: str) -> Optional[Dict]:
        if not self.sonarr_url or not self.sonarr_api_key:
            return None
        
        try:
            url = f"{self.sonarr_url}/api/v3/series"
            headers = {'X-Api-Key': self.sonarr_api_key}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                series_list = response.json()
                for series in series_list:
                    if title.lower() in series.get('title', '').lower():
                        return series
            
        except Exception as e:
            logger.error(f"Sonarr series lookup error: {e}")
        
        return None
    
    def get_radarr_movie(self, title: str) -> Optional[Dict]:
        if not self.radarr_url or not self.radarr_api_key:
            return None
        
        try:
            url = f"{self.radarr_url}/api/v3/movie"
            headers = {'X-Api-Key': self.radarr_api_key}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                movies_list = response.json()
                for movie in movies_list:
                    if title.lower() in movie.get('title', '').lower():
                        return movie
            
        except Exception as e:
            logger.error(f"Radarr movie lookup error: {e}")
        
        return None
