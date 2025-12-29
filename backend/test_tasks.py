import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8000/api/'
AUTH_URL = BASE_URL + 'auth/'

def get_auth_token():
    # Login to get token
    payload = {
        "username": "testuser_week1",
        "password": "testpassword123"
    }
    response = requests.post(AUTH_URL + 'login/', data=payload)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print("Login failed, trying to register...")
        # Register if login fails (maybe db was reset)
        reg_payload = {
            "username": "testuser_week1",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        requests.post(AUTH_URL + 'register/', data=reg_payload)
        return get_auth_token()

def test_task_crud():
    token = get_auth_token()
    headers = {'Authorization': f'Token {token}'}
    
    print("\n--- Testing Task CRUD ---")
    
    # 1. Create Task
    print("\n1. Creating Task...")
    due_date = (datetime.now() + timedelta(days=7)).isoformat()
    task_data = {
        "title": "Finish Week 2",
        "description": "Implement CRUD for tasks",
        "due_date": due_date,
        "priority": "High"
    }
    response = requests.post(BASE_URL + 'tasks/', data=task_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        task_id = response.json()['id']
        
        # 2. List Tasks
        print("\n2. Listing Tasks...")
        response = requests.get(BASE_URL + 'tasks/', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Count: {len(response.json())}")
        
        # 3. Update Task
        print("\n3. Updating Task...")
        update_data = {"status": "Completed"}
        response = requests.patch(f"{BASE_URL}tasks/{task_id}/", data=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"New Status: {response.json().get('status')}")
        
        # 4. Delete Task
        print("\n4. Deleting Task...")
        response = requests.delete(f"{BASE_URL}tasks/{task_id}/", headers=headers)
        print(f"Status: {response.status_code}")
        
        # Verify Delete
        response = requests.get(f"{BASE_URL}tasks/{task_id}/", headers=headers)
        print(f"Get Deleted Task Status: {response.status_code}") # Should be 404

if __name__ == "__main__":
    test_task_crud()
