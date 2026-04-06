from sentence_transformers import CrossEncoder
from src.retrieval.dense_retriever import load_dense_retriever
from src.retrieval.sparse_retriever import load_sparse_retriever
from src.retrieval.rrf_fusion import reciprocal_rank_fusion
from src.config.config import RERANKER_MODEL_NAME, DEVICE, HYBRID_TOP_K, RERANK_TOP_N

class HybridSearch:
    def __init__(self):
        print("Đang nạp Dense Retriever...")
        self.dense_retriever = load_dense_retriever()
        print("Đang nạp Sparse Retriever...")
        self.sparse_retriever = load_sparse_retriever()
        
        print(f"Đang khởi tạo Reranker: {RERANKER_MODEL_NAME} trên {DEVICE}...")
        self.reranker = CrossEncoder(
            RERANKER_MODEL_NAME, 
            device=DEVICE,
            trust_remote_code=True
        )

    def get_relevant_documents(self, query: str):
        """
        Quy trình: Retriever (200) -> RRF Fusion -> Truncate  -> Rerank 
        """
        
        # Retrieval
        dense_docs = self.dense_retriever.invoke(query)
        sparse_docs = self.sparse_retriever.invoke(query)
        
        # rrf 
        fused_docs = reciprocal_rank_fusion([sparse_docs, dense_docs])
        candidate_docs = fused_docs[:HYBRID_TOP_K]
        
        # rerank
        sentence_pairs = [[query, doc.page_content] for doc in candidate_docs]
        scores = self.reranker.predict(sentence_pairs)
        for i, doc in enumerate(candidate_docs):
            doc.metadata["rerank_score"] = float(scores[i])
        final_ranked_docs = sorted(
            candidate_docs, 
            key=lambda x: x.metadata["rerank_score"], 
            reverse=True
        )
        
        # kq
        return final_ranked_docs[:RERANK_TOP_N]