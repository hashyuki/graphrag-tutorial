import random

import streamlit as st
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock


def init_state():
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = None


def sidebar():
    st.session_state["api_key"] = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-****",
        value=st.session_state["api_key"],
    )


def setting_assistant(client):
    with st.container(border=True):
        st.write("LLM Setting")

        # assistant idを入力
        with st.container(border=True):
            assistant_id = st.text_input(
                "Assistant ID",
                type="password",
                placeholder="asst-****",
                key=random.random(),
            )

        # RAGをしたい場合は対象のファイルをアップロード
        with st.container(border=True):
            uploaded_files = st.file_uploader(
                "[Optional] RAGの対象ファイルをアップロード",
                accept_multiple_files=True,
                key=random.random(),
            )
            if uploaded_files and st.button(
                "VectorStoreの作成",
                use_container_width=True,
                key=random.random(),
            ):
                create_vector_store(client, assistant_id, uploaded_files)

    # assistant_idに対応したthreadを作成。
    @st.cache_resource()
    def create_thread(key):
        thread = client.beta.threads.create()
        return thread.id

    thread_id = create_thread(assistant_id)
    return assistant_id, thread_id


def create_vector_store(client, assistant_id, uploaded_files):
    tmp_file_paths = []
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.getvalue()
        location = f"temp_file_{uploaded_file.name}"
        with open(location, "wb") as f:
            f.write(bytes_data)
        tmp_file_paths.append(location)

    file_streams = [open(path, "rb") for path in tmp_file_paths]
    vector_store = client.beta.vector_stores.create(
        name="RAG Demo", expires_after={"anchor": "last_active_at", "days": 1}
    )
    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )


def creat_assistant_reply(client, assistant_id, thread_id, user_query):
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_query
    )
    stream = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        stream=True,
    )

    assistant_reply_box = st.empty()
    assistant_reply = ""

    for event in stream:
        if isinstance(event, ThreadMessageDelta):
            if isinstance(event.data.delta.content[0], TextDeltaBlock):
                assistant_reply += event.data.delta.content[0].text.value
                assistant_reply_box.markdown(assistant_reply)
    return assistant_reply
