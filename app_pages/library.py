import streamlit as st

from app_pages._components import render_photo_grid, render_picture_view_control
from photo_ai.database import get_filter_values, list_duplicate_photos, list_photos, stats

st.title("Photo883: Library")
st.session_state.setdefault("show_duplicate_photos", False)

summary = stats()
button_label = "Show all images" if st.session_state.show_duplicate_photos else "Duplicate images"
cols = st.columns([1, 1, 1, 1, 0.72], vertical_alignment="bottom")
cols[0].metric("Photos", summary["total"])
cols[1].metric("Analyzed", summary["analyzed"])
cols[2].metric("Embedded", summary["embedded"])
cols[3].metric("Failed", summary["failed"])
with cols[4]:
    if st.button(button_label, icon=":material/content_copy:"):
        st.session_state.show_duplicate_photos = not st.session_state.show_duplicate_photos
        st.rerun()

filters = get_filter_values()
with st.expander("Filters", icon=":material/filter_alt:"):
    folder = st.selectbox("Folder", [""] + filters["folders"], format_func=lambda value: value or "All folders")
    tag = st.selectbox("Tag", [""] + filters["tags"], format_func=lambda value: value or "All tags")
    scene = st.selectbox("Scene", [""] + filters["scenes"], format_func=lambda value: value or "All scenes")
    object_name = st.selectbox("Object", [""] + filters["objects"], format_func=lambda value: value or "All objects")
    st.divider()
    view_col, count_col = st.columns([1, 1.6], vertical_alignment="bottom")
    with view_col:
        view_mode = render_picture_view_control("library_photo_view")
    with count_col:
        image_count = st.segmented_control(
            "Image count",
            options=[200, 300, 400, 500],
            default=200,
            key="library_image_count",
        )

if st.session_state.show_duplicate_photos:
    records = list_duplicate_photos(limit=image_count or 200)
else:
    records = list_photos(
        folder=folder or None,
        tag=tag or None,
        scene=scene or None,
        object_name=object_name or None,
        limit=image_count or 200,
    )

if st.session_state.show_duplicate_photos:
    st.caption(f"Showing {len(records)} images with duplicate file hashes.")
else:
    st.caption(f"Showing {len(records)} images.")

render_photo_grid(
    records,
    view_key="library_photo_view_results",
    view_mode=view_mode,
    show_view_control=False,
)
