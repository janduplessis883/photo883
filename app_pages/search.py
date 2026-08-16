import streamlit as st

from app_pages._components import render_photo_grid, render_picture_view_control
from photo_ai.search import semantic_search

st.title("Photo883: Semantic search")

view_mode = render_picture_view_control("search_photo_view")

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
        st.session_state.search_results = results
    except Exception as exc:
        st.error(str(exc))

results = st.session_state.get("search_results", [])
if results:
    scores = {photo.id: score for photo, score in results}
    render_photo_grid(
        [photo for photo, _score in results],
        scores=scores,
        view_key="search_photo_view_results",
        view_mode=view_mode,
        show_view_control=False,
    )
