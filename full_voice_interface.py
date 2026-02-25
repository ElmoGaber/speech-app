# interfaces/full_voice_interface.py
import gradio as gr
from main import process_audio_input

def chat_with_voice(audio_input, model_choice):
    final_audio = process_audio_input(audio_input, eq_model=model_choice)
    return final_audio

iface = gr.Interface(
    fn=chat_with_voice,
    inputs=[
        gr.Audio(source="microphone", type="filepath", label="🎤 Speak here"),
        gr.Radio(["saudi", "arabic_english"], label="Equalizer Mode")
    ],
    outputs=gr.Audio(type="filepath", label="🔊 AI Response"),
    title="🎙️ Offline Voice Chat System",
    description="STT → LLM → TTS → Equalizer pipeline (offline)"
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7865)
