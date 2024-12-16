#-------------------------------------------------------------------------------------#
# frontend/Home.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run Home.py / streamlit run app/frontend/Home.py
#
# Git Commands:
# 1. Initialize repository -> git init
# 2. Add files to staging -> git add .
# 3. Commit changes -> git commit -m "your message"
# 4. Create new branch -> git checkout -b branch-name
# 5. Switch branches -> git checkout branch-name
# 6. Push to remote -> git push -u origin branch-name
# 7. Pull latest changes -> git pull origin branch-name
# 8. Check status -> git status
# 9. View commit history -> git log
#-------------------------------------------------------------------------------------#


import streamlit as st
import os
from datetime import datetime

st.set_page_config(
    page_title="Research Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Research Assistant")
st.subheader("Bhaktivedanta Institute Knowledge Base")

# Session state initialization
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Main dashboard stats
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Documents", value=len(st.session_state.uploaded_files))

with col2:
    st.metric(label="Recent Uploads", value="0")

with col3:
    st.metric(label="Recent Queries", value="0")

# Recent Activity
st.subheader("Recent Activity")
if not st.session_state.uploaded_files:
    st.info("No recent activity to display. Start by uploading documents or making queries!")
else:
    for file in st.session_state.uploaded_files[-5:]:
        st.text(f"📄 {file} uploaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Quick Actions
st.subheader("Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("📤 Upload Documents", use_container_width=True):
        st.switch_page("pages/upload.py")

with col2:
    if st.button("🔍 Search Knowledge Base", use_container_width=True):
        st.switch_page("pages/search.py")
