from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from src.config.config import LLM_BASE_URL, LLM_MODEL_NAME, LLM_TEMPERATURE,MAX_HISTORY_TURNS,MAX_TOKEN_LIMIT
from src.chain.prompts import SUMMARIZE_SYSTEM_PROMPT

TURNS_TO_SUMMARIZE = 7
TURNS_TO_KEEP = MAX_HISTORY_TURNS - TURNS_TO_SUMMARIZE 

class ConversationMemory:
    def __init__(self):
        self.summary: str = ""
        self.turns: list[tuple[str, str]] = []
        self.llm = ChatOpenAI(
            model=LLM_MODEL_NAME,
            openai_api_base=LLM_BASE_URL,
            openai_api_key="not-needed",
            temperature=LLM_TEMPERATURE,
            streaming=False,
        )

    def add_turn(self, human: str, ai: str) -> None:
        self.turns.append((human, ai))

        if self._should_summarize():
            self._summarize_old_turns()

    def build_history(self) -> list:
        messages = []
        if self.summary:
            messages.append(
                SystemMessage(content=f"Tóm tắt cuộc trò chuyện trước:\n{self.summary}")
            )

        for human, ai in self.turns:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))

        return messages

    def clear(self) -> None:
        self.summary = ""
        self.turns = []



    def _should_summarize(self) -> bool:
        if len(self.turns) > MAX_HISTORY_TURNS:
            return True
        total_text = self.summary
        for human, ai in self.turns:
            total_text += human + ai
        estimated_tokens = len(total_text) / 4
        if estimated_tokens > MAX_TOKEN_LIMIT:
            return True
        return False

    def _summarize_old_turns(self) -> None:
        old_turns = self.turns[:TURNS_TO_SUMMARIZE]
        self.turns = self.turns[TURNS_TO_SUMMARIZE:]
        content_to_summarize = self._format_turns_for_summary(old_turns)
        if self.summary:
            content_to_summarize = (
                f"Tóm tắt trước đó:\n{self.summary}\n\n"
                f"Hội thoại tiếp theo:\n{content_to_summarize}"
            )
        messages = [
            SystemMessage(content=SUMMARIZE_SYSTEM_PROMPT),
            HumanMessage(content=content_to_summarize),
        ]

        response = self.llm.invoke(messages)
        self.summary = response.content.strip()

    @staticmethod
    def _format_turns_for_summary(turns: list[tuple[str, str]]) -> str:
        lines = []
        for i, (human, ai) in enumerate(turns, start=1):
            lines.append(f"Lượt {i}:")
            lines.append(f"  Người dùng: {human}")
            lines.append(f"  Trợ lý: {ai}")
        return "\n".join(lines)