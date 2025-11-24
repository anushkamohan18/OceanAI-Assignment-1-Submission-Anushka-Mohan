from typing import List
from .models import TestCase
from .ingestion import get_knowledge_base
import google.generativeai as genai
import json
import os

def retrieve_context(query: str, n_results: int = 5) -> str:
    """Retrieves relevant context from ChromaDB."""
    collection = get_knowledge_base()
    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        if results and results['documents']:
            return "\n\n".join(results['documents'][0])
    except Exception as e:
        print(f"Error retrieving context: {e}")
    return ""

def generate_test_cases(query: str, api_key: str) -> List[TestCase]:
    if not api_key:
        raise ValueError("API Key is required")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    context = retrieve_context(query)
    
    prompt = f"""
    You are an expert QA Automation Engineer. 
    Your task is to generate comprehensive test cases for the following feature: "{query}".
    
    Strictly base your test cases on the provided context. Do not hallucinate features not mentioned in the context.
    
    Context:
    {context}
    
    Return the response ONLY as a JSON array of objects with the following keys:
    - test_id (e.g., TC-001)
    - feature (The feature being tested)
    - scenario (The test scenario)
    - expected_result (The expected outcome)
    - grounded_in (The source document filename where this rule is found, if available in context)
    
    JSON Output:
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean up code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return [TestCase(**item) for item in data]
    except Exception as e:
        print(f"Error generating test cases: {e}")
        return []

def generate_selenium_script(test_case: TestCase, html_content: str, api_key: str) -> str:
    if not api_key:
        raise ValueError("API Key is required")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Retrieve context again to ensure we have specific details if needed
    context = retrieve_context(test_case.scenario)
    
    prompt = f"""
    You are an expert Selenium Automation Engineer.
    Generate a robust, executable Python Selenium script for the following test case.
    
    Test Case: {test_case.scenario}
    Expected Result: {test_case.expected_result}
    
    HTML Structure (Target Page):
    {html_content}
    
    Additional Context/Rules:
    {context}
    
    Requirements:
    1. Use `selenium` webdriver (assume Chrome).
    2. Use explicit waits (`WebDriverWait`) for stability.
    3. Use precise selectors based on the provided HTML (IDs, Classes, etc.).
    4. Include assertions to verify the Expected Result.
    5. Return ONLY the Python code. No markdown formatting, no explanations.
    6. Handle potential errors (try/except).
    7. Ensure the script is complete and runnable.
    
    Python Code:
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean up code blocks
        if text.startswith("```python"):
            text = text[9:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    except Exception as e:
        return f"# Error generating script: {e}"
