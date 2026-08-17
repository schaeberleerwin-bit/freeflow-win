"""
Einfaches Status-Fenster fuer freeflow-win: zeigt Aufnahme-Status,
Verlauf der Transkriptionen und erlaubt das Aendern der Einstellungen.
"""

import datetime
import tkinter as tk
from tkinter import ttk

import config

IDLE_COLOR = "#3c3c3c"
RECORDING_COLOR = "#dc3232"


class FreeflowGUI:
    def __init__(self, on_save_settings):
        self.on_save_settings = on_save_settings
        self.root = tk.Tk()
        self.root.title("freeflow-win")
        self.root.geometry("420x480")
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.root.configure(bg="#1e1e1e")

        self._build_status_row()
        self._build_history()
        self._build_settings()

        self.hide()  # startet minimiert im Tray, Fenster nur bei Bedarf

    # ---------- UI Aufbau ----------

    def _build_status_row(self):
        frame = tk.Frame(self.root, bg="#1e1e1e", pady=12)
        frame.pack(fill="x", padx=16)

        self.dot = tk.Canvas(frame, width=18, height=18, bg="#1e1e1e", highlightthickness=0)
        self.dot_id = self.dot.create_oval(2, 2, 16, 16, fill=IDLE_COLOR, outline="")
        self.dot.pack(side="left")

        self.status_label = tk.Label(
            frame, text=f"Bereit — Taste '{config.HOTKEY}' halten zum Diktieren",
            bg="#1e1e1e", fg="#e0e0e0", font=("Segoe UI", 10), padx=10,
        )
        self.status_label.pack(side="left")

    def _build_history(self):
        tk.Label(self.root, text="Verlauf", bg="#1e1e1e", fg="#999999",
                  font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", padx=16)

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.history = tk.Text(
            frame, wrap="word", height=12, bg="#2a2a2a", fg="#e0e0e0",
            insertbackground="#e0e0e0", relief="flat", padx=8, pady=8,
            yscrollcommand=scrollbar.set, font=("Segoe UI", 10),
        )
        self.history.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history.yview)
        self.history.config(state="disabled")

    def _build_settings(self):
        frame = tk.LabelFrame(
            self.root, text="Einstellungen", bg="#1e1e1e", fg="#999999",
            font=("Segoe UI", 9, "bold"), padx=12, pady=10,
        )
        frame.pack(fill="x", padx=16, pady=(0, 16))

        self.hotkey_var = tk.StringVar(value=config.HOTKEY)
        self.language_var = tk.StringVar(value=config.LANGUAGE or "")
        self.model_var = tk.StringVar(value=config.MODEL)

        self._settings_row(frame, "Hotkey (halten)", self.hotkey_var, 0)
        self._settings_row(frame, "Sprache (z.B. de, en, leer=auto)", self.language_var, 1)
        self._settings_row(frame, "Modell", self.model_var, 2)

        save_btn = tk.Button(
            frame, text="Speichern (Neustart noetig)", command=self._save,
            bg="#3c3c3c", fg="#e0e0e0", relief="flat", padx=10, pady=4,
        )
        save_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        self.save_note = tk.Label(frame, text="", bg="#1e1e1e", fg="#4caf50", font=("Segoe UI", 9))
        self.save_note.grid(row=4, column=0, columnspan=2)

    def _settings_row(self, parent, label, var, row):
        tk.Label(parent, text=label, bg="#1e1e1e", fg="#cccccc", font=("Segoe UI", 9)).grid(
            row=row, column=0, sticky="w", pady=4
        )
        entry = tk.Entry(parent, textvariable=var, bg="#2a2a2a", fg="#e0e0e0",
                          insertbackground="#e0e0e0", relief="flat", width=22)
        entry.grid(row=row, column=1, sticky="e", pady=4)

    def _save(self):
        self.on_save_settings(
            hotkey=self.hotkey_var.get().strip(),
            language=self.language_var.get().strip(),
            model=self.model_var.get().strip(),
        )
        self.save_note.config(text="Gespeichert. Bitte App neu starten.")

    # ---------- Thread-sichere Updates ----------

    def set_recording(self, active):
        self.root.after(0, self._set_recording_ui, active)

    def _set_recording_ui(self, active):
        self.dot.itemconfig(self.dot_id, fill=RECORDING_COLOR if active else IDLE_COLOR)
        self.status_label.config(
            text="Nehme auf..." if active
            else f"Bereit — Taste '{config.HOTKEY}' halten zum Diktieren"
        )

    def add_transcript(self, text):
        self.root.after(0, self._add_transcript_ui, text)

    def _add_transcript_ui(self, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history.config(state="normal")
        self.history.insert("1.0", f"[{timestamp}] {text}\n\n")
        self.history.config(state="disabled")

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self):
        self.root.withdraw()

    def mainloop(self):
        self.root.mainloop()
