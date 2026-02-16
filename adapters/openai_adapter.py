import httpx
import time
from config import Config
from models import ChatCompletionRequest, ChatCompletionResponse, Choice, Message, Usage
from adapters.base import ModelAdapter

class OpenAIAdapter(ModelAdapter):
    def __init__(self, base_url: str = Config.OPENAI_BASE_URL, api_key: str = Config.OPENAI_API_KEY):
        self.base_url = base_url
        self.api_key = api_key

    async def generate(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload, filtering out None values
        payload = request.model_dump(exclude_none=True)
        
        # If model is "auto" or generic, we might want to map it, 
        # but for now, we pass it through or let the router decide the specific model name before calling generate.
        # Assuming the router sets the specific model in the request or we use the default from config if not specific.
        
        async with httpx.AsyncClient(timeout=Config.TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            # Map response back to our Pydantic model to ensure consistency
            # OpenAI response format should match mostly, but we validate it here.
            return ChatCompletionResponse(**data)
