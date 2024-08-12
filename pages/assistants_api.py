import random

import streamlit as st
from openai import OpenAI

import common


def main(api_key):
    random.seed(42)
    client = OpenAI(api_key=api_key)
    assistant_id, thread_id = common.setting_assistant(client)
    if not assistant_id:
        return

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask me a question"):
        # ユーザーの質問を表示・会話履歴に追加
        with st.chat_message("user"):
            st.markdown(user_query)
            st.session_state["chat_history"].append(
                {"role": "user", "content": user_query}
            )

        # アシスタントの回答を表示・会話履歴に追加
        with st.chat_message("assistant"):
            assistant_reply = common.creat_assistant_reply(
                client, assistant_id, thread_id, user_query
            )
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": assistant_reply}
            )


if __name__ == "__main__":
    st.set_page_config(layout="centered")
    common.init_state()
    common.sidebar()

    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
    else:
        main(st.session_state["api_key"])
