import random

import streamlit as st
from openai import OpenAI

import common
import tools
import tools.graphrag


def main(api_key):
    random.seed(42)
    client = OpenAI(api_key=api_key)
    assistant_id, thread_id, graph_store_id = common.setting_graprag(client)
    if not graph_store_id:
        return
    tools.graphrag.graph_rag.create(
        f"./data/graphrag/{graph_store_id}", api_key, "gpt-4o-mini"
    )

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
            pre_reply = tools.graphrag.graph_rag.chat(user_query)
            assistant_reply = common.creat_assistant_reply(
                client, assistant_id, thread_id, pre_reply
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
