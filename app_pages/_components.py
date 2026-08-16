from __future__ import annotations

from pathlib import Path

import streamlit as st

from photo_ai.database import delete_photo
from photo_ai.models import PhotoRecord
from photo_ai.vector_store import delete_embeddings


VIEW_MODES = {
    "Details": {"columns": 4, "show_info": True},
    "4 columns": {"columns": 4, "show_info": False},
    "6 columns": {"columns": 6, "show_info": False},
    "8 columns": {"columns": 8, "show_info": False},
}


def render_photo_grid(
    records: list[PhotoRecord],
    scores: dict[int, float | None] | None = None,
    view_key: str = "photo_grid_view",
    view_mode: str | None = None,
    show_view_control: bool = True,
) -> None:
    if not records:
        st.info("No photos to show yet.")
        return

    if show_view_control:
        view_mode = render_picture_view_control(view_key)
    view = VIEW_MODES[view_mode or "Details"]
    column_count = int(view["columns"])
    show_info = bool(view["show_info"])

    for row_start in range(0, len(records), column_count):
        cols = st.columns(column_count, vertical_alignment="top")
        for col, photo in zip(cols, records[row_start : row_start + column_count], strict=False):
            path = Path(photo.path)
            with col:
                if show_info:
                    with st.container(border=True):
                        _render_image(path)
                        _render_photo_info(photo, scores)
                else:
                    _render_image(path)


def render_picture_view_control(view_key: str = "photo_grid_view") -> str:
    return st.segmented_control(
        "Picture view",
        options=list(VIEW_MODES),
        default="Details",
        key=view_key,
    ) or "Details"


def _render_image(path: Path) -> None:
    if path.exists():
        st.image(str(path), width="stretch")
    else:
        st.warning("File missing from disk")


def _render_photo_info(photo: PhotoRecord, scores: dict[int, float | None] | None = None) -> None:
    st.write(f"**{photo.filename}**")
    if photo.caption:
        st.caption(photo.caption)
    if scores and photo.id in scores:
        st.caption(f"Distance: {scores[photo.id]:.4f}" if scores[photo.id] else "Distance: n/a")
    tag_text = ", ".join(photo.tags[:8])
    if tag_text:
        st.caption(f"Tags: {tag_text}")
    with st.expander("Metadata", icon=":material/info:"):
        st.write(f"Path: `{photo.path}`")
        st.write(f"Hash: `{photo.file_hash}`")
        st.write(f"Scene: {photo.scene or 'Unknown'}")
        st.write(f"Taken: {photo.taken_at or 'Unknown'}")
        st.write(f"Size: {photo.width or '?'} x {photo.height or '?'}")
        if photo.latitude is not None and photo.longitude is not None:
            st.write(f"GPS: {photo.latitude:.6f}, {photo.longitude:.6f}")
        if st.button(
            "Delete image",
            icon=":material/delete:",
            key=f"delete_photo_{photo.id}",
            type="secondary",
        ):
            confirm_delete_photo(photo)


@st.dialog("Delete image?", icon=":material/delete:")
def confirm_delete_photo(photo: PhotoRecord) -> None:
    path = Path(photo.path)
    st.warning("This will delete the image from storage and remove it from the database. This cannot be undone.")
    if path.exists():
        st.image(str(path), width="stretch")
    else:
        st.error("The image file is already missing from storage.")
    st.write(f"**{photo.filename}**")
    st.caption(str(path))

    with st.container(horizontal=True):
        if st.button(
            "Delete permanently",
            icon=":material/delete_forever:",
            type="primary",
            key=f"confirm_delete_photo_{photo.id}",
        ):
            try:
                if path.exists():
                    path.unlink()
                delete_photo(photo.id)
                try:
                    delete_embeddings(
                        photo.id,
                        [photo.text_embedding_id, photo.image_embedding_id],
                    )
                except Exception as exc:
                    st.warning(f"The image was deleted, but vector cleanup failed: {exc}")
                st.session_state.pop("search_results", None)
                st.success("Image deleted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete image: {exc}")
        if st.button("Cancel", icon=":material/close:", key=f"cancel_delete_photo_{photo.id}"):
            st.rerun()
