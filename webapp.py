import os
import threading
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from assistant import AIAssistant
from downloader import SpotifyDownloader
from config import Config


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "web" / "index.html"


class MessageIn(BaseModel):
    text: str


class WebState:
    def __init__(self):
        self.lock = threading.Lock()
        self.logs = []
        self.playlist = []
        self.count = 0
        self.awaiting_storage = False
        self.storage_mode = ""
        self.storage_event = threading.Event()
        self.output_folder = ""
        self.busy = False

    def add_log(self, text):
        with self.lock:
            self.logs.append(text)

    def snapshot(self, since=0):
        with self.lock:
            new_logs = self.logs[since:]
            return {
                "logs": new_logs,
                "next": len(self.logs),
                "playlist": self.playlist,
                "count": self.count,
                "awaiting_storage": self.awaiting_storage,
            }


state = WebState()
assistant = AIAssistant()

downloader = SpotifyDownloader()


class WebAppAdapter:
    def log(self, message):
        state.add_log(message)

    def ai_message(self, message):
        state.add_log(f"[AI] {message}")

    def show_playlist(self, songs):
        with state.lock:
            state.playlist = [f"{s.artist} - {s.name}" for s in songs]
            state.count = len(songs)

    def request_storage_mode(self, total_songs=None):
        state.awaiting_storage = True
        state.storage_mode = ""
        state.storage_event.clear()
        prompt = assistant.ask_storage_mode(total_songs)
        self.ai_message(prompt)
        state.storage_event.wait()
        state.awaiting_storage = False
        return state.storage_mode or "genre"

    def download_finished(self):
        state.busy = False
        state.add_log("Task Completed.")

    def organization_finished(self):
        state.busy = False
        state.add_log("Organization Task Completed.")


adapter = WebAppAdapter()


def start_download(url, use_ai):
    output_folder = state.output_folder
    downloader.run(url, output_folder, use_ai, adapter)


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_PATH.read_text(encoding="utf-8")


@app.post("/api/message")
def message(payload: MessageIn):
    text = payload.text.strip()
    if not text:
        return JSONResponse({"ok": True})

    state.add_log(f"[You] {text}")
    normalized = text.lower().strip()

    if state.awaiting_storage:
        if "gen" in normalized:
            state.storage_mode = "genre"
        elif "set" in normalized or "momento" in normalized:
            state.storage_mode = "set"
        else:
            adapter.ai_message("Escolha uma opção: gênero ou momentos do SET.")
            return JSONResponse({"ok": True})

        assistant.add_event("user", f"Storage mode: {state.storage_mode}")
        state.storage_event.set()
        return JSONResponse({"ok": True})

    if normalized in ("ai on", "ai ligado", "ai ativado"):
        if Config.OPENAI_API_KEY:
            state.add_log("[AI] Smart Search ligado.")
        else:
            state.add_log("[AI] Sem API key configurada.")
        return JSONResponse({"ok": True})

    if normalized in ("ai off", "ai desligado", "ai desativado"):
        state.add_log("[AI] Smart Search desligado.")
        return JSONResponse({"ok": True})

    if "open.spotify.com" in text:
        if not (Config.SPOTIFY_CLIENT_ID and Config.SPOTIFY_CLIENT_SECRET):
            state.add_log(
                "[Error] Configure SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no .env."
            )
            return JSONResponse({"ok": True})

        if state.busy:
            state.add_log("[AI] Já existe um processo em andamento.")
            return JSONResponse({"ok": True})

        assistant.user_message(f"Playlist URL: {text}")

        if not state.output_folder:
            default_folder = os.path.expanduser("~/Music/spot-downloader")
            os.makedirs(default_folder, exist_ok=True)
            state.output_folder = default_folder
            state.add_log(f"[AI] Pasta de saída definida: {state.output_folder}")

        state.busy = True
        use_ai = bool(Config.OPENAI_API_KEY)
        thread = threading.Thread(target=start_download, args=(text, use_ai), daemon=True)
        thread.start()
        return JSONResponse({"ok": True})

    if os.path.isdir(text):
        state.output_folder = text
        assistant.add_event("user", f"Output folder: {state.output_folder}")
        state.add_log(f"[AI] Pasta de saída definida: {state.output_folder}")
        return JSONResponse({"ok": True})

    if assistant:
        reply = assistant.respond(text)
        adapter.ai_message(reply)

    return JSONResponse({"ok": True})


@app.get("/api/poll")
def poll(since: int = 0):
    return JSONResponse(state.snapshot(since=since))
