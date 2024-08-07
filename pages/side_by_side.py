import random

import streamlit as st
from openai import OpenAI

import common


def main(api_key):
    random.seed(42)
    client = OpenAI(api_key=api_key)

    left_col, right_col = st.columns(2)
    with left_col:
        left_assistant_id, left_thread_id = common.setting_assistant(client)

    with right_col:
        right_assistant_id, right_thread_id = common.setting_assistant(client)

    if not left_assistant_id or not right_assistant_id:
        return

    if user_query := st.chat_input("Ask me a question"):
        with left_col:
            if "left_chat_history" not in st.session_state:
                st.session_state["left_chat_history"] = []
            for message in st.session_state["left_chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

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

        with right_col:
            if "right_chat_history" not in st.session_state:
                st.session_state["right_chat_history"] = []
            for message in st.session_state["right_chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # ユーザーの質問を表示・会話履歴に追加
            with st.chat_message("user"):
                st.markdown(user_query)
                st.session_state["right_chat_history"].append(
                    {"role": "user", "content": user_query}
                )

            # アシスタントの回答を表示・会話履歴に追加
            with st.chat_message("assistant"):
                assistant_reply = common.creat_assistant_reply(
                    client, right_assistant_id, right_thread_id, user_query
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
