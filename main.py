import streamlit as st

from pages.util import streamlit_components as stc


def main():
    st.write("<div align='center'><b>− SETTING −</b></div>", unsafe_allow_html=True)
    st.write(
        "<div align='center'><font size='3'>Assistants IDの発行やDataStoreの作成ができます</font></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.page_link("pages/agent_creator.py", icon="🛠️", use_container_width=True)

    st.write("<div align='center'><b>− CHAT −</b></div>", unsafe_allow_html=True)
    st.write(
        "<div align='center'><font size='3'>発行したIDを入力することでチャットができます</font></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.page_link(
            "pages/chat_assistants_api.py", icon="💬", use_container_width=True
        )
        st.page_link("pages/chat_graphrag.py", icon="💬", use_container_width=True)
        st.page_link("pages/chat_side_by_side.py", icon="💬", use_container_width=True)

    st.write(
        "<div align='center'><b>− VISUALIZATION −</b></div>", unsafe_allow_html=True
    )
    st.write(
        "<div align='center'><font size='3'>knowledge graphの可視化ができます</font></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.page_link("pages/vizualization.py", icon="👓", use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(layout="centered")
    stc.init_state()
    stc.sidebar()
    main()
