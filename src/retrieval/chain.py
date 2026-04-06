from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationTokenBufferMemory
from langchain.chat_models import ChatOpenAI
from retrieval.langchain_retriever import LangChainHybridRetriever
from src.config.config import LLM_BASE_URL,LLM_MODEL_NAME,LLM_TEMPERATURE,LLM_MAX_TOKENS,MAX_HISTORY_TURNS,MAX_TOKEN_LIMIT,


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL_NAME,
        openai_api_base=LLM_BASE_URL,
        openai_api_key="none",   
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        streaming=True,
    )


def build_memory(llm: ChatOpenAI) -> ConversationTokenBufferMemory:
    """
    Memory giới hạn theo cả 2 chiều:
    - MAX_TOKEN_LIMIT  : cắt khi tổng token lịch sử vượt ngưỡng
    - MAX_HISTORY_TURNS: cắt khi số lượt hội thoại vượt ngưỡng
    ConversationTokenBufferMemory xử lý token limit tự động.
    Giới hạn turns được kiểm soát thêm trong build_chain().
    """
    return ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=MAX_TOKEN_LIMIT,
        memory_key="chat_history",
        return_messages=True,       # trả về dạng Message objects cho ConversationalRetrievalChain
        output_key="answer",        # chain trả về cả "answer" lẫn "source_documents", cần chỉ rõ key nào lưu vào memory
    )


def build_chain() -> ConversationalRetrievalChain:
    """
    Kết nối toàn bộ pipeline:
        User query
            ↓
        Condense question (query + chat history → standalone query)
            ↓
        LangChainHybridRetriever (BM25 + Chroma → RRF → Rerank)
            ↓
        LLM generate answer
            ↓
        Lưu vào Memory
    """
    llm = build_llm()
    memory = build_memory(llm)
    retriever = LangChainHybridRetriever()

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False,
    )

    return chain


def trim_memory_by_turns(memory: ConversationTokenBufferMemory) -> None:
    """
    Cắt lịch sử nếu vượt quá MAX_HISTORY_TURNS.
    Được gọi trước mỗi lượt hội thoại trong main.py.

    Mỗi "turn" = 1 cặp (HumanMessage, AIMessage).
    """
    messages = memory.chat_memory.messages
    max_messages = MAX_HISTORY_TURNS * 2    # mỗi turn gồm 2 messages

    if len(messages) > max_messages:
        # Giữ lại max_messages cuối cùng, bỏ phần cũ
        memory.chat_memory.messages = messages[-max_messages:]