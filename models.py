from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
import time

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "auto"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    stream: Optional[bool] = False
    
class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = "stop"

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Choice]
    usage: Usage
