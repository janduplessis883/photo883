import streamlit as st

from photo_ai.database import initialize_database

st.set_page_config(
    page_title="Photo883",
    page_icon=":material/photo_library:",
    layout="wide",
)

initialize_database()

page = st.navigation(
    [
        st.Page("app_pages/library.py", title="Library", icon=":material/photo_library:"),
        st.Page("app_pages/search.py", title="Semantic search", icon=":material/search:"),
        st.Page("app_pages/index.py", title="Indexing", icon=":material/drive_folder_upload:"),
        st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:"),
    ]
)

page.run()
