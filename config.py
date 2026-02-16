import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Server Config
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    GATEWAY_KEY = os.getenv("GATEWAY_KEY", "sk-gateway-secret-key-123")

    # Provider Configs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Redis Config
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "false").lower() == "true"

    # Routing Config
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    CODER_MODEL = os.getenv("CODER_MODEL", "codellama")
    CHEAP_MODEL = os.getenv("CHEAP_MODEL", "gpt-3.5-turbo")
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-3.5-turbo")
    
    # Timeout
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 30))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))

    # Model Provider Mapping
    MODEL_PROVIDERS = {
        "gpt-4": "openai",
        "gpt-3.5-turbo": "openai",
        "llama3.2": "ollama",
        "qwen3:4b": "ollama",
        "gemma3:4b": "ollama",
        "codellama": "ollama",
    }
