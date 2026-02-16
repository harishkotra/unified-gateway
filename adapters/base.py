from abc import ABC, abstractmethod
from models import ChatCompletionRequest, ChatCompletionResponse

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        Generates a response from the model provider based on the request.
        """
        pass
