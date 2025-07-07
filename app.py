import os
import sys
import logging
import json
import subprocess
import threading
import time
import shutil
from pathlib import Path
from flask import Flask, request, jsonify
from simple_justwatch_python_api import JustWatch
import schedule
import yaml
from arr_integration import ArrIntegration
from content_matcher import ContentMatcher

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SVTPlayArr:
    def __init__(self):
        self.config = self.load_config()
        self.justwatch = JustWatch(country='SE')
        self.justwatch_no = JustWatch(country='NO')
        self.arr_integration = ArrIntegration()
        self.content_matcher = ContentMatcher()
        
    def load_config(self):
        config_path = Path('/config/config.yml')
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return self.create_default_config()
    
    def create_default_config(self):
        default_config = {
            'svtplay_dl': {
                'quality': 'best',
                'subtitle': True,
                'force_subtitle': False,
                'output': '/downloads/{type}/{title}',
                'remux': False,
                'merge_subtitle': False,
                'thumbnail': False
            },
            'providers': {
                'svt_play': True,
                'nrk': True
            },
            'paths': {
                'movies': '/downloads/movies',
                'tv': '/downloads/tv'
            }
        }
        
        config_path = Path('/config/config.yml')
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    def search_content(self, title, media_type='tv'):
        results = {'svt': [], 'nrk': []}
        
        if self.config['providers']['svt_play']:
            try:
                svt_results = self.justwatch.search_for_item(query=title)
                for item in svt_results:
                    if 'SVT Play' in [offer['provider_id'] for offer in item.get('offers', [])]:
                        results['svt'].append(item)
            except Exception as e:
                logger.error(f"SVT search error: {e}")
        
        if self.config['providers']['nrk']:
            try:
                nrk_results = self.justwatch_no.search_for_item(query=title)
                for item in nrk_results:
                    if 'NRK TV' in [offer['provider_id'] for offer in item.get('offers', [])]:
                        results['nrk'].append(item)
            except Exception as e:
                logger.error(f"NRK search error: {e}")
        
        return results
    
    def build_svtplay_dl_command(self, url, output_path, media_type):
        config = self.config['svtplay_dl']
        cmd = ['svtplay-dl']
        
        # Quality
        if config.get('quality'):
            cmd.extend(['-q', str(config['quality'])])
        
        # Subtitles
        if config.get('subtitle'):
            cmd.append('--subtitle')
        
        if config.get('force_subtitle'):
            cmd.append('--force-subtitle')
        
        # Output path
        cmd.extend(['-o', output_path])
        
        # Remux
        if config.get('remux'):
            cmd.append('--remux')
        
        # Merge subtitles
        if config.get('merge_subtitle'):
            cmd.append('--merge-subtitle')
        
        # Thumbnail
        if config.get('thumbnail'):
            cmd.append('--thumbnail')
        
        cmd.append(url)
        return cmd
    
    def download_content(self, url, title, media_type='tv'):
        try:
            # Determine output path
            base_path = self.config['paths'][media_type]
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_path = os.path.join(base_path, safe_title)
            
            # Create directory
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Build command
            cmd = self.build_svtplay_dl_command(url, output_path, media_type)
            
            logger.info(f"Starting download: {' '.join(cmd)}")
            
            # Execute download
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info(f"Download completed: {title}")
                self.notify_arr_services(title, media_type, output_path)
                return True
            else:
                logger.error(f"Download failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    def notify_arr_services(self, title, media_type, path):
        logger.info(f"Notifying arr services: {title} at {path}")
        
        if media_type == 'movie':
            self.arr_integration.notify_radarr_download(title, path)
        else:
            self.arr_integration.notify_sonarr_download(title, path)
    
    def notify_radarr(self, title, path):
        return self.arr_integration.notify_radarr_download(title, path)
    
    def notify_sonarr(self, title, path):
        return self.arr_integration.notify_sonarr_download(title, path)

svtplayarr = SVTPlayArr()

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract request details
        media_type = data.get('media', {}).get('mediaType', 'tv')
        title = data.get('media', {}).get('title', '')
        
        if not title:
            return jsonify({'error': 'No title provided'}), 400
        
        logger.info(f"Processing request for: {title} ({media_type})")
        
        # Search for content
        results = svtplayarr.search_content(title, media_type)
        
        if not results['svt'] and not results['nrk']:
            logger.info(f"Content not found on SVT/NRK: {title}")
            return jsonify({'message': 'Content not available on supported platforms'}), 404
        
        # Try to download from available sources
        downloaded = False
        
        # First try JustWatch results
        for provider, items in results.items():
            if items and not downloaded:
                urls = svtplayarr.content_matcher.extract_urls_from_justwatch(items, provider)
                if urls:
                    best_url = svtplayarr.content_matcher.get_best_match_url(urls, title)
                    if best_url and svtplayarr.download_content(best_url, title, media_type):
                        downloaded = True
                        break
        
        # Fallback to direct search if JustWatch didn't work
        if not downloaded:
            for provider in ['svt', 'nrk']:
                if not downloaded and svtplayarr.config['providers'].get(f'{provider}_play' if provider == 'svt' else provider):
                    direct_urls = svtplayarr.content_matcher.find_direct_urls(title, provider)
                    if direct_urls:
                        best_url = svtplayarr.content_matcher.get_best_match_url(direct_urls, title)
                        if best_url and svtplayarr.download_content(best_url, title, media_type):
                            downloaded = True
                            break
        
        if downloaded:
            return jsonify({'message': f'Download started for {title}'})
        else:
            return jsonify({'error': 'Failed to start download'}), 500
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search():
    title = request.args.get('title')
    media_type = request.args.get('type', 'tv')
    
    if not title:
        return jsonify({'error': 'Title parameter required'}), 400
    
    results = svtplayarr.search_content(title, media_type)
    return jsonify(results)

@app.route('/config')
def get_config():
    return jsonify(svtplayarr.config)

@app.route('/config', methods=['POST'])
def update_config():
    try:
        new_config = request.get_json()
        if new_config:
            svtplayarr.config.update(new_config)
            
            config_path = Path('/config/config.yml')
            with open(config_path, 'w') as f:
                yaml.dump(svtplayarr.config, f, default_flow_style=False)
            
            return jsonify({'message': 'Configuration updated'})
        return jsonify({'error': 'No configuration provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_svtplay_dl():
    try:
        logger.info("Updating svtplay-dl")
        result = subprocess.run(
            ['pip', 'install', '--upgrade', 'git+https://github.com/spaam/svtplay-dl.git'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info("svtplay-dl updated successfully")
        else:
            logger.error(f"Failed to update svtplay-dl: {result.stderr}")
    except Exception as e:
        logger.error(f"Update error: {e}")

def run_scheduler():
    schedule.every().day.at("02:00").do(update_svtplay_dl)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=2626, debug=False)
