import streamlit as st
from openai import OpenAI
from openai.types import ChatModel
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock


def create_llm_setting(client, key):
    with st.container(border=True):
        st.write("LLM Setting")
        assistant_init_method = st.radio(
            "Assistants APIの初期化方法",
            ["新規で作成する", "既存のIDを利用する"],
            horizontal=True,
            key=f"{key}-radio",
        )

        with st.container():
            if assistant_init_method == "新規で作成する":
                create_new_assistant(client, key)
            else:
                use_existing_assistant(key)

        uploaded_files = st.file_uploader(
            "[Optional] RAGの対象ファイルをアップロード",
            accept_multiple_files=True,
            key=f"{key}-file-upload",
        )

        if uploaded_files and st.button(
            "VectorStoreの作成",
            use_container_width=True,
            key=f"{key}-file-upload-button",
        ):
            create_vector_store(client, uploaded_files, key)

        assistant_id = st.session_state.get(f"assistant_id_{key}")
        if not assistant_id:
            st.warning("LLMの設定を正しくして下さい。")
            return 0
        return 1


def create_new_assistant(client, key):
    model_list = list(ChatModel.__args__)
    instructions = st.text_area(
        "システムプロンプト",
        value="あなたはAIアシスタントです。質問に日本語で回答してください。",
        key=f"{key}-instructions-input",
    )
    model = st.selectbox(
        "LLM model",
        options=model_list,
        index=model_list.index("gpt-4o-mini"),  # defaultでgpt-4o-miniを選択
        key=f"{key}-llm-model-select",
    )

    if st.button("作成", use_container_width=True, key=f"{key}-assistant-make-button"):
        assistant = client.beta.assistants.create(
            name="RAG Demo on Streamlit",
            instructions=instructions,
            model=model,
            tools=[{"type": "file_search"}],
        )
        st.session_state[f"assistant_id_{key}"] = assistant.id
        st.write(f"Success creating assistant.\n assistant id:{assistant.id}")


def use_existing_assistant(key):
    st.session_state[f"assistant_id_{key}"] = st.text_input(
        "Assistant ID",
        type="password",
        placeholder="asst-****",
        key=f"{key}-assistant-id-input",
    )


def create_vector_store(client, uploaded_files, key):
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
        assistant_id=st.session_state[f"assistant_id_{key}"],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )


def chat(client, user_query, key):
    if f"thread_id_{key}" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state[f"thread_id_{key}"] = thread.id

    with st.chat_message("user"):
        st.markdown(user_query)

    st.session_state.setdefault(f"chat_history_{key}", []).append(
        {"role": "user", "content": user_query}
    )
    client.beta.threads.messages.create(
        thread_id=st.session_state[f"thread_id_{key}"], role="user", content=user_query
    )

    with st.chat_message("assistant"):
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state[f"thread_id_{key}"],
            assistant_id=st.session_state[f"assistant_id_{key}"],
            stream=True,
        )

        assistant_reply_box = st.empty()
        assistant_reply = ""

        for event in stream:
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    assistant_reply += event.data.delta.content[0].text.value
                    assistant_reply_box.markdown(assistant_reply)

        st.session_state[f"chat_history_{key}"].append(
            {"role": "assistant", "content": assistant_reply}
        )


def main():
    st.set_page_config(layout="wide")

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-****")
    if not api_key:
        return

    client = OpenAI(api_key=api_key)
    cols = st.columns(2)

    with cols[0]:
        left_status = create_llm_setting(client, "left")
    with cols[1]:
        right_status = create_llm_setting(client, "right")

    if left_status == 0 and right_status == 0:
        return

    cols = st.columns(2)
    with cols[0]:
        chat_history = st.session_state.get("chat_history_left", [])
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    with cols[1]:
        chat_history = st.session_state.get("chat_history_right", [])
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_query := st.chat_input("Ask me a question"):
        with cols[0]:
            chat(client, user_query, "left")
        with cols[1]:
            chat(client, user_query, "right")


if __name__ == "__main__":
    main()
