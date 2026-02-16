from typing import List, Tuple
from config import Config
from models import ChatCompletionRequest
from adapters import ModelAdapter, OpenAIAdapter, OllamaAdapter

class Router:
    def __init__(self):
        self.openai_adapter = OpenAIAdapter()
        self.ollama_adapter = OllamaAdapter()
        
        # Simple mapping for now
        self.adapters = {
            "openai": self.openai_adapter,
            "ollama": self.ollama_adapter
        }

    def _get_provider_for_model(self, model_name: str) -> str:
        return Config.MODEL_PROVIDERS.get(model_name, "ollama") # Default to ollama if unknown

    def route(self, request: ChatCompletionRequest) -> Tuple[ModelAdapter, str, List[ModelAdapter]]:
        """
        Determines the best adapter and model to use based on the request.
        Returns: (primary_adapter, primary_model_name, list_of_fallback_adapters)
        """
        
        # 1. Rule-based Routing
        
        # Message analysis
        all_content = " ".join([m.content for m in request.messages])
        is_code_task = any(keyword in all_content.lower() for keyword in ["def ", "class ", "import ", "function", "code"])
        token_estimate = len(all_content) / 4 # Rough estimate
        
        selected_model = request.model
        
        if request.model == "auto":
            if is_code_task:
                selected_model = Config.CODER_MODEL
            elif token_estimate < 500:
                selected_model = Config.CHEAP_MODEL
            else:
                selected_model = Config.DEFAULT_MODEL
        
        # 2. Provider Selection
        provider = self._get_provider_for_model(selected_model)
        adapter = self.adapters.get(provider, self.openai_adapter)
        
        # 3. Fallback Chain
        fallback_model = Config.FALLBACK_MODEL
        fallback_provider = self._get_provider_for_model(fallback_model)
        fallback_adapter = self.adapters.get(fallback_provider, self.openai_adapter)
        
        fallbacks = []
        if adapter != fallback_adapter:
            fallbacks.append(fallback_adapter)
            
        return adapter, selected_model, fallbacks

# Global router instance
router = Router()
