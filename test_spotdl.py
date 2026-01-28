from spotdl import Spotdl
from spotdl.types.song import Song
import asyncio

from config import Config

print("Initializing SpotDL...")
spotdl = Spotdl(client_id=Config.SPOTIFY_CLIENT_ID, client_secret=Config.SPOTIFY_CLIENT_SECRET)
print("Searching...")
# Use a known safe song
songs = spotdl.search(["https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"])
song = songs[0]
print(f"Found: {song.name}")

print("Attempting download...")
try:
    print("Using download_songs([song])...")
    res_list = spotdl.download_songs([song])
    print(f"Result type: {type(res_list)}")
    print(f"Result: {res_list}")
    if res_list:
        print(f"First path: {res_list[0][1]}")
except Exception as e:
    print(f"Error: {e}")
