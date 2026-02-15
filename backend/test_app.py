from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

try:
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
