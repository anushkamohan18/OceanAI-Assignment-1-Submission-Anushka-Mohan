import requests
import os
import time
import subprocess
import sys

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Starting backend...")
    # Start backend in a subprocess
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.backend.main:app", "--port", "8000"], 
                            cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server to start
        time.sleep(5)
        
        print("Testing /upload_files...")
        files = [
            ('files', ('product_specs.md', open('data/product_specs.md', 'rb'), 'text/markdown')),
            ('files', ('checkout.html', open('data/checkout.html', 'rb'), 'text/html'))
        ]
        resp = requests.post(f"{BASE_URL}/upload_files", files=files)
        print(f"Upload Status: {resp.status_code}")
        print(f"Upload Response: {resp.json()}")
        assert resp.status_code == 200
        
        print("\nTesting /generate_test_cases...")
        resp = requests.post(f"{BASE_URL}/generate_test_cases", json={"query": "Discount Code"})
        print(f"Test Cases Status: {resp.status_code}")
        data = resp.json()
        print(f"Generated {len(data)} test cases")
        assert len(data) > 0
        assert data[0]['feature'] == "Discount Code"
        
        print("\nTesting /generate_script...")
        test_case = data[0]
        resp = requests.post(f"{BASE_URL}/generate_script", json={
            "test_case": test_case,
            "html_content": None
        })
        print(f"Script Status: {resp.status_code}")
        script_data = resp.json()
        print("Script generated successfully")
        assert "selenium" in script_data['script_code']
        
        print("\nALL TESTS PASSED!")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        # Print server output if failed
        outs, errs = proc.communicate(timeout=1)
        print("Server Output:", outs.decode())
        print("Server Errors:", errs.decode())
        
    finally:
        print("Stopping backend...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_backend()
