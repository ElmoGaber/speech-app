from transformers import pipeline
from utils import setup_logger, timestamped_filename
logger = setup_logger()

def build_whisper_pipe(model_name="openai/whisper-small"):
    pipe = pipeline("automatic-speech-recognition", model=model_name)
    return pipe

def transcribe_file(pipe, audio_path):
    logger.info(f"Transcribing {audio_path}")
    res = pipe(audio_path)
    text = res.get("text", "")
    out_fn = timestamped_filename("transcript","json")
    import json
    with open(f"outputs/transcripts/{out_fn}", "w", encoding="utf-8") as f:
        json.dump({"audio": audio_path, "text": text}, f, ensure_ascii=False, indent=2)
    logger.info(f"Transcript saved: outputs/transcripts/{out_fn}")
    return text
