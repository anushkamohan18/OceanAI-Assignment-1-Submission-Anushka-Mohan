# Autonomous QA Agent

## Setup Instructions

1. **Prerequisites**: Python 3.9+
2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

The application consists of a FastAPI backend and a Streamlit frontend.

1. **Start Backend**:
   ```bash
   uvicorn app.backend.main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```bash
   streamlit run app/frontend/ui.py
   ```

## Usage

1. Open the Streamlit UI (usually http://localhost:8501).
2. Upload `checkout.html` and support documents (`product_specs.md`, etc.) from the `data/` folder.
3. Click "Build Knowledge Base".
4. Use the "Test Case Agent" tab to generate test cases (e.g., "Generate test cases for discount code").
5. Select a test case and click "Generate Selenium Script".

## Technical Implementation
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Knowledge Base**: Lightweight in-memory vector storage for demonstration stability.
- **RAG Pipeline**: Custom implementation for context retrieval and prompt engineering.

## Support Documents
- `product_specs.md`: Business rules.
- `ui_ux_guide.txt`: Visual requirements.
- `api_endpoints.json`: Mock API definitions.
