import requests
import time
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8000/api/'
AUTH_URL = BASE_URL + 'auth/'

def get_auth_token():
    payload = {"username": "testuser_week1", "password": "testpassword123"}
    try:
        response = requests.post(AUTH_URL + 'login/', data=payload)
        if response.status_code == 200:
            return response.json()['token']
    except Exception as e:
        print(f"Connection error: {e}")
        return None
    
    # Try Registering
    print("Login failed, trying to register...")
    reg_payload = {
        "username": "testuser_week1", 
        "email": "test@example.com", 
        "password": "testpassword123"
    }
    requests.post(AUTH_URL + 'register/', data=reg_payload)
    
    # Retry Login
    response = requests.post(AUTH_URL + 'login/', data=payload)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Final login failed: {response.text}")
        return None

def test_recurring():
    token = get_auth_token()
    if not token:
        return

    headers = {'Authorization': f'Token {token}'}
    print("\n--- Testing Recurring Tasks ---")

    # 1. Create Recurring Task
    print("\n1. Creating Recurring Task (Daily)...")
    due_date = (datetime.now() + timedelta(days=1)).isoformat()
    task_data = {
        "title": "Daily Standup",
        "due_date": due_date,
        "priority": "High",
        "is_recurring": True,
        "recurrence_interval": "Daily"
    }
    response = requests.post(BASE_URL + 'tasks/', data=task_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        print(response.text)
        return

    task_id = response.json()['id']
    print(f"Task Created: ID {task_id}")

    # 2. Mark as Complete
    print("\n2. Marking as Complete (should trigger recurrence)...")
    url = f"{BASE_URL}tasks/{task_id}/complete/"
    response = requests.post(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    # 3. Verify New Task Created
    print("\n3. Verifying New Task Creation...")
    time.sleep(1) # Give signal a moment
    response = requests.get(BASE_URL + 'tasks/', headers=headers)
    tasks = response.json()
    
    new_task_found = False
    for t in tasks:
        # Check for task with same title but status Pending and different ID
        if t['title'] == "Daily Standup" and t['id'] != task_id and t['status'] == 'Pending':
            print(f"New Task Found! ID: {t['id']}, Due: {t['due_date']}")
            new_task_found = True
            break
    
    if new_task_found:
        print("SUCCESS: Recurring task generated.")
    else:
        print("FAILURE: No new task found.")

if __name__ == "__main__":
    test_recurring()
