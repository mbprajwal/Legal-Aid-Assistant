import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000"

def test_signup_login():
    # Generate a random email to avoid conflicts
    random_id = str(uuid.uuid4())[:8]
    email = f"test_{random_id}@example.com"
    password = "password123"

    print(f"Testing with email: {email}")

    # 1. Test Signup
    print("\n--- Testing Signup ---")
    signup_payload = {"email": email, "password": password}
    try:
        response = requests.post(f"{BASE_URL}/signup", json=signup_payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
             print(f"Error: {response.text}")
        else:
             print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Signup failed: {e}")

    # 2. Test Login
    print("\n--- Testing Login ---")
    login_payload = {"email": email, "password": password}
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
             print(f"Error: {response.text}")
        else:
             print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Login failed: {e}")

    # 3. Test Invalid Login
    print("\n--- Testing Invalid Login ---")
    invalid_payload = {"email": email, "password": "wrongpassword"}
    try:
        response = requests.post(f"{BASE_URL}/login", json=invalid_payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
             print(f"Error: {response.text}")
        else:
             print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Invalid Login failed: {e}")

    # 4. Test Invalid Email Format
    print("\n--- Testing Invalid Email ---")
    invalid_email_payload = {"email": "notanemail", "password": "password123"}
    try:
        response = requests.post(f"{BASE_URL}/signup", json=invalid_email_payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
             print(f"Error: {response.text}")
        else:
             print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Invalid Email failed: {e}")

if __name__ == "__main__":
    # Wait a bit for the server to start if running immediately after spawn
    time.sleep(2)
    test_signup_login()
