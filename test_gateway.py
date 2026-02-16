import httpx
import time
import asyncio

BASE_URL = "http://localhost:8000"
API_KEY = "sk-gateway-secret-key-123"

async def test_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/health")
        print(f"Health Check: {resp.status_code} - {resp.json()}")

async def test_chat_completion():
    headers = {"X-Gateway-Key": API_KEY}
    payload = {
        "model": "auto",
        "messages": [{"role": "user", "content": "Hello!"}]
    }
    
    print("\nTesting Chat Completion (General)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)
            if resp.status_code == 200:
                print(f"Success! Model Used: {resp.json()['model']}")
                print(f"Response: {resp.json()['choices'][0]['message']['content'][:50]}...")
            else:
                print(f"Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

async def test_coder_routing():
    headers = {"X-Gateway-Key": API_KEY}
    payload = {
        "model": "auto",
        "messages": [{"role": "user", "content": "Write a python function to print hello world"}]
    }
    
    print("\nTesting Coder Routing...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)
            if resp.status_code == 200:
                print(f"Success! Model Used: {resp.json()['model']}")
            else:
                print(f"Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_health())
    asyncio.run(test_chat_completion())
    asyncio.run(test_coder_routing())
