import pickle
from langchain_community.retrievers import BM25Retriever
from src.config.config import BM25_INDEX_PATH, SPARSE_TOP_K


def load_sparse_retriever():
    with open(BM25_INDEX_PATH, "rb") as f:
        retriever: BM25Retriever = pickle.load(f)

    retriever.k = SPARSE_TOP_K

    return retriever