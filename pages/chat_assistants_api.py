import random

import streamlit as st
from openai import OpenAI

from pages.util import streamlit_components as stc


def chat(api_key):
    client = OpenAI(api_key=api_key)
    assistant_id, thread_id = stc.setting_assistant(client)
    if not assistant_id:
        return

    if thread_id not in st.session_state:
        st.session_state[thread_id] = []
    for message in st.session_state[thread_id]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask me a question"):
        # ユーザーの質問を表示・会話履歴に追加
        with st.chat_message("user"):
            st.markdown(user_query)
            st.session_state[thread_id].append({"role": "user", "content": user_query})

        # アシスタントの回答を表示・会話履歴に追加
        with st.chat_message("assistant"):
            assistant_reply = stc.creat_assistant_reply(
                client, assistant_id, thread_id, user_query
            )
            st.session_state[thread_id].append(
                {"role": "assistant", "content": assistant_reply}
            )


def main():
    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
        return

    chat(st.session_state["api_key"])


if __name__ == "__main__":
    random.seed(42)
    st.set_page_config(layout="centered")
    stc.init_state()
    stc.sidebar()

    main()
