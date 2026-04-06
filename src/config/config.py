import os
from pathlib import Path
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BASE_DIR = Path(__file__).resolve().parent.parent.parent



DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw"
CHROMA_DB_PATH = DATA_DIR / "chroma_db"
LAWS_PATH = DATA_DIR / "processed" / "all_laws_with_id.json"
BM25_INDEX_PATH = DATA_DIR / "BM25" / "bm25_retriever.pkl"


EMBEDDING_MODEL_NAME = "huyydangg/DEk21_hcmute_embedding"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"


LLM_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct-AWQ"
LLM_BASE_URL = "https://michal-sphenographic-pregnantly.ngrok-free.dev/v1"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS  = 2048

DENSE_TOP_K  = 100   # ChromaDB
SPARSE_TOP_K = 100   # BM25
RRF_K = 60  
RRF_WEIGHTS = [0.4, 0.6] # [BM25, Chromna]


HYBRID_TOP_K = 100
RERANK_TOP_N = 10 

MAX_HISTORY_TURNS = 10    
MAX_TOKEN_LIMIT   = 3000