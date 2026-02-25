# postproc.py
import torchaudio
import torch

def apply_equalizer(audio_tensor, sample_rate, eq_model="saudi"):
    """
    Apply simple EQ (equalization) effect based on model type.
    """
    if eq_model == "saudi":
        # نرفع الباس شوية ونقلل التربل
        bass_boost = torchaudio.functional.equalizer_biquad(audio_tensor, sample_rate, center_freq=150, gain=5.0, Q=0.707)
        treble_cut = torchaudio.functional.equalizer_biquad(bass_boost, sample_rate, center_freq=6000, gain=-3.0, Q=0.707)
        return treble_cut
    elif eq_model == "arabic_english":
        # نرفع الميد رينج لتحسين الوضوح
        mid_boost = torchaudio.functional.equalizer_biquad(audio_tensor, sample_rate, center_freq=1500, gain=4.0, Q=1.0)
        return mid_boost
    else:
        return audio_tensor

def normalize_audio(audio_tensor):
    """
    Normalize audio to -1 to 1 range.
    """
    return audio_tensor / torch.max(torch.abs(audio_tensor))
