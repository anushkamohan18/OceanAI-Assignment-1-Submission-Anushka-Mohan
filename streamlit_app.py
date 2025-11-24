import streamlit as st
import os
import shutil
from app.backend.ingestion import ingest_documents, clear_knowledge_base
from app.backend.rag import generate_test_cases, generate_selenium_script
from app.backend.models import TestCase

# Page Config
st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("🤖 Autonomous QA Agent")
st.markdown("Generate Test Cases and Selenium Scripts from Documentation")

# Setup Temp Dir for Uploads
UPLOAD_DIR = "temp_uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Sidebar for File Upload
st.sidebar.header("1. Knowledge Base")
uploaded_files = st.sidebar.file_uploader(
    "Upload Support Docs & HTML", 
    accept_multiple_files=True,
    type=['md', 'txt', 'json', 'html', 'pdf']
)

if st.sidebar.button("Build Knowledge Base"):
    if uploaded_files:
        with st.spinner("Building Knowledge Base..."):
            # Clear previous
            clear_knowledge_base()
            for f in os.listdir(UPLOAD_DIR):
                os.remove(os.path.join(UPLOAD_DIR, f))
            
            # Save files
            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
            
            # Ingest
            try:
                num_chunks = ingest_documents(file_paths)
                st.sidebar.success(f"Success! Processed {num_chunks} chunks.")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please upload files first.")

# Main Area
st.header("2. Test Case Generation")

query = st.text_input("Enter a feature to test (e.g., 'Discount Code', 'Shipping')", "Discount Code")

if st.button("Generate Test Cases"):
    with st.spinner("Analyzing documents..."):
        try:
            test_cases = generate_test_cases(query)
            # Convert Pydantic models to dicts for session state
            st.session_state['test_cases'] = [tc.dict() for tc in test_cases]
            st.success(f"Generated {len(test_cases)} test cases.")
        except Exception as e:
            st.error(f"Error: {e}")

# Display Test Cases
if 'test_cases' in st.session_state and st.session_state['test_cases']:
    st.subheader("Generated Test Cases")
    
    selected_test_case_index = st.radio(
        "Select a test case to generate script for:",
        range(len(st.session_state['test_cases'])),
        format_func=lambda i: f"{st.session_state['test_cases'][i]['test_id']}: {st.session_state['test_cases'][i]['scenario']}"
    )
    
    selected_case_dict = st.session_state['test_cases'][selected_test_case_index]
    selected_case = TestCase(**selected_case_dict)
    
    st.markdown("### Selected Test Case Details")
    st.json(selected_case_dict)
    
    st.header("3. Selenium Script Generation")
    if st.button("Generate Selenium Script"):
        with st.spinner("Generating script..."):
            try:
                # Find HTML content
                html_content = ""
                for f in os.listdir(UPLOAD_DIR):
                    if f.endswith(".html"):
                        with open(os.path.join(UPLOAD_DIR, f), "r", encoding="utf-8") as file:
                            html_content = file.read()
                        break
                
                script_code = generate_selenium_script(selected_case, html_content)
                st.code(script_code, language='python')
            except Exception as e:
                st.error(f"Error: {e}")
