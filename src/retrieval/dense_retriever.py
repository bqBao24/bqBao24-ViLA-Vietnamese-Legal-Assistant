from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config.config import CHROMA_DB_PATH, DEVICE, EMBEDDING_MODEL_NAME, DENSE_TOP_K


def load_dense_retriever():
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": DEVICE, "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embedding_model,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": DENSE_TOP_K},
    )

    return retriever