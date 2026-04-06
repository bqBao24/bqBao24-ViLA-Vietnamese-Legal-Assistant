from typing import List
from langchain_core.documents import Document
from src.config.config import RRF_K, RRF_WEIGHTS

def reciprocal_rank_fusion(retriever_results: List[List[Document]]) -> List[Document]:
    fused_scores = {}
    for weight, docs in zip(RRF_WEIGHTS, retriever_results):
        for rank, doc in enumerate(docs):
            doc_key = doc.metadata.get("chunk_id", str(hash(doc.page_content)))
            
            if doc_key not in fused_scores:
                fused_scores[doc_key] = {"score": 0.0, "doc": doc}
            fused_scores[doc_key]["score"] += weight / (RRF_K + rank + 1)

    reranked_results = sorted(
        fused_scores.values(), 
        key=lambda x: x["score"], 
        reverse=True
    )

    return [item["doc"] for item in reranked_results]