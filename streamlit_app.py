import streamlit as st
from app.backend.ingestion import ingest_uploaded_files, clear_knowledge_base
from app.backend.rag import generate_test_cases, generate_selenium_script

# Page Config
st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("🤖 Autonomous QA Agent")
st.markdown("Generate Test Cases and Selenium Scripts from Documentation")

# Sidebar for Configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
if not api_key:
    st.sidebar.warning("Please enter your Google Gemini API Key to proceed.")

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
            try:
                # Clear existing knowledge base
                clear_knowledge_base()
                
                # Prepare files for ingestion
                file_data = [(file.name, file.getvalue()) for file in uploaded_files]
                
                # Store HTML content in session state for script generation
                html_content = None
                for file in uploaded_files:
                    if file.name.endswith('.html'):
                        html_content = file.getvalue().decode('utf-8')
                        st.session_state['html_content'] = html_content
                        break
                
                # Ingest documents
                num_chunks = ingest_uploaded_files(file_data)
                st.sidebar.success(f"Success! Knowledge Base Built Successfully ({num_chunks} chunks)")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please upload files first.")

# Main Area
st.header("2. Test Case Generation")

query = st.text_input("Enter a feature to test (e.g., 'Discount Code', 'Shipping')", "Discount Code")

if st.button("Generate Test Cases"):
    if not api_key:
        st.error("API Key is required!")
    else:
        with st.spinner("Analyzing documents..."):
            try:
                test_cases = generate_test_cases(query, api_key)
                st.session_state['test_cases'] = [tc.dict() for tc in test_cases]
                st.success(f"Generated {len(test_cases)} test cases.")
            except Exception as e:
                st.error(f"Error: {e}")

# Display Test Cases
if 'test_cases' in st.session_state and st.session_state['test_cases']:
    st.subheader("Generated Test Cases")
    
    # Create a list of labels for the radio button
    options = range(len(st.session_state['test_cases']))
    
    def format_option(i):
        tc = st.session_state['test_cases'][i]
        return f"{tc['test_id']}: {tc['scenario']}"
    
    selected_test_case_index = st.radio(
        "Select a test case to generate script for:",
        options,
        format_func=format_option
    )
    
    selected_case = st.session_state['test_cases'][selected_test_case_index]
    
    st.markdown("### Selected Test Case Details")
    st.json(selected_case)
    
    st.header("3. Selenium Script Generation")
    if st.button("Generate Selenium Script"):
        if not api_key:
            st.error("API Key is required!")
        else:
            with st.spinner("Generating script..."):
                try:
                    #Get HTML content from session state
                    html_content = st.session_state.get('html_content', '')
                    
                    if not html_content:
                        st.warning("No HTML file found. Please upload checkout.html when building the knowledge base.")
                    
                    # Convert selected_case dict back to TestCase object
                    from app.backend.models import TestCase
                    test_case_obj = TestCase(**selected_case)
                    
                    script_code = generate_selenium_script(test_case_obj, html_content, api_key)
                    st.code(script_code, language='python')
                except Exception as e:
                    st.error(f"Error: {e}")
