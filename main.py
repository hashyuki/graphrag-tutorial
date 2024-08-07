import streamlit as st

import common


def main():
    st.page_link("pages/assistants_api.py", icon="1️⃣")
    st.page_link("pages/side_by_side.py", icon="2️⃣")


if __name__ == "__main__":
    common.init_state()
    common.sidebar()
    main()
