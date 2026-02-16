from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import time
import uvicorn

from config import Config
from models import ChatCompletionRequest, ChatCompletionResponse
from router import router
from cache import cache
from logger import request_logger

# Auth
api_key_header = APIKeyHeader(name="X-Gateway-Key", auto_error=False)

async def verify_api_key(key: str = Depends(api_key_header)):
    if key != Config.GATEWAY_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-Gateway-Key"
        )
    return key

# Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: could check redis connection here
    yield
    # Shutdown: close connections if needed

app = FastAPI(title="Unified Model Gateway", lifespan=lifespan)

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    start_time = time.time()
    
    # 1. Routing
    adapter, model_name, fallbacks = router.route(request)
    
    # Update request with actual model name if it was "auto"
    request.model = model_name
    
    # 2. Caching
    request_dict = request.model_dump()
    cached_response = await cache.get(request_dict)
    if cached_response:
        # Log cache hit (optional, maybe separate field)
        return ChatCompletionResponse(**cached_response)

    # 3. Generation & Fallback
    response = None
    error_msg = None
    fallback_used = False
    
    # Primary attempt
    try:
        response = await adapter.generate(request)
        provider = adapter.__class__.__name__
    except Exception as e:
        print(f"Primary provider failed: {e}")
        error_msg = str(e)
        
        # Fallback attempts
        for fb_adapter in fallbacks:
            try:
                print(f"Attempting fallback to {fb_adapter.__class__.__name__}")
                response = await fb_adapter.generate(request)
                provider = fb_adapter.__class__.__name__
                fallback_used = True
                error_msg = None # Clear error on success
                break
            except Exception as fb_e:
                print(f"Fallback provider failed: {fb_e}")
                error_msg = str(fb_e)
    
    if not response:
        # Log failure
        latency = (time.time() - start_time) * 1000
        request_logger.log_request(
            model_requested=request.model,
            model_used="None",
            provider="None",
            latency_ms=latency,
            usage={},
            status_code=500,
            fallback_used=fallback_used,
            error_message=error_msg
        )
        raise HTTPException(status_code=502, detail=f"All providers failed. Last error: {error_msg}")

    # 4. Cache Store
    await cache.set(request_dict, response.model_dump())

    # 5. Logging
    latency = (time.time() - start_time) * 1000
    request_logger.log_request(
        model_requested=request.model,
        model_used=response.model,
        provider=provider,
        latency_ms=latency,
        usage=response.usage.model_dump(),
        status_code=200,
        fallback_used=fallback_used,
        error_message=None
    )

    return response

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/models")
async def valid_models():
    return {"models": list(Config.MODEL_PROVIDERS.keys())}
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=Config.PORT, reload=True)
