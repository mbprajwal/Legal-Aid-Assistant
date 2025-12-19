import requests
import time

BASE_URL = "http://localhost:8000"

def test_chat_history_flow():
    print("--- Testing Chat History Flow ---")

    # 1. Send a chat message (to populate memory)
    print("\n1. Sending chat message...")
    try:
        resp = requests.post(f"{BASE_URL}/chat", json={"user_query": "My name is Alice and I have a legal question."})
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Failed to connect to API: {e}")
        return

    # 2. Save the chat
    print("\n2. Saving chat session...")
    resp = requests.post(f"{BASE_URL}/chat/save", json={"user_id": "test_user_1"})
    print(f"Save Result: {resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "saved"

    # 3. Retrieve history
    print("\n3. Retrieving history...")
    resp = requests.get(f"{BASE_URL}/chat/history", params={"user_id": "test_user_1"})
    history = resp.json()["sessions"]
    print(f"History: {history}")
    assert len(history) > 0
    print("✅ History retrieval successful")

    # 4. Start new chat
    print("\n4. Starting new chat (clearing memory)...")
    resp = requests.post(f"{BASE_URL}/chat/new")
    print(f"New Chat Result: {resp.json()}")
    assert resp.status_code == 200

    # 5. Verify memory is cleared (by checking if saving returns 'ignored' or empty)
    print("\n5. Verifying memory cleared...")
    resp = requests.post(f"{BASE_URL}/chat/save", json={"user_id": "test_user_1"})
    print(f"Save Result (should be ignored/empty): {resp.json()}")
    # Depending on implementation, it might return status 'ignored' or just save an empty session
    # My implementation returns {"status": "ignored", ...} if no messages
    assert resp.json().get("status") == "ignored"
    print("✅ Memory cleared successfully")

if __name__ == "__main__":
    # Ensure server is running before running this test
    print("Make sure 'uvicorn app.api_server:app' is running in another terminal!")
    time.sleep(1)
    test_chat_history_flow()
