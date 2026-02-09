"""
User Interface for ECEN 214 Lab Assistant
Simple chat interface using LightRAG only
"""

import streamlit as st
import os
import json
from langchain_ollama import ChatOllama

from database_bridge import InitializeDatabase, SaveSession, ClearCudaCache
from lightrag import LightRAG
from config import DEFAULT_EMBEDDING_MODEL, DEFAULT_DOCS_PATH, CHROMA_DIR, LLM_TEMPERATURE, LLM_TOP_P, LLM_MAX_TOKENS

st.set_page_config(page_title="ECEN 214 Lab Assistant", layout="centered")

# Load active model from admin config
config_file = "active_model.json"
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
        active_model = config.get("model", "tinyllama")
else:
    active_model = "tinyllama"

st.title("ECEN 214 Lab Assistant")
st.caption(f"Model: {active_model}")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if "session_id" not in st.session_state:
    st.session_state.session_id = "user_session"

# Load database
if "db" not in st.session_state:
    if os.path.isdir(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        try:
            with st.spinner("Loading knowledge base..."):
                st.session_state.db = InitializeDatabase(
                    DEFAULT_EMBEDDING_MODEL,
                    DEFAULT_DOCS_PATH,
                    force_reload=False
                )
        except Exception as e:
            st.error(f"Error loading database: {e}")
            st.session_state.db = None
    else:
        st.session_state.db = None

# Initialize LLM
if "llm" not in st.session_state:
    st.session_state.llm = ChatOllama(
        model=active_model,
        temperature=LLM_TEMPERATURE,
        top_p=LLM_TOP_P,
        num_predict=LLM_MAX_TOKENS
    )

# Initialize LightRAG
if "lightrag" not in st.session_state and st.session_state.db:
    st.session_state.lightrag = LightRAG(
        st.session_state.llm,
        st.session_state.db
    )

# Main chat interface
if st.session_state.db is None:
    st.error("Knowledge base not available")
    st.info("Contact administrator to build the database")
else:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            if "sources" in msg and msg["sources"]:
                with st.expander("View Sources"):
                    for source in msg["sources"]:
                        st.caption(source)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the lab"):
        # Auto-clear cache periodically
        st.session_state.query_count += 1
        if st.session_state.query_count % 5 == 0:
            ClearCudaCache()
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response using LightRAG
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.lightrag.generate(prompt)
                    response_text = result["answer"]
                    
                    st.write(response_text)
                    
                    # Show evidence
                    if result["evidence"]:
                        with st.expander("Evidence Used"):
                            for ev in result["evidence"][:3]:
                                st.caption(f"[{ev['id']}] {ev['source']} (Page {ev['page']}) - Relevance: {ev['retrieval_score']:.2f}")
                    
                    # Collect sources
                    sources = result["sources"]
                    
                    if sources:
                        with st.expander("View Sources"):
                            for source in sources:
                                st.caption(source)
                    
                    # Save to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sources": sources
                    })
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    response_text = "I encountered an error processing your question."
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sources": []
                    })

# Auto-save session after page load (if messages exist)
if st.session_state.messages:
    try:
        session_data = {
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in st.session_state.messages
            ]
        }
        SaveSession(session_data, st.session_state.session_id)
    except:
        pass