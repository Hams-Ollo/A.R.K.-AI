import streamlit as st
import os
from datetime import datetime

st.set_page_config(
    page_title="Upload Documents - Research Assistant",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Upload Documents")

# File uploader
uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=['pdf'],
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("Document Details")
    
    for file in uploaded_files:
        with st.expander(f"📄 {file.name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title", file.name, key=f"title_{file.name}")
                author = st.text_input("Author", "", key=f"author_{file.name}")
            
            with col2:
                pub_date = st.date_input("Publication Date", None, key=f"date_{file.name}")
                doc_type = st.selectbox(
                    "Document Type",
                    ["Research Paper", "Book", "Article", "Report"],
                    key=f"type_{file.name}"
                )
    
    if st.button("Process Documents", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            # Save file temporarily
            temp_path = os.path.join("temp", file.name)
            os.makedirs("temp", exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {file.name}... ({i+1}/{len(uploaded_files)})")
            
            # Add to session state
            if 'uploaded_files' not in st.session_state:
                st.session_state.uploaded_files = []
            st.session_state.uploaded_files.append(file.name)
            
            # Clean up
            os.remove(temp_path)
        
        st.success("All documents processed successfully!")
        if st.button("Return to Home"):
            st.switch_page("Home.py")
