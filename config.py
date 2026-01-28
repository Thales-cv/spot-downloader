import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # App Settings
    APP_NAME = "Spotify Link to MP3 Downloader"
    APP_SIZE = "800x600"
    THEME_COLOR = "green"  # system theme

    @staticmethod
    def validate_openai():
        if not Config.OPENAI_API_KEY:
            return False, "Missing OPENAI_API_KEY in .env file."
        return True, "OK"
