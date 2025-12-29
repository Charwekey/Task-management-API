import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/auth/'

def test_register():
    print("Testing Registration...")
    payload = {
        "username": "testuser_week1",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    try:
        response = requests.post(BASE_URL + 'register/', data=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_login():
    print("\nTesting Login...")
    payload = {
        "username": "testuser_week1",
        "password": "testpassword123"
    }
    try:
        response = requests.post(BASE_URL + 'login/', data=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
    test_login()
