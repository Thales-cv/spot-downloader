from ui import App
from downloader import SpotifyDownloader
from config import Config
from assistant import AIAssistant

# Global instance to prevent re-initialization error
downloader = None
assistant = AIAssistant()

def get_downloader():
    global downloader
    if downloader is None:
        downloader = SpotifyDownloader()
    return downloader

def start_download_bridge(url, folder, use_ai, app_instance):
    """
    Bridge function to run the downloader from the UI thread.
    """
    # Validate keys if using AI
    if use_ai:
        valid, msg = Config.validate_openai()
        if not valid:
            app_instance.log(f"[Error] {msg}")
            app_instance.download_finished()
            return

    dl = get_downloader()
    dl.run(url, folder, use_ai, app_instance)

def start_organize_bridge(folder, use_ai, app_instance):
    """
    Bridge function to run organization.
    """
    if use_ai:
        valid, msg = Config.validate_openai()
        if not valid:
            app_instance.log(f"[Error] {msg}")
            app_instance.organization_finished()
            return
            
    dl = get_downloader()
    storage_mode = app_instance.request_storage_mode(None)
    dl.organize_existing(folder, app_instance, use_ai, storage_mode)

if __name__ == "__main__":
    app = App(start_download_bridge, start_organize_bridge, assistant=assistant)
    app.mainloop()
