import json, base64, asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils import setup_logger, ensure_dirs, save_b64_file
from pipeline.stt import build_whisper_pipe, transcribe_file
from pipeline.image_proc import process_image_b64, ocr_image, image_embedding
from pipeline.retriever import retrieve  # assume pre-built index loaded
from pipeline.llm_agent import load_llm, generate_reply
from pipeline.tts import synthesize_to_file

logger = setup_logger()
ensure_dirs()

app = FastAPI()
whisper_pipe = build_whisper_pipe()
tokenizer, llm_model = load_llm("mistralai/Mistral-7B-Instruct-v0.2")  # استخدم موديلك

# Example: simplified in-order handler (synchronous per message)
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    session = None
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type")

            if msg_type == "upload":
                session = msg.get("session_id")
                img_info = msg.get("image")
                aud_info = msg.get("audio")
                # save image & audio
                img_path = process_image_b64(img_info["b64"], dest_dir="outputs")
                audio_path = save_b64_file(aud_info["b64"], f"outputs/{aud_info['filename']}")
                await ws.send_text(json.dumps({"status":"saved", "image":img_path, "audio":audio_path}))

                # OCR + img emb
                ocr_text = ocr_image(img_path)
                img_emb = image_embedding(img_path)

                # STT
                stt_text = transcribe_file(whisper_pipe, audio_path)

                # Combine for retrieval prompt
                combined_query = f"Customer said: {stt_text}\nImage OCR: {ocr_text}"
                # retriever returns ids -> you need to load texts by ids
                # For demo, assume kb_texts built and index loaded
                ids, dists = retrieve(index, combined_query, topk=5)

                # Construct prompt for LLM
                context = "\n".join([KB_TEXTS[i] for i in ids])  # KB_TEXTS preloaded
                prompt = f"You are a customer service assistant. Use context:\n{context}\n\nUser: {stt_text}\nRespond concisely."
                reply = generate_reply(tokenizer, llm_model, prompt)

                # TTS
                out_audio = synthesize_to_file(reply, language=msg.get("metadata",{}).get("language","ar"))
                # Send back audio path or b64
                with open(out_audio,"rb") as f:
                    b64_audio = base64.b64encode(f.read()).decode("utf-8")
                await ws.send_text(json.dumps({"type":"response_audio", "b64": b64_audio, "text": reply}))
            else:
                await ws.send_text(json.dumps({"error":"unknown_type"}))

    except WebSocketDisconnect:
        logger.info("Client disconnected")
