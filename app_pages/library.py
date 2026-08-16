import streamlit as st

from app_pages._components import render_photo_grid
from photo_ai.database import get_filter_values, list_photos, stats

st.title("Library")

summary = stats()
cols = st.columns(4)
cols[0].metric("Photos", summary["total"])
cols[1].metric("Analyzed", summary["analyzed"])
cols[2].metric("Embedded", summary["embedded"])
cols[3].metric("Failed", summary["failed"])

filters = get_filter_values()
with st.container(border=True):
    st.subheader("Filters")
    folder = st.selectbox("Folder", [""] + filters["folders"], format_func=lambda value: value or "All folders")
    tag = st.selectbox("Tag", [""] + filters["tags"], format_func=lambda value: value or "All tags")
    scene = st.selectbox("Scene", [""] + filters["scenes"], format_func=lambda value: value or "All scenes")
    object_name = st.selectbox("Object", [""] + filters["objects"], format_func=lambda value: value or "All objects")

records = list_photos(
    folder=folder or None,
    tag=tag or None,
    scene=scene or None,
    object_name=object_name or None,
)

render_photo_grid(records)
