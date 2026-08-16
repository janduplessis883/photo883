import streamlit as st

from config import (
    CHROMA_DIR,
    MLX_EMBEDDING_MODEL,
    OPENAI_COMPAT_BASE_URL,
    OPENAI_COMPAT_VISION_MODEL,
    SQLITE_PATH,
)

st.title("Settings")

with st.container(border=True):
    st.subheader("Local model endpoint")
    st.write(f"Base URL: `{OPENAI_COMPAT_BASE_URL}`")
    st.write(f"Vision model: `{OPENAI_COMPAT_VISION_MODEL}`")
    st.write(f"MLX embedding model: `{MLX_EMBEDDING_MODEL}`")

with st.container(border=True):
    st.subheader("Storage")
    st.write(f"SQLite: `{SQLITE_PATH}`")
    st.write(f"ChromaDB: `{CHROMA_DIR}`")
    st.caption("Photos remain in their original folders. The app stores paths, metadata, AI text, and vectors only.")
