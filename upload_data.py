import requests

API_URL = "http://localhost:8000"
FILES = [
    'data/checkout.html',
    'data/product_specs.md',
    'data/ui_ux_guide.txt',
    'data/api_endpoints.json'
]

def upload():
    files_to_send = []
    opened_files = []
    try:
        for f_path in FILES:
            f = open(f_path, 'rb')
            opened_files.append(f)
            files_to_send.append(('files', (f_path.split('/')[-1], f)))
        
        print("Uploading files...")
        resp = requests.post(f"{API_URL}/upload_files", files=files_to_send)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for f in opened_files:
            f.close()

if __name__ == "__main__":
    upload()
