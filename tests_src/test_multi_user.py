import requests
import time

BASE_URL = "http://localhost:8000"

def test_multi_user_isolation():
    print("--- Testing Multi-User Isolation ---")

    user_a = "alice"
    user_b = "bob"

    # 1. User A introduces herself
    print(f"\n1. {user_a} says 'My name is Alice'...")
    try:
        resp = requests.post(f"{BASE_URL}/chat", json={"user_query": "My name is Alice", "user_id": user_a})
        print(f"Alice's Response: {resp.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. User B introduces himself
    print(f"\n2. {user_b} says 'My name is Bob'...")
    resp = requests.post(f"{BASE_URL}/chat", json={"user_query": "My name is Bob", "user_id": user_b})
    print(f"Bob's Response: {resp.json()}")

    # 3. Ask User A "What is my name?"
    print(f"\n3. Asking {user_a}: 'What is my name?'")
    resp = requests.post(f"{BASE_URL}/chat", json={"user_query": "What is my name?", "user_id": user_a})
    ans_a = resp.json()["response"]
    print(f"Alice's Answer: {ans_a}")
    
    # Verify Alice's session knows Alice
    if "Alice" in ans_a:
        print("✅ Alice's session correctly remembers Alice.")
    else:
        print("❌ Alice's session forgot Alice!")

    # 4. Ask User B "What is my name?"
    print(f"\n4. Asking {user_b}: 'What is my name?'")
    resp = requests.post(f"{BASE_URL}/chat", json={"user_query": "What is my name?", "user_id": user_b})
    ans_b = resp.json()["response"]
    print(f"Bob's Answer: {ans_b}")

    # Verify Bob's session knows Bob and NOT Alice
    if "Bob" in ans_b and "Alice" not in ans_b:
        print("✅ Bob's session correctly remembers Bob and NOT Alice.")
    else:
        print("❌ Bob's session is confused!")

    # 5. Save Alice's chat
    print(f"\n5. Saving {user_a}'s chat...")
    resp = requests.post(f"{BASE_URL}/chat/save", json={"user_id": user_a})
    print(f"Save Result: {resp.json()}")
    assert resp.json()["status"] == "saved"

    # 6. Check Alice's History
    print(f"\n6. Checking {user_a}'s history...")
    resp = requests.get(f"{BASE_URL}/chat/history", params={"user_id": user_a})
    hist_a = resp.json()["sessions"]
    print(f"Alice's History: {len(hist_a)} sessions")
    assert len(hist_a) > 0

    # 7. Check Bob's History (should be empty if we didn't save Bob)
    print(f"\n7. Checking {user_b}'s history...")
    resp = requests.get(f"{BASE_URL}/chat/history", params={"user_id": user_b})
    hist_b = resp.json()["sessions"]
    print(f"Bob's History: {len(hist_b)} sessions")
    # Note: Bob might have history from previous runs if we reused the DB, but for this run we only saved Alice.
    # If DB was empty, Bob should have 0.

if __name__ == "__main__":
    print("Make sure 'uvicorn app.api_server:app' is running!")
    time.sleep(1)
    test_multi_user_isolation()
