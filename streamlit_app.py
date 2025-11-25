import streamlit as st
from app.backend.ingestion import ingest_uploaded_files, clear_knowledge_base
from app.backend.rag import generate_test_cases, generate_selenium_script

# Page Config
st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif&family=Poppins:wght@400;600;700&display=swap');
    
    /* Main app background */
    .stApp {
        background-color: #090909;
        font-family: 'Poppins', sans-serif;
    }
    
    /* File uploader text */
    .uploadedFileName,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small,
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] div,
    section[data-testid="stFileUploadDropzone"] *,
    section[data-testid="stFileUploadDropzone"] span {
        color: #ffffff !important;
    }
    
    /* Limit width and left align file uploader */
    div[data-testid="stFileUploader"] {
        width: 60% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
    }
    
    /* Browse files button */
    button[kind="secondary"],
    [data-testid="stFileUploadDropzone"] button {
        background-color: #ffffff !important;
        color: #090909 !important;
        border: 2px solid #090909 !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* All text color */
    .stApp, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label {
        color: #D3FFE9 !important;
        font-family: 'Poppins', sans-serif;
        font-size: 16px !important;
    }
    
    /* Header sizes */
    h1 {
        font-size: 24px !important;
    }
    
    h2 {
        font-size: 18px !important;
    }
    
    /* Input fields */
    input, textarea, select {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #333 !important;
        font-family: 'Poppins', sans-serif;
        font-size: 14px !important;
        padding: 0.5rem !important;
        min-height: 0px !important;
    }
    
    /* Adjust container height for inputs */
    div[data-baseweb="input"] {
        min-height: 35px !important;
        height: 35px !important;
    }

    /* Limit width and left align input fields */
    div[data-testid="stTextInput"] {
        width: 60% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4b5043 !important;
        color: #ffffff !important;
        border: none;
        font-family: 'Poppins', sans-serif;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #3a3f35;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Success/Warning/Error messages */
    .stSuccess, .stWarning, .stError, [data-testid="stAlert"] {
        background-color: #8DDBE0 !important;
        color: #000000 !important;
        border-radius: 5px;
        padding: 10px;
        width: 40% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
    }
    
    [data-testid="stAlert"] * {
        color: #000000 !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #D3FFE9 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom styled title
st.markdown("""
    <h1 style="
        font-family: 'Poppins', sans-serif;
        font-size: 56px;
        text-align: center;
        color: #D3FFE9;
        font-weight: 600;
        margin-bottom: 10px;
    ">Autonomous QA Agent</h1>
""", unsafe_allow_html=True)

st.markdown("""
    <p style="
        font-size: 24px;
        text-align: center;
        color: #D3FFE9;
        margin-bottom: 30px;
    ">Generate Test Cases and Selenium Scripts from Documentation</p>
""", unsafe_allow_html=True)

# Configuration
st.header("Configuration")
api_key = st.text_input("Google Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Google Gemini API Key to proceed.")

# 1. Knowledge Base
st.header("1. Knowledge Base")
uploaded_files = st.file_uploader(
    "Upload Support Docs & HTML", 
    accept_multiple_files=True,
    type=['md', 'txt', 'json', 'html', 'pdf']
)

if st.button("Build Knowledge Base"):
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
                st.success(f"Success! Knowledge Base Built Successfully ({num_chunks} chunks)")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload files first.")

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
