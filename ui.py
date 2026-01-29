import customtkinter as ctk
from tkinter import filedialog
import threading
from config import Config

class App(ctk.CTk):
    def __init__(self, start_download_callback, organize_callback, assistant=None):
        super().__init__()
        self.start_download_callback = start_download_callback
        self.organize_callback = organize_callback
        self.assistant = assistant
        self.storage_mode_var = ctk.StringVar(value="")
        self.storage_mode_event = threading.Event()

        # Window Setup
        self.title(Config.APP_NAME)
        self.geometry(Config.APP_SIZE)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme(Config.THEME_COLOR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)  # Log area expands

        self.setup_ui()
        if self.assistant:
            self.ai_message(self.assistant.initial_message())

    def setup_ui(self):
        # Header
        self.label_header = ctk.CTkLabel(self, text="Spotify to MP3 Downloader", font=("Roboto", 24))
        self.label_header.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Playlist URL Input
        self.entry_url = ctk.CTkEntry(self, placeholder_text="Paste Spotify Playlist URL here...", width=500)
        self.entry_url.grid(row=1, column=0, padx=20, pady=10)

        # Output Folder Selection
        self.frame_folder = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_folder.grid(row=2, column=0, padx=20, pady=5)
        
        self.entry_folder = ctk.CTkEntry(self.frame_folder, placeholder_text="Select Output Folder...", width=350)
        self.entry_folder.pack(side="left", padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.frame_folder, text="Browse", command=self.browse_folder, width=140)
        self.btn_browse.pack(side="left")

        # Options
        self.check_ai = ctk.CTkCheckBox(self, text="Enable Smart Search (Prefers Extended/Club Mixes & Audio Only)")
        if not Config.OPENAI_API_KEY:
            self.check_ai.configure(state="disabled", text="AI Smart Search (Requires API Key in .env)")
        else:
            self.check_ai.select() # Default on if key exists
        self.check_ai.grid(row=3, column=0, padx=20, pady=10)

        # Action Button
        self.btn_start = ctk.CTkButton(self, text="Start Download", command=self.on_start, height=50, font=("Roboto", 16, "bold"))
        self.btn_start.grid(row=4, column=0, padx=20, pady=20)

        # Organize Button
        self.btn_organize = ctk.CTkButton(self, text="Organize Existing Files", command=self.on_organize, fg_color="gray", width=200)
        self.btn_organize.grid(row=6, column=0, padx=20, pady=(0, 20))

        # Log Console
        self.textbox_log = ctk.CTkTextbox(self, width=700, font=("Consolas", 12))
        self.textbox_log.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log("Ready to download.")

        # Chat Input
        self.frame_chat = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_chat.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.frame_chat.grid_columnconfigure(0, weight=1)

        self.entry_chat = ctk.CTkEntry(self.frame_chat, placeholder_text="Fale com a assistente...", width=500)
        self.entry_chat.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_send = ctk.CTkButton(self.frame_chat, text="Enviar", command=self.on_send_chat, width=120)
        self.btn_send.grid(row=0, column=1)

        self.entry_chat.bind("<Return>", lambda _e: self.on_send_chat())

        # Storage Mode
        self.frame_storage = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_storage.grid(row=5, column=0, padx=20, pady=(0, 10))

        self.label_storage = ctk.CTkLabel(self.frame_storage, text="Armazenamento das músicas:")
        self.label_storage.pack(side="left", padx=(0, 10))

        self.radio_genre = ctk.CTkRadioButton(
            self.frame_storage, text="Por gênero", value="genre", variable=self.storage_mode_var
        )
        self.radio_genre.pack(side="left", padx=(0, 10))

        self.radio_set = ctk.CTkRadioButton(
            self.frame_storage, text="Por momentos do SET", value="set", variable=self.storage_mode_var
        )
        self.radio_set.pack(side="left", padx=(0, 10))

        self.btn_confirm_storage = ctk.CTkButton(
            self.frame_storage, text="Confirmar", command=self.on_confirm_storage, width=120
        )
        self.btn_confirm_storage.pack(side="left")

        self._set_storage_controls_state("disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, folder)

    def log(self, message):
        self.textbox_log.insert("end", f"{message}\n")
        self.textbox_log.see("end")

    def ai_message(self, message):
        self.log(f"[AI] {message}")

    def _set_storage_controls_state(self, state):
        self.radio_genre.configure(state=state)
        self.radio_set.configure(state=state)
        self.btn_confirm_storage.configure(state=state)

    def on_start(self):
        url = self.entry_url.get().strip()
        folder = self.entry_folder.get().strip()
        use_ai = self.check_ai.get() == 1

        if not url:
            self.log("[Error] Please enter a Spotify URL.")
            return
        if not folder:
            self.log("[Error] Please select an output folder.")
            return

        if self.assistant:
            self.assistant.user_message(f"Playlist URL: {url}")
            self.assistant.add_event("user", f"Output folder: {folder}")
            self.assistant.add_event("user", f"Smart Search: {'on' if use_ai else 'off'}")

        self.btn_start.configure(state="disabled", text="Downloading...")
        
        # Start download in a separate thread
        thread = threading.Thread(target=self.start_download_callback, args=(url, folder, use_ai, self))
        thread.start()

    def on_organize(self):
        folder = self.entry_folder.get().strip()
        use_ai = self.check_ai.get() == 1
        
        if not folder:
            self.log("[Error] Please select a folder to organize.")
            return
            
        self.btn_organize.configure(state="disabled", text="Organizing...")
        self.btn_start.configure(state="disabled")
        
        thread = threading.Thread(target=self.organize_callback, args=(folder, use_ai, self))
        thread.start()

    def on_confirm_storage(self):
        if not self.storage_mode_var.get():
            self.log("[Error] Selecione uma forma de armazenamento.")
            return
        self._set_storage_controls_state("disabled")
        if self.assistant:
            choice = "gênero" if self.storage_mode_var.get() == "genre" else "momentos do SET"
            self.assistant.add_event("user", f"Storage mode: {choice}")
        self.storage_mode_event.set()

    def request_storage_mode(self, total_songs=None):
        self.storage_mode_event.clear()
        self.storage_mode_var.set("")

        def _prompt():
            if self.assistant:
                self.ai_message(self.assistant.ask_storage_mode(total_songs))
            else:
                if total_songs is None:
                    self.ai_message("Como você quer armazenar as músicas?")
                else:
                    self.ai_message(
                        f"Encontrei {total_songs} músicas. "
                        "Como você quer armazenar as músicas?"
                    )
            self._set_storage_controls_state("normal")

        self.after(0, _prompt)
        self.storage_mode_event.wait()
        return self.storage_mode_var.get() or "genre"

    def on_send_chat(self):
        text = self.entry_chat.get().strip()
        if not text:
            return
        self.entry_chat.delete(0, "end")
        self.log(f"[You] {text}")
        if self.assistant:
            reply = self.assistant.respond(text)
            self.ai_message(reply)
        else:
            self.log("[AI] Assistente indisponível.")

    def download_finished(self):
        self.btn_start.configure(state="normal", text="Start Download")
        self.btn_organize.configure(state="normal", text="Organize Existing Files")
        self.log("Task Completed.")

    def organization_finished(self):
        self.btn_start.configure(state="normal")
        self.btn_organize.configure(state="normal", text="Organize Existing Files")
        self.log("Organization Task Completed.")
