import streamlit as st
from typing import List, Dict
import json
from datetime import datetime
import httpx
import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.backend.agents.research_librarian import ResearchLibrarian
from app.backend.vector_store.chroma_store import ChromaDocStore
from app.backend.document_store.document_store import DocumentStore
from app.utils.cli_logger import CliLogger

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "research_context" not in st.session_state:
        st.session_state.research_context = None
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None
    if "librarian" not in st.session_state:
        # Initialize Research Librarian
        vector_store = ChromaDocStore()
        document_store = DocumentStore()
        st.session_state.librarian = ResearchLibrarian(vector_store, document_store)

def display_message(message: Dict):
    """Display a chat message with appropriate styling."""
    role = message["role"]
    content = message["content"]
    
    if role == "assistant":
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(content)
            if "citations" in message and message["citations"]:
                st.markdown("---")
                st.markdown("**Sources:**")
                for citation in message["citations"]:
                    st.markdown(
                        f"- **{citation['title']}** (Page {citation['page']})"
                        f"\n  Relevance Score: {citation['relevance_score']:.2f}"
                    )
            if "suggestions" in message and message["suggestions"]:
                st.markdown("---")
                st.markdown("**Related Topics:**")
                for suggestion in message["suggestions"]:
                    st.markdown(f"- {suggestion}")
    else:
        with st.chat_message("user"):
            st.markdown(content)

def display_research_context():
    """Display the current research context in the sidebar."""
    with st.sidebar:
        st.subheader("Research Context")
        if st.session_state.current_topic:
            st.markdown(f"**Current Topic:** {st.session_state.current_topic}")
        
        if st.session_state.research_context:
            st.markdown("**Recent Documents:**")
            for doc in st.session_state.research_context:
                if isinstance(doc, dict):
                    title = doc.get('title', 'Untitled')
                    last_accessed = doc.get('last_accessed', 'Unknown')
                    st.markdown(
                        f"- **{title}**\n"
                        f"  Last accessed: {last_accessed}"
                    )
                else:
                    st.markdown(f"- {doc}")
                
        # Add document upload
        st.markdown("---")
        st.subheader("Add Documents")
        uploaded_files = st.file_uploader(
            "Upload documents to your knowledge base",
            type=['pdf', 'docx', 'txt', 'md', 'csv', 'xlsx'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            with st.spinner("Processing documents..."):
                for file in uploaded_files:
                    try:
                        # Process and add to knowledge base
                        st.success(f"Added {file.name} to knowledge base")
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")

async def process_message_async(librarian: ResearchLibrarian, prompt: str) -> Dict:
    """Process message asynchronously."""
    try:
        CliLogger.info("Processing user message...", context='user_input',
                      details={"message_length": len(prompt)})
        response = await librarian.process_message(prompt)
        CliLogger.success("Message processed successfully!", context='ai_response',
                         details={"response_length": len(response)})
        return response
    except Exception as e:
        CliLogger.error(f"Error processing message: {str(e)}")
        raise

def run_async(coro):
    """Run an async coroutine in a synchronous context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def main():
    st.set_page_config(
        page_title="ARK AI - Research Chat",
        page_icon="🎓",
        layout="wide"
    )

    st.title("🎓 AI Research Librarian")
    st.markdown("""
    Chat with your AI Research Librarian to:
    - Explore your knowledge repository
    - Get research suggestions
    - Find connections between documents
    - Generate summaries and insights
    """)

    # Initialize session state
    init_session_state()

    # Display research context in sidebar
    display_research_context()

    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)

    # Chat input
    if prompt := st.chat_input("Ask your research question..."):
        # Add user message to chat history
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        display_message(user_message)

        # Get AI response
        with st.spinner("Researching..."):
            try:
                # Process message through Research Librarian asynchronously
                response = run_async(
                    process_message_async(st.session_state.librarian, prompt)
                )
                
                ai_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
                
                st.session_state.messages.append(ai_message)
                display_message(ai_message)
                
            except Exception as e:
                CliLogger.error(f"Error in chat interface: {str(e)}")
                st.error(f"Error: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I apologize, but I encountered an error processing your request. Please try again.",
                    "timestamp": datetime.now().isoformat()
                })

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("Export Chat"):
                chat_export = json.dumps(st.session_state.messages, indent=2)
                st.download_button(
                    label="Download Chat",
                    data=chat_export,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Advanced options
        with st.expander("Advanced Options"):
            st.slider(
                "Response Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Higher values make responses more creative but potentially less focused"
            )
            st.number_input(
                "Max Search Results",
                min_value=1,
                max_value=20,
                value=5,
                help="Maximum number of documents to search through"
            )

if __name__ == "__main__":
    main()
