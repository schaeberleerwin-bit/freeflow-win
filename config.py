import os
from dotenv import load_dotenv

load_dotenv()

HOTKEY = os.getenv("FREEFLOW_HOTKEY", "right ctrl")  # gehalten = aufnehmen
LANGUAGE = os.getenv("FREEFLOW_LANGUAGE", "de")  # None fuer Auto-Erkennung
# Lokales faster-whisper Modell: tiny/base/small/medium/large-v3 (Groesse = Geschwindigkeit vs. Genauigkeit)
MODEL = os.getenv("FREEFLOW_MODEL", "small")
DEVICE = os.getenv("FREEFLOW_DEVICE", "cpu")  # keine NVIDIA/CUDA-GPU vorhanden -> cpu
COMPUTE_TYPE = os.getenv("FREEFLOW_COMPUTE_TYPE", "int8")  # int8 = schnell genug auf CPU
