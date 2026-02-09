"""
Administrator Interface for ECEN 214 Lab Assistant
Configure models, train database, view chat histories
"""

import streamlit as st
import os
import json
from datetime import datetime
from langchain_ollama import ChatOllama

from database_bridge import InitializeDatabase, SaveSession, ListSessions, LoadSession, ClearCudaCache, UnloadOllamaModel
from model import GetListOfModels
from config import DEFAULT_EMBEDDING_MODEL, DEFAULT_DOCS_PATH, CHROMA_DIR, SESSIONS_DIR

st.set_page_config(page_title="ECEN 214 Admin", layout="wide")
st.title("ECEN 214 Lab Assistant - Admin Panel")

# Sidebar navigation
page = st.sidebar.radio("Admin Functions", ["Model Configuration", "Database Management", "Chat Histories"])

# Model Configuration Page
if page == "Model Configuration":
    st.header("Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Models")
        models = GetListOfModels()
        
        if models:
            for model in models:
                st.text(f"- {model}")
        else:
            st.warning("No models found. Ensure Ollama is running.")
        
        if st.button("Refresh Model List"):
            st.rerun()
    
    with col2:
        st.subheader("Set Active Model")
        
        # Load current config
        config_file = "active_model.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                current_config = json.load(f)
        else:
            current_config = {"model": "tinyllama"}
        
        st.info(f"Current model: {current_config['model']}")
        
        if models:
            selected_model = st.selectbox("Select model for user interface", models)
            
            if st.button("Set Active Model"):
                current_config["model"] = selected_model
                current_config["updated_at"] = datetime.now().isoformat()
                
                with open(config_file, 'w') as f:
                    json.dump(current_config, f, indent=2)
                
                st.success(f"Active model set to: {selected_model}")
                st.info("Users will use this model on next session")
    
    st.divider()
    
    st.subheader("GPU Memory Status")
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            mem_info = result.stdout.strip().split(',')
            used = mem_info[0].strip()
            total = mem_info[1].strip()
            st.metric("GPU Memory", f"{used} MB / {total} MB")
    except:
        st.warning("Could not read GPU memory")

# Database Management Page
elif page == "Database Management":
    st.header("Database Management")
    
    st.subheader("Document Indexing")
    
    docs_path = st.text_input("Documents Directory", DEFAULT_DOCS_PATH)
    
    if os.path.isdir(docs_path):
        doc_files = [f for f in os.listdir(docs_path) 
                     if f.endswith(('.pdf', '.txt', '.md', '.docx'))]
        st.success(f"Found {len(doc_files)} documents")
        
        with st.expander("Document List"):
            for doc in doc_files:
                st.text(f"- {doc}")
    else:
        st.error("Invalid directory path")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Build/Rebuild Database", type="primary", use_container_width=True):
            if os.path.isdir(docs_path):
                with st.spinner("Indexing documents (this may take several minutes)..."):
                    try:
                        ClearCudaCache()
                        db = InitializeDatabase(
                            DEFAULT_EMBEDDING_MODEL,
                            docs_path,
                            force_reload=True
                        )
                        st.success("Database built successfully")
                        st.info("Embedding model automatically unloaded from GPU")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Invalid path")
    
    with col2:
        if st.button("Unload Embedding Model", use_container_width=True):
            try:
                UnloadOllamaModel(DEFAULT_EMBEDDING_MODEL)
                ClearCudaCache()
                st.success("Embedding model unloaded")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.divider()
    
    st.subheader("Database Status")
    if os.path.isdir(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        st.success("Database exists and ready")
        
        try:
            db_size = sum(
                os.path.getsize(os.path.join(CHROMA_DIR, f))
                for f in os.listdir(CHROMA_DIR)
                if os.path.isfile(os.path.join(CHROMA_DIR, f))
            ) / (1024 * 1024)
            st.metric("Database Size", f"{db_size:.2f} MB")
        except:
            pass
    else:
        st.warning("No database found. Build database to enable user queries.")

# Chat Histories Page
elif page == "Chat Histories":
    st.header("Chat Histories")
    
    saved_sessions = ListSessions()
    
    if not saved_sessions:
        st.info("No saved chat sessions found")
    else:
        st.success(f"Found {len(saved_sessions)} saved sessions")
        
        selected_session = st.selectbox("Select session to view", saved_sessions)
        
        if selected_session:
            try:
                session_data = LoadSession(selected_session)
                
                st.subheader(f"Session: {selected_session}")
                st.caption(f"Saved: {session_data.get('timestamp', 'Unknown')}")
                
                st.divider()
                
                messages = session_data.get("messages", [])
                
                for msg in messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    
                    if role in ["user", "human"]:
                        st.markdown(f"**User:** {content}")
                    else:
                        st.markdown(f"**Assistant:** {content}")
                    
                    st.divider()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Export as JSON"):
                        st.download_button(
                            "Download JSON",
                            data=json.dumps(session_data, indent=2),
                            file_name=f"{selected_session}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("Export as Text"):
                        text_export = f"Session: {selected_session}\n"
                        text_export += f"Date: {session_data.get('timestamp', 'Unknown')}\n\n"
                        
                        for msg in messages:
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")
                            text_export += f"{role.upper()}: {content}\n\n"
                        
                        st.download_button(
                            "Download Text",
                            data=text_export,
                            file_name=f"{selected_session}.txt",
                            mime="text/plain"
                        )
                
                with col3:
                    if st.button("Delete Session", type="secondary"):
                        try:
                            filepath = os.path.join(SESSIONS_DIR, f"{selected_session}.json")
                            os.remove(filepath)
                            st.success("Session deleted")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                
            except Exception as e:
                st.error(f"Error loading session: {e}")

# Footer
st.sidebar.divider()
st.sidebar.caption("Administrator Panel v1.0")
st.sidebar.caption("Manage models, database, and chat histories")