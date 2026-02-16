# Minimal Unified Model Gateway

A lightweight, production-ready AI Gateway built with FastAPI. It provides a single **OpenAI-compatible API** to route requests to various LLM providers, designed with an **"Ollama First"** approach for local inference.

<img width="1238" height="542" alt="image" src="https://github.com/user-attachments/assets/c51e37b4-3f6f-4e25-a008-5bed2dedd36d" />


## 🌟 Key Features

*   **Ollama Native**: Works out-of-the-box with your local Ollama models.
*   **OpenAI Compatible**: Drop-in replacement for OpenAI SDKs (`/v1/chat/completions`).
*   **Smart Routing**: Automatically routes requests based on rules (e.g., Code tasks -> Coder Model, Short prompts -> Fast Model).
*   **Resilient**: Automatic fallbacks if a provider fails.
*   **Cachable**: Built-in Redis caching support (totally optional).
*   **Observable**: Requests are logged to a local SQLite database for easy auditing.

## 🚀 Quick Start

### 1. Prerequisites

*   Python 3.11+
*   [Ollama](https://ollama.com/) running locally (`ollama serve`)

### 2. Installation

Clone/Download this repo and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration

The project uses a `.env` file. You can copy the example:

```bash
cp .env.example .env
```

**Defaults work immediately!**
By default, it looks for these Ollama models. Make sure you have them pulled or update `.env` to match what you have:
*   `DEFAULT_MODEL=llama3.2`
*   `CODER_MODEL=qwen3:4b`
*   `CHEAP_MODEL=gemma3:4b`

*(To pull them: `ollama pull llama3.2`, `ollama pull qwen3:4b`, etc.)*

### 4. Run It

```bash
uvicorn app:app --reload
```
Server runs at `http://localhost:8000`.

## ⚡ Usage

You can use standard OpenAI libraries. Just change the `base_url` and `api_key`.

**Python Example:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-gateway-secret-key-123" # Matches GATEWAY_KEY in .env
)

# Route to General Model
response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Tell me a joke."}]
)
print(response.choices[0].message.content)

# Smart Routing (Code -> Coder Model)
# This will be automatically routed to 'qwen3:4b' (or your configured coder model)
response = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "Write a Python function to merge sort a list."}]
)
```

## 🛠️ Fork & Extend

This project is built to be a minimal foundation. Here are ideas on how you can extend it:

### 1. Advanced Routing (Router.py)
*   **Semantic Routing**: Use an embedding model to classify the prompt intent (e.g., "creative writing", "math", "coding") and route to the best specialized model.
*   **Cost-Based Routing**: Route to cheaper providers for non-critical tasks.
*   **A/B Testing**: Randomly split traffic between two models to compare performance.

### 2. New Adapters (adapters/)
*   **Anthropic**: Add `adapters/anthropic_adapter.py` to support Claude.
*   **Groq**: Add a specialized adapter for ultra-fast inference.
*   **Gemini/Vertex**: Add Google model support.
*   *How*: Inherit from `ModelAdapter` and implement `generate()`.

### 3. Enterprise Features
*   **Rate Limiting**: Add Redis-based token buckets per API key.
*   **User Management**: Replace the simple API key check with a database of users/orgs.
*   **Admin UI**: Build a Streamlit or React dashboard to view the SQLite logs (`requests.db`).

### 4. DevOps
*   **Dockerize**: Add a `Dockerfile` and `docker-compose.yml` to bundle the app with Redis and Ollama.
*   **Metrics**: Expose a `/metrics` endpoint for Prometheus to track token usage and latency.
