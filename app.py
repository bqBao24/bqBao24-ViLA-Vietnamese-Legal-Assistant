import sys
from pathlib import Path
import streamlit as st
from src.chain.chain import LegalChatBot

# Page config
st.set_page_config(
    page_title="Tư vấn Pháp luật",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ Chatbot Tư vấn Pháp luật Việt Nam")
st.caption("Hỏi đáp các vấn đề pháp luật dựa trên văn bản luật Việt Nam.")

if "chatbot" not in st.session_state:
    with st.spinner("Đang khởi động hệ thống..."):
        st.session_state.chatbot = LegalChatBot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Nhập câu hỏi pháp luật của bạn..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("......"):
            response = st.session_state.chatbot.chat(query)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

with st.sidebar:
    st.header("Thông tin")
    st.info(
        "Chatbot tư vấn pháp luật Việt Nam. "
        "Chỉ hỗ trợ các câu hỏi liên quan đến pháp luật."
    )

    st.divider()

    if st.button("🗑️ Xóa lịch sử hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chatbot.memory.clear()
        st.rerun()