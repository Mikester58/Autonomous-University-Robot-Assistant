"""
User Interface (Jetson Nano)
"""

#python -m streamlit run user.py

import streamlit as st
import os
import json
from langchain_ollama import ChatOllama

from database_bridge import InitializeDatabase, SaveSession, ClearCudaCache
from lightrag import LightRAG
from config import DEFAULT_EMBEDDING_MODEL, DEFAULT_DOCS_PATH, CHROMA_DIR, LLM_TEMPERATURE, LLM_TOP_P, LLM_MAX_TOKENS

st.set_page_config(page_title="AURA Assistant", layout="wide")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "user_" + os.urandom(4).hex()
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None

st.title("ECEN 214 Lab Assistant")

# --- System Init ---
if st.session_state.rag_system is None:
    # Check if database exists (transferred from Admin)
    if os.path.isdir(CHROMA_DIR) and len(os.listdir(CHROMA_DIR)) > 0:
        with st.spinner("Initializing System..."):
            try:
                # 1. Load DB (Read-only mode essentially)
                db = InitializeDatabase(
                    DEFAULT_EMBEDDING_MODEL, 
                    DEFAULT_DOCS_PATH, 
                    force_reload=False
                )
                
                # 2. Init LLM
                llm = ChatOllama(
                    model="llama3.2:3b", # Hardcoded for Jetson stability
                    temperature=LLM_TEMPERATURE,
                    top_p=LLM_TOP_P,
                    num_predict=LLM_MAX_TOKENS,
                    keep_alive="1h"
                )
                
                st.session_state.rag_system = LightRAG(llm, db)
                ClearCudaCache()
                
            except Exception as e:
                st.error(f"Startup Error: {e}")
    else:
        st.error(f"Database not found at {CHROMA_DIR}.")
        st.info("Please transfer 'chroma_db.zip' from the Admin console and extract it to 'storage/chroma'.")

# --- Chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]: st.caption(s)

if prompt := st.chat_input("Ask a question..."):
    if not st.session_state.rag_system:
        st.error("System not initialized.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.rag_system.generate(prompt)
                st.write(result["answer"])
                
                if result.get("evidence"):
                    with st.expander("View Evidence"):
                        for ev in result["evidence"]:
                            st.caption(f"{ev['source']} ({ev['retrieval_score']:.2f})")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })
                
                SaveSession({
                    "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                }, st.session_state.session_id)
                
            except Exception as e:
                st.error(f"Error: {e}")