import random

import streamlit as st
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock


def init_state():
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = None


def sidebar():
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-****",
        value=st.session_state["api_key"],
    )

    st.session_state["api_key"] = api_key


def setting_assistant(client):
    with st.container(border=True):
        assistant_id = ""
        # assistant idを入力
        assistant_id = st.text_input(
            "Assistant ID",
            type="password",
            placeholder="asst_****",
            key=random.random(),
        )

        # RAG対象のIDを入力
        vector_store_id = st.text_input(
            "VectorStore ID",
            type="password",
            placeholder="vs_****",
            disabled=(assistant_id == ""),
            key=random.random(),
        )

        if len(assistant_id) == 29 and assistant_id.startswith("asst_"):
            _update_assistant(client, assistant_id, vector_store_id)

    # assistant_idに対応したthreadを作成。
    @st.cache_resource()
    def create_thread(key1, key2):
        thread = client.beta.threads.create()
        return thread.id

    thread_id = create_thread(assistant_id, vector_store_id)
    return assistant_id, thread_id


def setting_graprag(client):
    with st.container(border=True):
        # assistant idを入力
        assistant_id = st.text_input(
            "Assistant ID",
            type="password",
            placeholder="asst_****",
            key=random.random(),
        )

        # RAG対象のIDを入力
        graph_store_id = st.text_input(
            "GraphStore ID",
            type="password",
            placeholder="gs_****",
            disabled=(assistant_id == ""),
            key=random.random(),
        )

    # assistant_idに対応したthreadを作成。
    @st.cache_resource()
    def create_thread(key1, key2):
        thread = client.beta.threads.create()
        return thread.id

    thread_id = create_thread(assistant_id, graph_store_id)

    return assistant_id, thread_id, graph_store_id


def _update_assistant(client, assistant_id, vector_store_id):
    if len(vector_store_id) == 27:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        )
    else:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={"file_search": {"vector_store_ids": []}},
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
