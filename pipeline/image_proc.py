from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer
from utils import save_b64_file, timestamped_filename, setup_logger
logger = setup_logger()

clip_model = SentenceTransformer('clip-ViT-B-32')  # or other image encoder

def process_image_b64(b64str, dest_dir="outputs"):
    fn = timestamped_filename("img","png")
    path = f"{dest_dir}/{fn}"
    save_b64_file(b64str, path)
    return path

def ocr_image(img_path):
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang='eng+ara')  # Arabic + English
    logger.info(f"OCR extracted {len(text)} chars from {img_path}")
    return text

def image_embedding(img_path):
    emb = clip_model.encode(img_path)
    return emb
