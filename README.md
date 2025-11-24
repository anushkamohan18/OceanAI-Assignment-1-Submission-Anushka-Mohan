# Autonomous QA Agent

## Objective
This project implements an intelligent, autonomous QA agent capable of constructing a "testing brain" from project documentation. It ingests support documents (specs, UI/UX guides) and HTML structure to generate comprehensive test cases and executable Selenium scripts.

## Features
- **Knowledge Base Ingestion**: Parses PDF, Markdown, TXT, JSON, and HTML files.
- **RAG Pipeline**: Uses ChromaDB for vector storage and Google Gemini for reasoning.
- **Test Case Generation**: Generates grounded test cases based on uploaded documents.
- **Selenium Script Generation**: Converts test cases into runnable Python Selenium scripts.
- **Single-Page UI**: Built with Streamlit for easy interaction.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Google Gemini API Key (Free tier available)

### Installation
1. Clone the repository.
2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
The application is designed to run with a single command. The Streamlit frontend integrates directly with the FastAPI backend functions.

```bash
streamlit run streamlit_app.py
```

- **Frontend**: http://localhost:8501

**Note**: The FastAPI backend structure is maintained for compliance with assignment requirements. To run the FastAPI server separately (optional), use:
```bash
cd app/backend && uvicorn main:app --reload
```
- **Backend API Docs**: http://localhost:8000/docs

## Usage Examples
1. **Enter API Key**: Input your Google Gemini API Key in the sidebar.
2. **Upload Documents**:
   - Navigate to the `data/` folder.
   - Upload `product_specs.md`, `ui_ux_guide.txt`, `api_endpoints.json`, and `checkout.html`.
3. **Build Knowledge Base**: Click the "Build Knowledge Base" button.
4. **Generate Test Cases**:
   - Enter a feature name (e.g., "Discount Code").
   - Click "Generate Test Cases".
5. **Generate Script**:
   - Select a generated test case.
   - Click "Generate Selenium Script".
   - Copy the generated code and run it locally.

## Included Support Documents (`data/`)
- `checkout.html`: The target web application for testing.
- `product_specs.md`: Defines business rules (discounts, shipping costs).
- `ui_ux_guide.txt`: Defines UI requirements (error messages, button colors).
- `api_endpoints.json`: Mock API definitions.

## Project Structure
- `app/backend/`: FastAPI backend logic (Ingestion, RAG, Models).
- `streamlit_app.py`: Streamlit frontend.
- `data/`: Sample assets.
