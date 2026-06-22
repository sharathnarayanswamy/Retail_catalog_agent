"""
Streamlit web UI — thin demo wrapper around the agent.

Run from the project root:
    streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st

from src.catalog import load_catalog
from src.agent import Agent

st.set_page_config(
    page_title="Agentic Product Discovery",
    page_icon="",
    layout="centered",
)

st.title("Agentic Product Discovery")
st.caption("Ask me to find clothing and footwear. I'll search the real catalog.")


@st.cache_resource(show_spinner="Loading catalog...")
def get_catalog() -> list[dict]:
    try:
        return load_catalog()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()


catalog = get_catalog()

if "agent" not in st.session_state:
    st.session_state.agent = Agent(catalog)
    st.session_state.history: list[tuple[str, str]] = []

with st.sidebar:
    st.markdown(f"**Catalog:** {len(catalog)} products")
    if st.button("New conversation", use_container_width=True):
        st.session_state.agent.reset()
        st.session_state.history = []
        st.rerun()
    st.divider()
    st.markdown("**Try asking:**")
    examples = [
        "Warm jacket for winter under £100, not black",
        "Casual tops for women under £40",
        "Something for a city break — smart but comfortable",
        "Running shoes",
        "A gift for my dad",
    ]
    for ex in examples:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state._prefill = ex
            st.rerun()

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.write(content)

prefill = st.session_state.pop("_prefill", None)

if prompt := st.chat_input("What are you looking for?", key="chat_input"):
    prefill = prompt

if prefill:
    st.session_state.history.append(("user", prefill))
    with st.chat_message("user"):
        st.write(prefill)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            response = st.session_state.agent.chat(prefill)
        st.write(response)

    st.session_state.history.append(("assistant", response))
    st.rerun()
