import random

import streamlit as st
from openai import OpenAI

from pages.util import graph_search
from pages.util import streamlit_components as stc


def main(api_key):
    random.seed(42)
    client = OpenAI(api_key=api_key)

    left_col, center_col, right_col = st.columns(3)
    with left_col:
        left_assistant_id, left_thread_id = stc.setting_assistant(client)

    with center_col:
        center_assistant_id, center_thread_id = stc.setting_assistant(client)

    with right_col:
        right_assistant_id, right_thread_id, right_graph_store_id = stc.setting_graprag(
            client
        )

    if not left_assistant_id or not right_assistant_id or not right_graph_store_id:
        return

    search_engine = graph_search.create_global_search_engine(
        f"./data/graphrag/{right_graph_store_id}", api_key, "gpt-4o-mini"
    )

    if left_thread_id not in st.session_state:
        st.session_state[left_thread_id] = []
    for message in st.session_state[left_thread_id]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if center_thread_id not in st.session_state:
        st.session_state[center_thread_id] = []
    for message in st.session_state[center_thread_id]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if right_thread_id not in st.session_state:
        st.session_state[right_thread_id] = []
    for message in st.session_state[right_thread_id]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if user_query := st.chat_input("Ask me a question"):
        with left_col:
            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state[left_thread_id].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                assistant_reply = stc.creat_assistant_reply(
                    client, left_assistant_id, left_thread_id, user_query
                )
                st.session_state[left_thread_id].append(
                    {"role": "assistant", "content": assistant_reply}
                )

        with center_col:
            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state[center_thread_id].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                assistant_reply = stc.creat_assistant_reply(
                    client, center_assistant_id, center_thread_id, user_query
                )
                st.session_state[center_thread_id].append(
                    {"role": "assistant", "content": assistant_reply}
                )

        with right_col:
            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state[right_thread_id].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                global_context = search_engine.search(user_query)
                assistant_reply = stc.creat_assistant_reply(
                    client, right_assistant_id, right_thread_id, global_context
                )

                st.session_state[right_thread_id].append(
                    {"role": "assistant", "content": assistant_reply}
                )


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    stc.init_state()
    stc.sidebar()

    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
    else:
        main(st.session_state["api_key"])
