import streamlit as st
from typing import List, Dict
import json
from datetime import datetime

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "research_context" not in st.session_state:
        st.session_state.research_context = None
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None

def display_message(message: Dict):
    """Display a chat message with appropriate styling."""
    role = message["role"]
    content = message["content"]
    
    if role == "assistant":
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(content)
            if "citations" in message:
                st.markdown("---")
                st.markdown("**Sources:**")
                for citation in message["citations"]:
                    st.markdown(f"- {citation}")
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
            st.markdown("**Key Documents:**")
            for doc in st.session_state.research_context:
                st.markdown(f"- {doc['title']}")

def main():
    st.set_page_config(
        page_title="Research Assistant - Chat",
        page_icon="🎓",
        layout="wide"
    )

    st.title("🎓 Research Librarian Chat")
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
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        display_message({"role": "user", "content": prompt})

        # Get AI response
        with st.spinner("Researching..."):
            # Here we'll integrate with the ResearchLibrarian agent
            # This is a placeholder for now
            response = {
                "role": "assistant",
                "content": "This is a placeholder response. The AI Research Librarian will be integrated here.",
                "citations": ["Sample Citation 1", "Sample Citation 2"],
                "timestamp": datetime.now().isoformat()
            }
            
            st.session_state.messages.append(response)
            display_message(response)

    # Sidebar controls
    with st.sidebar:
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("Export Chat"):
            chat_export = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="Download Chat History",
                data=chat_export,
                file_name="research_chat_export.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
