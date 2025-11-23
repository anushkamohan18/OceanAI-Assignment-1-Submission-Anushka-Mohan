from typing import List
from .models import TestCase, TestPlan
from .ingestion import get_knowledge_base
import json

# Mock LLM response generator
def query_llm(prompt: str, context: str) -> str:
    """
    Simulates an LLM response based on the prompt and context.
    """
    if "test cases" in prompt.lower():
        return """
        [
            {
                "test_id": "TC-001",
                "feature": "Discount Code",
                "scenario": "Apply valid discount code 'SAVE15'",
                "expected_result": "Total price reduced by 15%",
                "grounded_in": "product_specs.md"
            },
            {
                "test_id": "TC-002",
                "feature": "Shipping Method",
                "scenario": "Select Express Shipping",
                "expected_result": "Shipping cost becomes $10.00",
                "grounded_in": "product_specs.md"
            },
             {
                "test_id": "TC-003",
                "feature": "Form Validation",
                "scenario": "Submit empty form",
                "expected_result": "Error messages displayed for Name, Email, Address",
                "grounded_in": "ui_ux_guide.txt"
            },
            {
                "test_id": "TC-004",
                "feature": "Payment",
                "scenario": "Select PayPal",
                "expected_result": "Payment method updates to PayPal",
                "grounded_in": "product_specs.md"
            }
        ]
        """
    elif "selenium script" in prompt.lower():
        return """
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_scenario():
    # Setup Driver
    driver = webdriver.Chrome()
    try:
        # Navigate to page (Assuming local file for demo)
        driver.get("file:///C:/Users/anush/Documents/oceanai/data/checkout.html")
        
        # Maximize window
        driver.maximize_window()
        time.sleep(1)
        
        # Example interaction based on context
        # Locate discount input
        discount_input = driver.find_element(By.ID, "discountCode")
        discount_input.send_keys("SAVE15")
        
        # Click apply button
        apply_btn = driver.find_element(By.ID, "applyDiscount")
        apply_btn.click()
        
        # Verify success message
        success_msg = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.ID, "discountMessage"))
        )
        assert "15% Discount Applied" in success_msg.text
        print("Test Passed!")
        
    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_scenario()
        """
    return "[]"

def generate_test_cases(query: str) -> List[TestCase]:
    kb = get_knowledge_base()
    # Simple retrieval: get all content (since it's small) or keyword match
    # For this demo, we just dump everything as context
    context = "\n\n".join([item["content"] for item in kb])
    
    prompt = f"Generate test cases for: {query}\nContext: {context[:5000]}" # Limit context size
    
    response_text = query_llm(prompt, context)
    try:
        data = json.loads(response_text)
        return [TestCase(**item) for item in data]
    except:
        return []

def generate_selenium_script(test_case: TestCase, html_content: str) -> str:
    kb = get_knowledge_base()
    context = "\n\n".join([item["content"] for item in kb])
    
    prompt = f"""
    Generate a Selenium Python script for:
    Test Case: {test_case.scenario}
    Expected Result: {test_case.expected_result}
    HTML Content: {html_content[:1000]}...
    Context: {context[:2000]}
    """
    
    return query_llm("Generate selenium script", context)
