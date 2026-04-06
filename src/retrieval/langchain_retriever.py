from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import BaseModel, ConfigDict
from src.retrieval.hybrid_search import HybridSearch

class LangChainHybridRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    hybrid_search: HybridSearch = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "hybrid_search", HybridSearch())

    def _get_relevant_documents(self, query: str) -> List[Document]:
        return self.hybrid_search.get_relevant_documents(query)

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)