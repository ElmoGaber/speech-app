import os
import logging
from datetime import datetime
import base64

def setup_logger(name="voice_rag"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    os.makedirs("outputs/logs", exist_ok=True)
    fh = logging.FileHandler(f"outputs/logs/{name}.log", encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger

def ensure_dirs():
    os.makedirs("outputs/audio", exist_ok=True)
    os.makedirs("outputs/transcripts", exist_ok=True)
    os.makedirs("models", exist_ok=True)

def save_b64_file(b64str: str, dest_path: str):
    data = base64.b64decode(b64str)
    with open(dest_path, "wb") as f:
        f.write(data)
    return dest_path

def timestamped_filename(prefix, ext):
    t = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")[:-3]
    return f"{prefix}_{t}.{ext}"
