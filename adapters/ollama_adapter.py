import httpx
import time
import uuid
from config import Config
from models import ChatCompletionRequest, ChatCompletionResponse, Choice, Message, Usage
from adapters.base import ModelAdapter

class OllamaAdapter(ModelAdapter):
    def __init__(self, base_url: str = Config.OLLAMA_BASE_URL):
        self.base_url = base_url

    async def generate(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        # Convert OpenAI format to Ollama format
        ollama_payload = {
            "model": request.model,
            "messages": [msg.model_dump() for msg in request.messages],
            "stream": False,  # We enforce no streaming for version 1
            "options": {
                "temperature": request.temperature,
                # "num_predict": request.max_tokens # Ollama uses num_predict instead of max_tokens
            }
        }
        
        if request.max_tokens:
            ollama_payload["options"]["num_predict"] = request.max_tokens

        async with httpx.AsyncClient(timeout=Config.TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=ollama_payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert Ollama response to OpenAI format
            # Ollama response example:
            # {
            #   "model": "llama3",
            #   "created_at": "2023-08-04T19:22:45.499127Z",
            #   "message": { "role": "assistant", "content": "Hello!" },
            #   "done": true,
            #   "total_duration": 123,
            #   "load_duration": 123,
            #   "prompt_eval_count": 10,
            #   "eval_count": 20
            # }

            return ChatCompletionResponse(
                id=f"chatcmpl-{uuid.uuid4()}",
                object="chat.completion",
                created=int(time.time()),
                model=data.get("model", request.model),
                choices=[
                    Choice(
                        index=0,
                        message=Message(
                            role=data["message"]["role"],
                            content=data["message"]["content"]
                        ),
                        finish_reason="stop" if data.get("done") else "length"
                    )
                ],
                usage=Usage(
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                )
            )
