import streamlit as st
import requests
import json

# Backend API URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

st.title("🤖 Autonomous QA Agent")
st.markdown("Generate Test Cases and Selenium Scripts from Documentation")

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
            files = [('files', (file.name, file, file.type)) for file in uploaded_files]
            try:
                response = requests.post(f"{API_URL}/upload_files", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.sidebar.success(f"Success! Processed {data['chunks_processed']} chunks.")
                else:
                    st.sidebar.error(f"Error: {response.text}")
            except Exception as e:
                st.sidebar.error(f"Connection Error: {e}")
    else:
        st.sidebar.warning("Please upload files first.")

# Main Area
st.header("2. Test Case Generation")

query = st.text_input("Enter a feature to test (e.g., 'Discount Code', 'Shipping')", "Discount Code")

if st.button("Generate Test Cases"):
    with st.spinner("Analyzing documents..."):
        try:
            payload = {"query": query}
            response = requests.post(f"{API_URL}/generate_test_cases", json=payload)
            if response.status_code == 200:
                test_cases = response.json()
                st.session_state['test_cases'] = test_cases
                st.success(f"Generated {len(test_cases)} test cases.")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# Display Test Cases
if 'test_cases' in st.session_state and st.session_state['test_cases']:
    st.subheader("Generated Test Cases")
    
    # Convert to list of dicts for display if needed, or just use as is
    # st.table(st.session_state['test_cases'])
    
    selected_test_case_index = st.radio(
        "Select a test case to generate script for:",
        range(len(st.session_state['test_cases'])),
        format_func=lambda i: f"{st.session_state['test_cases'][i]['test_id']}: {st.session_state['test_cases'][i]['scenario']}"
    )
    
    selected_case = st.session_state['test_cases'][selected_test_case_index]
    
    st.markdown("### Selected Test Case Details")
    st.json(selected_case)
    
    st.header("3. Selenium Script Generation")
    if st.button("Generate Selenium Script"):
        with st.spinner("Generating script..."):
            try:
                payload = {
                    "test_case": selected_case,
                    "html_content": None # Backend will pick up uploaded HTML
                }
                response = requests.post(f"{API_URL}/generate_script", json=payload)
                if response.status_code == 200:
                    script_code = response.json()['script_code']
                    st.code(script_code, language='python')
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

