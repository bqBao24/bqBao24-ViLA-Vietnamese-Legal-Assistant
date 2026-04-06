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
    return ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=MAX_TOKEN_LIMIT,
        memory_key="chat_history",
        return_messages=True,       
        output_key="answer",        
    )


def build_chain() -> ConversationalRetrievalChain:
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