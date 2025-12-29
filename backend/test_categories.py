import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8000/api/'
AUTH_URL = BASE_URL + 'auth/'

def get_auth_token():
    payload = {"username": "testuser_week1", "password": "testpassword123"}
    try:
        response = requests.post(AUTH_URL + 'login/', data=payload)
        if response.status_code == 200:
            return response.json()['token']
    except:
        pass
    print("Login failed - ensure user exists or server is running")
    return None

def test_categories():
    token = get_auth_token()
    if not token:
        return

    headers = {'Authorization': f'Token {token}'}
    print("\n--- Testing Categories ---")

    # 1. Create Category
    print("\n1. Creating Category 'Work'...")
    cat_data = {"name": "Work"}
    response = requests.post(BASE_URL + 'categories/', data=cat_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 201:
        cat_id = response.json()['id']

        # 2. Create Task with Category
        print("\n2. Creating Task in 'Work'...")
        due_date = (datetime.now() + timedelta(days=3)).isoformat()
        task_data = {
            "title": "Categorized Task",
            "due_date": due_date,
            "category_id": cat_id,
            "priority": "High"
        }
        response = requests.post(BASE_URL + 'tasks/', data=task_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Task Category: {response.json().get('category')}")

        # 3. Filter by Category
        print("\n3. Filtering Tasks by Category...")
        response = requests.get(f"{BASE_URL}tasks/?category={cat_id}", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Count: {len(response.json())}")

    # 4. List Categories
    print("\n4. Listing Categories...")
    response = requests.get(BASE_URL + 'categories/', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Categories: {response.json()}")

if __name__ == "__main__":
    test_categories()
