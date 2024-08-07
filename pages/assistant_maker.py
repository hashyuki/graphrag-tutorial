import streamlit as st
from openai import OpenAI
from openai.types import ChatModel

import common


def create_assistant(api_key):
    client = OpenAI(api_key=api_key)
    assistant_id = None

    with st.container(border=True):
        model_list = list(ChatModel.__args__)
        instructions = st.text_area(
            "システムプロンプト",
            value="あなたはAIアシスタントです。質問に日本語で回答してください。",
        )
        model = st.selectbox(
            "LLM model",
            options=model_list,
            index=model_list.index("gpt-4o-mini"),  # defaultでgpt-4o-miniを選択
        )

        if st.button("作成", use_container_width=True):
            assistant = client.beta.assistants.create(
                name="RAG Demo on Streamlit",
                instructions=instructions,
                model=model,
                tools=[{"type": "file_search"}],
            )
            assistant_id = assistant.id
    if assistant_id is not None:
        st.success(f"Assistant ID: {assistant.id}")


if __name__ == "__main__":
    common.init_state()
    common.sidebar()

    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
    else:
        create_assistant(st.session_state["api_key"])
