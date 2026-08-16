from __future__ import annotations

from pathlib import Path

import streamlit as st

from photo_ai.models import PhotoRecord


def render_photo_grid(records: list[PhotoRecord], scores: dict[int, float | None] | None = None) -> None:
    if not records:
        st.info("No photos to show yet.")
        return

    for row_start in range(0, len(records), 4):
        cols = st.columns(4, vertical_alignment="top")
        for col, photo in zip(cols, records[row_start : row_start + 4], strict=False):
            with col.container(border=True):
                path = Path(photo.path)
                if path.exists():
                    st.image(str(path), width="stretch")
                else:
                    st.warning("File missing from disk")
                st.write(f"**{photo.filename}**")
                if photo.caption:
                    st.caption(photo.caption)
                if scores and photo.id in scores:
                    st.caption(f"Distance: {scores[photo.id]:.4f}" if scores[photo.id] else "Distance: n/a")
                tag_text = ", ".join(photo.tags[:8])
                if tag_text:
                    st.caption(f"Tags: {tag_text}")
                with st.expander("Metadata"):
                    st.write(f"Path: `{photo.path}`")
                    st.write(f"Hash: `{photo.file_hash}`")
                    st.write(f"Scene: {photo.scene or 'Unknown'}")
                    st.write(f"Taken: {photo.taken_at or 'Unknown'}")
                    st.write(f"Size: {photo.width or '?'} x {photo.height or '?'}")
                    if photo.latitude is not None and photo.longitude is not None:
                        st.write(f"GPS: {photo.latitude:.6f}, {photo.longitude:.6f}")
