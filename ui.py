import customtkinter as ctk
import threading
import os
import re
from config import Config


class App(ctk.CTk):
    def __init__(self, start_download_callback, organize_callback, assistant=None):
        super().__init__()
        self.start_download_callback = start_download_callback
        self.organize_callback = organize_callback
        self.assistant = assistant
        self.storage_mode_var = ""
        self.storage_mode_event = threading.Event()
        self.awaiting_storage_choice = False
        self.use_ai = bool(Config.OPENAI_API_KEY)
        self.playlist_url = ""
        self.output_folder = ""
        self.busy = False

        # Window Setup
        self.title(Config.APP_NAME)
        self.geometry(Config.APP_SIZE)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme(Config.THEME_COLOR)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)  # Chat log expands

        self.setup_ui()
        if self.assistant:
            self.ai_message(self.assistant.initial_message())

    def setup_ui(self):
        # Header
        self.label_header = ctk.CTkLabel(self, text="Spotify to MP3 Downloader", font=("Roboto", 24))
        self.label_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Chat Log
        self.textbox_log = ctk.CTkTextbox(self, width=700, font=("Consolas", 12))
        self.textbox_log.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew", rowspan=4)
        self.log("Ready to chat.")

        # Chat Input
        self.frame_chat = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_chat.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.frame_chat.grid_columnconfigure(0, weight=1)

        self.entry_chat = ctk.CTkEntry(self.frame_chat, placeholder_text="Fale com a assistente...", width=500)
        self.entry_chat.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_send = ctk.CTkButton(self.frame_chat, text="Enviar", command=self.on_send_chat, width=120)
        self.btn_send.grid(row=0, column=1)

        self.entry_chat.bind("<Return>", lambda _e: self.on_send_chat())

        # Right panel: Playlist info
        self.frame_playlist = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_playlist.grid(row=0, column=1, padx=(0, 20), pady=(20, 20), sticky="nsew", rowspan=7)
        self.frame_playlist.grid_rowconfigure(1, weight=1)

        self.label_playlist = ctk.CTkLabel(self.frame_playlist, text="Playlist", font=("Roboto", 18))
        self.label_playlist.grid(row=0, column=0, sticky="w", padx=10, pady=(0, 10))

        self.label_count = ctk.CTkLabel(self.frame_playlist, text="0 músicas")
        self.label_count.grid(row=0, column=1, sticky="e", padx=10, pady=(0, 10))

        self.textbox_playlist = ctk.CTkTextbox(self.frame_playlist, width=320, font=("Consolas", 12))
        self.textbox_playlist.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        self.textbox_playlist.insert("end", "Aguardando playlist...\n")
        self.textbox_playlist.configure(state="disabled")

    def log(self, message):
        self.textbox_log.insert("end", f"{message}\n")
        self.textbox_log.see("end")

    def ai_message(self, message):
        self.log(f"[AI] {message}")

    def on_organize(self):
        folder = self.output_folder
        use_ai = self.use_ai

        if not folder:
            self.log("[Error] Please select a folder to organize.")
            return

        self.busy = True
        thread = threading.Thread(target=self.organize_callback, args=(folder, use_ai, self))
        thread.start()

    def request_storage_mode(self, total_songs=None):
        self.storage_mode_event.clear()
        self.storage_mode_var = ""
        self.awaiting_storage_choice = True

        def _prompt():
            if self.assistant:
                self.ai_message(self.assistant.ask_storage_mode(total_songs))
            else:
                if total_songs is None:
                    self.ai_message("Como você quer armazenar as músicas? (gênero ou set)")
                else:
                    self.ai_message(
                        f"Encontrei {total_songs} músicas. "
                        "Como você quer armazenar as músicas? (gênero ou set)"
                    )

        self.after(0, _prompt)
        self.storage_mode_event.wait()
        return self.storage_mode_var or "genre"

    def show_playlist(self, songs):
        def _update():
            self.textbox_playlist.configure(state="normal")
            self.textbox_playlist.delete("1.0", "end")
            for i, song in enumerate(songs, 1):
                self.textbox_playlist.insert("end", f"{i}. {song.artist} - {song.name}\n")
            self.textbox_playlist.configure(state="disabled")
            self.label_count.configure(text=f"{len(songs)} músicas")
        self.after(0, _update)

    def _handle_storage_choice(self, text):
        normalized = text.lower()
        if "gen" in normalized:
            self.storage_mode_var = "genre"
        elif "set" in normalized or "momento" in normalized:
            self.storage_mode_var = "set"
        else:
            self.ai_message("Escolha uma opção: gênero ou momentos do SET.")
            return False

        if self.assistant:
            choice = "gênero" if self.storage_mode_var == "genre" else "momentos do SET"
            self.assistant.add_event("user", f"Storage mode: {choice}")
        self.awaiting_storage_choice = False
        self.storage_mode_event.set()
        return True

    def on_send_chat(self):
        text = self.entry_chat.get().strip()
        if not text:
            return
        self.entry_chat.delete(0, "end")
        self.log(f"[You] {text}")

        if self.awaiting_storage_choice:
            if self._handle_storage_choice(text):
                return

        normalized = text.lower().strip()

        if normalized in ("ai on", "ai ligado", "ai ativado"):
            if Config.OPENAI_API_KEY:
                self.use_ai = True
                self.log("[AI] Smart Search ligado.")
            else:
                self.log("[AI] Sem API key configurada.")
            return

        if normalized in ("ai off", "ai desligado", "ai desativado"):
            self.use_ai = False
            self.log("[AI] Smart Search desligado.")
            return

        if "open.spotify.com" in text:
            self.playlist_url = text.strip()
            if self.assistant:
                self.assistant.user_message(f"Playlist URL: {self.playlist_url}")

            if not self.output_folder:
                default_folder = os.path.expanduser("~/Music/spot-downloader")
                os.makedirs(default_folder, exist_ok=True)
                self.output_folder = default_folder
                self.log(f"[AI] Pasta de saída definida: {self.output_folder}")

            if self.busy:
                self.log("[AI] Já existe um processo em andamento.")
                return

            self.busy = True
            thread = threading.Thread(
                target=self.start_download_callback,
                args=(self.playlist_url, self.output_folder, self.use_ai, self),
            )
            thread.start()
            return

        path_match = re.match(r"^([A-Za-z]:\\|/).+", text)
        if path_match and os.path.isdir(text):
            self.output_folder = text
            if self.assistant:
                self.assistant.add_event("user", f"Output folder: {self.output_folder}")
            self.log(f"[AI] Pasta de saída definida: {self.output_folder}")
            return

        if self.assistant:
            reply = self.assistant.respond(text)
            self.ai_message(reply)
        else:
            self.log("[AI] Assistente indisponível.")

    def download_finished(self):
        self.busy = False
        self.log("Task Completed.")

    def organization_finished(self):
        self.busy = False
        self.log("Organization Task Completed.")
