"""
freeflow-win: einfache Hold-to-Talk Diktier-App fuer Windows.
Rechte STRG halten -> spricht -> Taste loslassen -> Text wird transkribiert
und an der aktuellen Cursor-Position eingefuegt (per Zwischenablage + Strg+V).
Transkription laeuft komplett lokal ueber faster-whisper (keine Cloud-API,
keine Audiodaten verlassen den Rechner).
"""

import sys
import threading
import time

import keyboard
import pyperclip
import sounddevice as sd
from faster_whisper import WhisperModel
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

import config

SAMPLE_RATE = 16000
CHANNELS = 1

model = None
recording = False
audio_frames = []
stream = None
icon = None


def get_model():
    global model
    if model is None:
        print(f"Lade Whisper-Modell '{config.MODEL}' ({config.DEVICE}/{config.COMPUTE_TYPE}) ...")
        model = WhisperModel(config.MODEL, device=config.DEVICE, compute_type=config.COMPUTE_TYPE)
        print("Modell geladen.")
    return model


def audio_callback(indata, frames, time_info, status):
    audio_frames.append(indata.copy())


def start_recording():
    global recording, audio_frames, stream
    if recording:
        return
    recording = True
    audio_frames = []
    set_icon_state(True)
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback
    )
    stream.start()


def stop_recording_and_transcribe():
    global recording, stream
    if not recording:
        return
    recording = False
    set_icon_state(False)
    stream.stop()
    stream.close()

    if not audio_frames:
        return

    import numpy as np

    audio = np.concatenate(audio_frames, axis=0)
    duration = len(audio) / SAMPLE_RATE
    if duration < 0.3:
        return  # zu kurz, wahrscheinlich versehentlicher Tastendruck

    threading.Thread(target=transcribe_and_insert, args=(audio,), daemon=True).start()


def transcribe_and_insert(audio):
    try:
        m = get_model()
        # faster-whisper erwartet mono float32 @ SAMPLE_RATE; sounddevice liefert das bereits.
        segments, _info = m.transcribe(
            audio.flatten(),
            language=config.LANGUAGE or None,
        )
        text = "".join(segment.text for segment in segments).strip()
        if text:
            insert_text(text)
    except Exception as e:
        print(f"Transkriptionsfehler: {e}")


def insert_text(text):
    previous = None
    try:
        previous = pyperclip.paste()
    except Exception:
        pass
    pyperclip.copy(text)
    keyboard.send("ctrl+v")
    if previous is not None:
        time.sleep(0.2)
        pyperclip.copy(previous)


def set_icon_state(active):
    if icon is None:
        return
    icon.icon = make_image(active)


def make_image(active):
    color = (220, 50, 50) if active else (60, 60, 60)
    img = Image.new("RGB", (64, 64), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill=color)
    return img


def quit_app(icon_ref, item):
    icon_ref.stop()
    keyboard.unhook_all()
    sys.exit(0)


def run_hotkey_listener():
    keyboard.on_press_key(config.HOTKEY, lambda e: start_recording(), suppress=False)
    keyboard.on_release_key(
        config.HOTKEY, lambda e: stop_recording_and_transcribe(), suppress=False
    )
    keyboard.wait()


def main():
    global icon
    get_model()  # Modell frueh laden, damit die erste Aufnahme nicht wartet

    icon = Icon(
        "freeflow-win",
        make_image(False),
        f"freeflow-win ({config.HOTKEY} halten zum Diktieren)",
        menu=Menu(MenuItem("Beenden", quit_app)),
    )

    t = threading.Thread(target=run_hotkey_listener, daemon=True)
    t.start()

    print(f"freeflow-win laeuft. Halte '{config.HOTKEY}' zum Diktieren. Tray-Icon zum Beenden nutzen.")
    icon.run()


if __name__ == "__main__":
    main()
