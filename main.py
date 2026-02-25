# main.py
import os
import torch
import torchaudio
from TTS.api import TTS
from whisper import load_model as load_whisper
from llama_cpp import Llama
from postproc import apply_equalizer, normalize_audio

# ===============================
# 1️⃣ تحميل الموديلات
# ===============================
print("🔹 Loading models ...")

# STT (Whisper)
stt_model = load_whisper("small")

# TTS (XTTS multilingual)
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# LLM (Qwen3-4B Instruct)
llm = Llama(
    model_path="Qwen2.5-4B-Instruct.Q4_K_M.gguf",  # ضعه في مجلد models أو نزله من HF
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=20 if torch.cuda.is_available() else 0
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
os.makedirs("outputs/audio", exist_ok=True)

# ===============================
# 2️⃣ البروسيس الكامل
# ===============================
def process_audio_input(audio_path, eq_model="saudi"):
    """
    الصوت → STT → Qwen LLM → TTS → EQ
    """
    # STT
    result = stt_model.transcribe(audio_path)
    user_text = result["text"]
    print(f"🗣️ User said: {user_text}")

    # Qwen3-4B: الرد على النص
    system_prompt = (
        "أنت مساعد ذكي مخصص لخدمة العملاء. "
        "تتحدث بالعربية أو الإنجليزية حسب لغة المستخدم. "
        "كن ودودًا وواضحًا في الرد."
    )

    llm_response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        max_tokens=200,
        temperature=0.7
    )

    reply_text = llm_response["choices"][0]["message"]["content"]
    print(f"🤖 LLM reply: {reply_text}")

    # TTS
    output_path = f"outputs/audio/{eq_model}_reply.wav"
    tts_model.tts_to_file(text=reply_text, file_path=output_path, language="ar")

    # EQ + normalization
    waveform, sr = torchaudio.load(output_path)
    eq_wave = apply_equalizer(waveform, sr, eq_model)
    eq_wave = normalize_audio(eq_wave)

    final_path = f"outputs/audio/{eq_model}_reply_eq.wav"
    torchaudio.save(final_path, eq_wave, sr)

    print(f"✅ Final response saved: {final_path}")
    return final_path
