import threading

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


def run_bot():
    import os
    import asyncio
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
    from telegram.ext import ContextTypes

    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        print("BOT_TOKEN not set, skipping bot startup")
        return

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[InlineKeyboardButton(
            "🛡 Open Token Risk Checker",
            web_app=WebAppInfo(url="https://anti-scam-g7zhk3yy4-nicks-projects-24d5052b.vercel.app")
        )]]
        await update.message.reply_text(
            "👋 Welcome to Token Risk Checker!\n\nSend any BSC or ETH token address to analyze it.\n\nOr open the Mini App:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def run():
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        await app_bot.initialize()
        await app_bot.start()
        await app_bot.updater.start_polling()
        print("Telegram bot is running...")
        await asyncio.Event().wait()

    asyncio.run(run())


bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=10000)