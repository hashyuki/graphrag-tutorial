import asyncio
import random

import streamlit as st
from openai import OpenAI

from pages.util import graph_search
from pages.util import streamlit_components as stc


async def process_chat(
    client, assistant_id, thread_id, user_query, col, search_engine=None
):
    with col:
        # ユーザーの質問を表示・会話履歴に追加
        with st.chat_message("user"):
            st.markdown(user_query)
            st.session_state[thread_id].append({"role": "user", "content": user_query})

        # アシスタントの回答を表示・会話履歴に追加
        with st.chat_message("assistant"):
            context = (
                await search_engine.asearch(user_query) if search_engine else user_query
            )
            assistant_reply = await stc.create_assistant_reply_async(
                client, assistant_id, thread_id, context
            )
            st.session_state[thread_id].append(
                {"role": "assistant", "content": assistant_reply}
            )


async def chat(api_key):
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

    for col, thread_id in zip(
        [left_col, center_col, right_col],
        [left_thread_id, center_thread_id, right_thread_id],
    ):
        if thread_id not in st.session_state:
            st.session_state[thread_id] = []
        for message in st.session_state[thread_id]:
            with col:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    if user_query := st.chat_input("Ask me a question"):
        await asyncio.gather(
            process_chat(
                client, left_assistant_id, left_thread_id, user_query, left_col
            ),
            process_chat(
                client, center_assistant_id, center_thread_id, user_query, center_col
            ),
            process_chat(
                client,
                right_assistant_id,
                right_thread_id,
                user_query,
                right_col,
                search_engine,
            ),
        )


def main():
    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
        return

    asyncio.run(chat(st.session_state["api_key"]))


if __name__ == "__main__":
    random.seed(42)
    st.set_page_config(layout="wide")
    stc.init_state()
    stc.sidebar()

    main()
