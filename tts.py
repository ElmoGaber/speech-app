from TTS.api import TTS
from utils import timestamped_filename, setup_logger
logger = setup_logger()
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")  # or local path

def synthesize_to_file(text, language="ar", speaker_wav=None):
    out_fn = timestamped_filename("reply","wav")
    out_path = f"outputs/audio/{out_fn}"
    tts.tts_to_file(text=text, file_path=out_path, language=language, speaker_wav=speaker_wav)
    logger.info(f"TTS saved: {out_path}")
    return out_path
