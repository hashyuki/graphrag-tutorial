import os
import random
import string

import streamlit as st
from openai import OpenAI
from openai.types import ChatModel

import common
import tools
import tools.graphrag


def create_assistant(api_key):
    client = OpenAI(api_key=api_key)
    assistant_id = None

    st.header("Create Assistant")
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

        if st.button("Create Assistants", use_container_width=True):
            assistant = client.beta.assistants.create(
                name="RAG Demo on Streamlit",
                instructions=instructions,
                model=model,
                tools=[{"type": "file_search"}],
            )
            assistant_id = assistant.id

        if assistant_id is not None:
            st.success(f"Assistant ID: {assistant.id}")


def create_vector_store(api_key):
    client = OpenAI(api_key=api_key)
    vector_store_id = None

    st.header("Create VectorStore")
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "RAGの対象ファイルをアップロード",
            accept_multiple_files=True,
            key="vector",
        )
        if st.button("Create VectorStore", use_container_width=True):
            tmp_file_paths = []
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.getvalue()
                location = f"./data/assistants_api/input/{uploaded_file.name}"
                with open(location, "wb") as f:
                    f.write(bytes_data)
                tmp_file_paths.append(location)

            file_streams = [open(path, "rb") for path in tmp_file_paths]
            vector_store = client.beta.vector_stores.create(
                name="RAG Demo",
                expires_after={"anchor": "last_active_at", "days": 1},
            )
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
            vector_store_id = vector_store.id

        if vector_store_id is not None:
            st.success(f"VectorStore ID: {vector_store_id}")


def create_graph_store(api_key):
    graph_store_id = None

    st.header("Create GraphStore")
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "RAGの対象ファイルをアップロード", accept_multiple_files=True, key="graph"
        )
        if st.button("Create GraphStore", use_container_width=True):
            graph_store_id = "gs_" + "".join(
                random.choices(string.ascii_letters + string.digits, k=24)
            )
            os.makedirs(f"./data/graphrag/{graph_store_id}/input", exist_ok=True)

            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.getvalue()
                location = (
                    f"./data/graphrag/{graph_store_id}/input/{uploaded_file.name}"
                )
                with open(location, "wb") as f:
                    f.write(bytes_data)

            tools.graphrag.graph_store.create(
                f"./data/graphrag/{graph_store_id}", api_key, "gpt-4o-mini"
            )

        if graph_store_id is not None:
            st.success(f"GraphStore ID: {graph_store_id}")


def main():
    if not st.session_state["api_key"]:
        st.warning("OpenAI API Keyが設定されていません。")
        return

    api_key = st.session_state["api_key"]
    create_assistant(api_key)
    create_vector_store(api_key)
    create_graph_store(api_key)


if __name__ == "__main__":
    common.init_state()
    common.sidebar()

    main()
