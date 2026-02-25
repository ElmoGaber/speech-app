from transformers import AutoTokenizer, AutoModelForCausalLM
from utils import setup_logger
logger = setup_logger()

def load_llm(model_id="qwen/qwen-3-4b"):  # مثال
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
    return tokenizer, model

def generate_reply(tokenizer, model, prompt, max_new_tokens=150):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens)
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    logger.info("LLM generated reply")
    return text
