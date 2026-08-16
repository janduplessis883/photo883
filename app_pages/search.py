import streamlit as st

from app_pages._components import render_photo_grid
from photo_ai.search import semantic_search

st.title("Semantic search")

with st.form("semantic_search", border=False):
    query = st.text_input(
        "Search",
        placeholder="Search your photos...",
        label_visibility="collapsed",
    )
    limit = st.slider("Results", min_value=4, max_value=48, value=24, step=4)
    submitted = st.form_submit_button("Search", icon=":material/search:", type="primary")

st.caption("Try: dogs on beaches, modern houses with swimming pools, food in restaurants")

if submitted:
    try:
        with st.skeleton(height=240):
            results = semantic_search(query, limit=limit)
        scores = {photo.id: score for photo, score in results}
        render_photo_grid([photo for photo, _score in results], scores=scores)
    except Exception as exc:
        st.error(str(exc))
