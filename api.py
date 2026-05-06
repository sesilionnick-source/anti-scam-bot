from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from web3 import Web3

from checker import analyze_token

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Token Risk Checker API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request, token: str, network: str = "bsc"):
    if not Web3.is_address(token):
        return JSONResponse(status_code=400, content={"error": "Invalid token address"})

    if network not in ("bsc", "eth"):
        return JSONResponse(status_code=400, content={"error": "Network must be bsc or eth"})

    try:
        result = analyze_token(token, network)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/health")
async def health():
    return {"status": "ok"}


import threading
import asyncio

def run_bot():
    from bot import main as bot_main
    asyncio.run(bot_main())

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

import threading

def run_bot():
    import asyncio
    from bot import main as bot_main
    asyncio.run(bot_main())

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=10000)
    
