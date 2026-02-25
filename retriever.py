import faiss, numpy as np
from sentence_transformers import SentenceTransformer
from utils import setup_logger
logger = setup_logger()
embed_model = SentenceTransformer("all-MiniLM-L6-v2")  # for text/image captions

# build index (offline) from KB docs: texts list and ids
def build_faiss_index(texts):
    vectors = embed_model.encode(texts, convert_to_numpy=True)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index, vectors

def retrieve(index, query_text, topk=5):
    qv = embed_model.encode([query_text], convert_to_numpy=True)
    D, I = index.search(qv, topk)
    logger.info(f"Retriever found {I.shape[1]} candidates")
    return I[0].tolist(), D[0].tolist()
