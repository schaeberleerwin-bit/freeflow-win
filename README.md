# freeflow-win

Kleine eigene Hold-to-Talk-Diktier-App fuer Windows 11 (Python, eigenstaendige Implementierung, orientiert an der Idee "Taste halten, sprechen, Text erscheint"). Transkription laeuft komplett lokal ueber [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CPU) – keine Cloud-API, kein API-Key, keine Audiodaten verlassen den Rechner.

## Setup

1. Python 3.10+ installieren.
2. Virtuelle Umgebung anlegen und Abhaengigkeiten installieren:
   ```
   python -m venv venv
   venv\Scripts\pip install -r requirements.txt
   ```
3. `.env.example` zu `.env` kopieren (Defaults passen meist ohne Anpassung):
   ```
   copy .env.example .env
   ```
4. Starten:
   ```
   venv\Scripts\python main.py
   ```
   Beim allerersten Start wird das Whisper-Modell einmalig heruntergeladen (~500MB bei `small`) und lokal gecacht (`%USERPROFILE%\.cache\huggingface`). Danach laeuft alles offline.

## Nutzung

Rechte STRG-Taste gedrueckt halten, sprechen, loslassen. Der transkribierte Text wird an der aktuellen Cursor-Position eingefuegt. Tray-Icon (unten rechts) zum Beenden nutzen.

## Konfiguration (.env)

- `FREEFLOW_HOTKEY` – welche Taste gehalten werden muss (Standard: `right ctrl`)
- `FREEFLOW_LANGUAGE` – Sprachcode fuer Transkription, z.B. `de`, `en` (leer lassen fuer Auto-Erkennung)
- `FREEFLOW_MODEL` – lokales Whisper-Modell: `tiny`/`base`/`small`/`medium`/`large-v3` (Standard: `small`; groesser = genauer, aber langsamer auf CPU)
- `FREEFLOW_DEVICE` – `cpu` (Standard; keine NVIDIA/CUDA-GPU auf diesem Rechner) oder `cuda` falls vorhanden
- `FREEFLOW_COMPUTE_TYPE` – Quantisierung, `int8` (Standard, schnell auf CPU) oder `float16`/`float32`

## Bekannte Einschraenkungen

- Erster Start braucht Internet zum einmaligen Modell-Download, danach voll offline.
- Laeuft auf CPU (int8-Quantisierung) – bei `small` liegt die Transkription eines kurzen Diktats meist bei 1-3 Sekunden, bei `medium`/`large-v3` entsprechend langsamer.
- `keyboard`-Bibliothek benoetigt unter Windows ggf. Admin-Rechte fuer globale Hotkeys.
- Kein Autostart/Installer – einfach `venv\Scripts\python main.py` bei Bedarf starten.
