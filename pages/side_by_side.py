import random

import streamlit as st
from openai import OpenAI

import common
import tools.graphrag


def main(api_key):
    random.seed(42)
    client = OpenAI(api_key=api_key)

    left_col, center_col, right_col = st.columns(3)
    with left_col:
        left_assistant_id, left_thread_id = common.setting_assistant(client)

    with center_col:
        center_assistant_id, center_thread_id = common.setting_assistant(client)

    with right_col:
        right_assistant_id, right_thread_id, right_graph_store_id = (
            common.setting_graprag(client)
        )

    if not left_assistant_id or not right_assistant_id or not right_graph_store_id:
        return

    tools.graphrag.graph_rag.create(
        f"./data/graphrag/{right_graph_store_id}", api_key, "gpt-4o-mini"
    )

    if "left_chat_history" not in st.session_state:
        st.session_state["left_chat_history"] = []
    for message in st.session_state["left_chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if "center_chat_history" not in st.session_state:
        st.session_state["center_chat_history"] = []
    for message in st.session_state["center_chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if "right_chat_history" not in st.session_state:
        st.session_state["right_chat_history"] = []
    for message in st.session_state["right_chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if user_query := st.chat_input("Ask me a question"):
        with left_col:
            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state["left_chat_history"].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                assistant_reply = common.creat_assistant_reply(
                    client, left_assistant_id, left_thread_id, user_query
                )
                st.session_state["left_chat_history"].append(
                    {"role": "assistant", "content": assistant_reply}
                )

        with center_col:
            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state["center_chat_history"].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                assistant_reply = common.creat_assistant_reply(
                    client, center_assistant_id, center_thread_id, user_query
                )
                st.session_state["center_chat_history"].append(
                    {"role": "assistant", "content": assistant_reply}
                )

        with right_col:
            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state["right_chat_history"].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                pre_reply = tools.graphrag.graph_rag.chat(user_query)
                assistant_reply = common.creat_assistant_reply(
                    client, right_assistant_id, right_thread_id, pre_reply
                )

                st.session_state["right_chat_history"].append(
                    {"role": "assistant", "content": assistant_reply}
                )


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    common.init_state()
    common.sidebar()

    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
    else:
        main(st.session_state["api_key"])
