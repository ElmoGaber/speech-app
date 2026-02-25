import torch
from utils import setup_logger
logger = setup_logger()

# Load Silero VAD once
def load_vad_model(device='cpu'):
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=False)
    (get_speech_ts, save_audio, read_audio, VADIterator, collect_chunks) = utils
    return model, get_speech_ts, read_audio

# returns list of dicts: [{"start": ..., "end": ...}, ...] in samples
def detect_speech_segments(wav_path, model, get_speech_ts, sampling_rate=16000):
    audio = get_audio_array(wav_path, sampling_rate)  # implement reading normalized array
    timestamps = get_speech_ts(audio, model, sampling_rate=sampling_rate)
    logger.info(f"VAD found {len(timestamps)} segments in {wav_path}")
    return timestamps
