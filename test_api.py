import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY")

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Headers for API requests
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print(f"Health check status code: {response.status_code}")
    print(f"Health check response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


if __name__ == "__main__":
    print("Testing API...")
    test_health_check()
    print("All tests passed!")
