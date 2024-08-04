import streamlit as st
from openai import OpenAI
from openai.types import ChatModel
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock


def main():
    with st.container(border=True):
        st.write("LLM Setting")
        st.session_state["openai_api_key"] = st.text_input(
            "OpenAI API Key", type="password", value=None
        )
        st.session_state["assistant_id"] = st.text_input(
            "Assistant ID", type="password", value=None
        )
        model_list = list(ChatModel.__args__)
        st.session_state["llm_model"] = st.selectbox(
            "LLM model",
            options=model_list,
            index=model_list.index("gpt-4o-mini"),  # defaultでgpt-4o-miniを選択
        )

    if st.session_state["openai_api_key"] or st.session_state["assistant_id"] is None:
        st.warning("OpenAI API keyとAssistant IDを入力してください")
        return

    client = OpenAI(api_key=st.session_state["openai_api_key"])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask me a question"):
        if "thread_id" not in st.session_state:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        with st.chat_message("user"):
            st.markdown(user_query)

        st.session_state.chat_history.append({"role": "user", "content": user_query})

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=user_query
        )

        with st.chat_message("assistant"):
            stream = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.session_state["assistant_id"],
                stream=True,
            )

            assistant_reply_box = st.empty()

            assistant_reply = ""

            for event in stream:
                if isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        assistant_reply_box.empty()
                        assistant_reply += event.data.delta.content[0].text.value
                        assistant_reply_box.markdown(assistant_reply)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": assistant_reply}
            )


if __name__ == "__main__":
    main()
