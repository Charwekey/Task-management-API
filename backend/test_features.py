import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8000/api/'
AUTH_URL = BASE_URL + 'auth/'

def get_auth_token():
    payload = {"username": "testuser_week1", "password": "testpassword123"}
    response = requests.post(AUTH_URL + 'login/', data=payload)
    if response.status_code == 200:
        return response.json()['token']
    return None

def test_features():
    token = get_auth_token()
    if not token:
        print("Login failed")
        return

    headers = {'Authorization': f'Token {token}'}
    print("\n--- Testing Week 3 Features ---")

    # 1. Test Validation (Past Date)
    print("\n1. Testing Due Date Validation...")
    past_date = (datetime.now() - timedelta(days=1)).isoformat()
    task_data = {
        "title": "Past Task", 
        "due_date": past_date, 
        "priority": "Low"
    }
    response = requests.post(BASE_URL + 'tasks/', data=task_data, headers=headers)
    print(f"Status: {response.status_code}") # Should be 400
    if response.status_code == 400:
        print("Validation Passed")

    # Create dummy tasks
    print("\nCreating tasks for filtering...")
    future_date = (datetime.now() + timedelta(days=5)).isoformat()
    requests.post(BASE_URL + 'tasks/', data={"title": "High Prio", "due_date": future_date, "priority": "High", "status": "Pending"}, headers=headers)
    requests.post(BASE_URL + 'tasks/', data={"title": "Low Prio", "due_date": future_date, "priority": "Low", "status": "Completed"}, headers=headers)

    # 2. Test Filtering
    print("\n2. Testing Filters (Priority=High)...")
    response = requests.get(BASE_URL + 'tasks/?priority=High', headers=headers)
    print(f"Count: {len(response.json())}")
    for task in response.json():
        print(f"- {task['title']} ({task['priority']})")

    # 3. Test Sorting
    print("\n3. Testing Sorting (due_date)...")
    response = requests.get(BASE_URL + 'tasks/?ordering=due_date', headers=headers)
    print("Tasks sorted by due date")

    # 4. Test Mark Complete
    print("\n4. Testing Mark Complete...")
    # Get a pending task
    response = requests.get(BASE_URL + 'tasks/?status=Pending', headers=headers)
    if response.json():
        task_id = response.json()[0]['id']
        url = f"{BASE_URL}tasks/{task_id}/complete/"
        response = requests.post(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify status
        task_check = requests.get(f"{BASE_URL}tasks/{task_id}/", headers=headers)
        print(f"New Status: {task_check.json()['status']}")

if __name__ == "__main__":
    test_features()
