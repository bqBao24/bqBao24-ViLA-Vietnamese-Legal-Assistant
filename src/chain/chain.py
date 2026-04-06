from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from src.config.config import LLM_BASE_URL, LLM_MODEL_NAME, LLM_TEMPERATURE, LLM_MAX_TOKENS
from src.chain.prompts import GREETING_SYSTEM_PROMPT, LEGAL_SYSTEM_PROMPT
from src.chain.router import QueryRouter, RouteType
from src.chain.memory import ConversationMemory
from src.retrieval.langchain_retriever import LangChainHybridRetriever

class LegalChatBot:
    def __init__(self):
        self.router = QueryRouter()
        self.memory = ConversationMemory()
        self.retriever = LangChainHybridRetriever()
        self.llm = ChatOpenAI(
            model=LLM_MODEL_NAME,
            openai_api_base=LLM_BASE_URL,
            openai_api_key="not-needed",
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            streaming=True,
        )
    
    def chat(self, query: str) -> str:
        chat_history = self.memory.build_history()
        route = self.router.classify(query = query, chat_history = chat_history)
        if route == RouteType.GREETING:
            messages = [
                SystemMessage(content=GREETING_SYSTEM_PROMPT),
                *chat_history,
                HumanMessage(content=query),
            ]
            response = self.llm.invoke(messages).content
            self.memory.add_turn(human=query, ai=response)
            return response
        
        elif route == RouteType.LEGAL:
            docs = self.retriever.invoke(query)
            context_parts = []
            for doc in docs:
                meta = doc.metadata
                citation = f"{meta.get('Article', '')} {meta.get('ChuDe', '')} {meta.get('SoHieu', '')}"
                context_parts.append(f"{citation}\n{doc.page_content}")
            context = "\n\n".join(context_parts)
            messages = [
                SystemMessage(content=LEGAL_SYSTEM_PROMPT.format(context=context)),
                *chat_history,
                HumanMessage(content=query)
            ]
            response = self.llm.invoke(messages).content
            self.memory.add_turn(human=query, ai=response)
            return response
        
        elif route == RouteType.OUT_OF_SCOPE:
            return "Xin lỗi, tôi không thể giúp bạn thực hiện yêu cầu, việc này nằm ngoài khả năng của tôi"
        
        elif route == RouteType.CLARIFY:
            return "Tôi chưa hiểu rõ ý của bạn lắm, bạn có thể cung câp thêm thông tin chi tiết không?"