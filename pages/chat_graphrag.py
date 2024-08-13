import random

import streamlit as st
from openai import OpenAI

from pages.util import graph_search
from pages.util import streamlit_components as stc


def chat(api_key):
    client = OpenAI(api_key=api_key)
    assistant_id, thread_id, graph_store_id = stc.setting_graprag(client)
    if not graph_store_id:
        return
    search_engine = graph_search.create_global_search_engine(
        f"./data/graphrag/{graph_store_id}", api_key, "gpt-4o-mini"
    )

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
            global_context = search_engine.search(user_query)
            assistant_reply = stc.creat_assistant_reply(
                client, assistant_id, thread_id, global_context
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
