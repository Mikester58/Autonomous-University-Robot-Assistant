"""
Administrator Interface (Remote Host)
Capabilities: Upload Docs -> Build DB -> Download DB
"""

#python -m streamlit run admin.py

import streamlit as st
import os
import shutil
from database_bridge import InitializeDatabase, ZipDatabase, ListSessions, LoadSession, ClearCudaCache
from config import DEFAULT_EMBEDDING_MODEL, DEFAULT_DOCS_PATH, CHROMA_DIR

st.set_page_config(page_title="AURA Admin (Remote)", layout="wide")

page = st.sidebar.radio("Navigation", ["Database Builder", "Session Logs"])

if page == "Database Builder":
    st.header("Remote Database Builder")
    st.info("Upload documents here. The database will be built on this server, then you can download it to transfer to the Jetson.")

    # 1. File Upload Section
    st.subheader("1. Upload Documents")
    uploaded_files = st.file_uploader("Upload PDFs/Text", type=['pdf', 'txt'], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button(f"Process {len(uploaded_files)} Files"):
            # Clear old docs
            if os.path.exists(DEFAULT_DOCS_PATH):
                shutil.rmtree(DEFAULT_DOCS_PATH)
            os.makedirs(DEFAULT_DOCS_PATH)
            
            # Save new docs
            for uploaded_file in uploaded_files:
                with open(os.path.join(DEFAULT_DOCS_PATH, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"Saved {len(uploaded_files)} files to staging area.")

    st.divider()

    # 2. Build Database
    st.subheader("2. Build Vector Database")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Build Database", type="primary"):
            with st.spinner("Embedding documents... (This uses GPU/CPU)"):
                try:
                    ClearCudaCache()
                    InitializeDatabase(DEFAULT_EMBEDDING_MODEL, DEFAULT_DOCS_PATH, force_reload=True)
                    st.success("Database built successfully!")
                    ClearCudaCache()
                except Exception as e:
                    st.error(f"Error building database: {e}")

    # 3. Download Database
    with col2:
        if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
            st.success("Database is ready for download.")
            if st.button("Prepare Download"):
                zip_path = ZipDatabase()
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label="Download 'chroma_db.zip'",
                        data=fp,
                        file_name="chroma_db.zip",
                        mime="application/zip",
                        help="Transfer this file to the 'storage/' folder on your Jetson Nano."
                    )
        else:
            st.warning("No database found. Build it first.")

elif page == "Session Logs":
    st.header("Session Logs")
    # Note: These logs are local to *this* machine.
    # If users are on Jetson, you won't see their logs here unless synced.
    st.warning("Viewing logs stored on this remote server.")
    sessions = ListSessions()
    if sessions:
        sel = st.selectbox("Select Session", sessions)
        if sel:
            data = LoadSession(sel)
            for msg in data.get("messages", []):
                st.text(f"{msg.get('role').upper()}: {msg.get('content')}")
                st.divider()
    else:
        st.info("No logs found on this server.")