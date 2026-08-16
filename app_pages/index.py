from pathlib import Path

import streamlit as st

from photo_ai.indexer import index_directory, scan_only

st.title("Indexing")

with st.container(border=True):
    root = st.text_input("Photo folder", value=str(Path.home() / "Pictures"))
    force = st.checkbox("Re-index existing photos")
    with st.container(horizontal=True):
        scan = st.button("Scan folder", icon=":material/folder_open:")
        index = st.button("Index new photos", icon=":material/play_arrow:", type="primary")

if scan:
    try:
        paths = scan_only(root)
        st.success(f"Discovered {len(paths)} supported images.")
        st.dataframe(
            [{"path": str(path), "filename": path.name} for path in paths[:500]],
            hide_index=True,
        )
        if len(paths) > 500:
            st.caption("Showing first 500 discovered images.")
    except Exception as exc:
        st.error(str(exc))

if index:
    progress_bar = st.progress(0)
    status = st.status("Indexing photos", expanded=True)
    log_slot = st.empty()
    messages: list[str] = []

    with status:
        for event in index_directory(root, force=force):
            if event.total:
                progress_bar.progress(event.current / event.total)
            messages.append(f"{event.current} / {event.total} - {event.message}")
            log_slot.code("\n".join(messages[-15:]))
        status.update(label="Indexing complete", state="complete", expanded=False)
