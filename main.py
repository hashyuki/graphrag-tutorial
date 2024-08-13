import streamlit as st

from pages.util import streamlit_components as stc


def main():
    st.write("<div align='center'>SETTING</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.page_link("pages/agent_creator.py", icon="🛠️", use_container_width=True)

    st.write("<div align='center'>CHAT</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.page_link(
            "pages/chat_assistants_api.py", icon="💬", use_container_width=True
        )
        st.page_link("pages/chat_graphrag.py", icon="💬", use_container_width=True)
        st.page_link("pages/chat_side_by_side.py", icon="💬", use_container_width=True)

    st.write(
        "<div align='center'>手順</div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        """
        1. agent creatorで各種IDを発行してください
            - このとき発行されるIDはチャットの際に利用します。
        2. chat xxxで発行したIDを入力するとチャットができます。
            - Assistant IDだけを入力すると普通のChatGPTとして利用できます
            - Assisiant IDとVectorStore IDを入力すると、Assistants APIを利用したRAGが使用できます。
            - Assistatn IDとGraphStore IDを入力すると、MicrosoftのGraphRAGを利用したRAGが使用できます。
        """


if __name__ == "__main__":
    st.set_page_config(layout="centered")
    stc.init_state()
    stc.sidebar()
    main()
