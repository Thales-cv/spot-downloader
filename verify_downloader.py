import os
from downloader import SpotifyDownloader
from config import Config

# Mock App Class
class MockApp:
    def log(self, message):
        print(f"[LOG] {message}")
    
    def download_finished(self):
        print("[STATUS] Download Finished")
        
    def organization_finished(self):
        print("[STATUS] Organization Finished")

import threading
import time

def run_download_thread(downloader, url, output, app):
    try:
        downloader.run(url, output, use_ai=False, app_instance=app)
    except Exception as e:
        print(f"[THREAD ERROR] {e}")

def test_downloader():
    print("Testing SpotifyDownloader...")
    
    # Ensure client ID/Secret are available (assuming they are in env or config)
    # Config.SPOTIFY_CLIENT_ID and Config.SPOTIFY_CLIENT_SECRET
    
    downloader = SpotifyDownloader()
    mock_app = MockApp()
    
    # URL that worked in test_spotdl.py
    test_url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT" 
    output_folder = "test_output"
    
    print(f"Downloading {test_url} to {output_folder}")
    
    # Run in a separate thread like the UI does
    t = threading.Thread(target=run_download_thread, args=(downloader, test_url, output_folder, mock_app))
    t.start()
    t.join()

if __name__ == "__main__":
    test_downloader()
