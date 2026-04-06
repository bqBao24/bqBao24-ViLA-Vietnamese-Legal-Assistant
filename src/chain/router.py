from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from src.config.config import LLM_BASE_URL, LLM_MODEL_NAME
from src.chain.prompts import ROUTER_SYSTEM_PROMPT


class RouteType(str, Enum):
    GREETING     = "GREETING"      # chòa hỏi
    LEGAL        = "LEGAL"         # câu hỏi pháp luật 
    OUT_OF_SCOPE = "OUT_OF_SCOPE"  # không liên quan
    CLARIFY      = "CLARIFY"       # mơ hồ


class QueryRouter:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLM_MODEL_NAME,
            openai_api_base=LLM_BASE_URL,
            openai_api_key="not-needed",
            temperature=0,
            max_tokens=10,      
            streaming=False,
        )

    def classify(self, query: str, chat_history: list = None) -> RouteType:
        messages = [SystemMessage(content=ROUTER_SYSTEM_PROMPT)]
        if chat_history:
            messages.extend(chat_history)
 
        messages.append(HumanMessage(content=query))
 
        response = self.llm.invoke(messages)
        label = response.content.strip().upper()
 
        return self._parse_label(label)

    @staticmethod
    def _parse_label(label: str) -> RouteType:
        try:
            return RouteType(label)
        except ValueError:
            return RouteType.LEGAL
