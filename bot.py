from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from web3 import Web3

from checker import analyze_token


BOT_TOKEN = "8541598294:AAGYc17FoDgIWDfDhDMVjFHY8l0Gjg1PRkE"
DEFAULT_NETWORK = "bsc"


def is_valid_token_address(address: str) -> bool:
    return Web3.is_address(address)


def verdict_emoji(risk_level: str) -> str:
    if risk_level == "LOW RISK":
        return "✅ LOW RISK"
    if risk_level == "MEDIUM RISK":
        return "⚠️ CAUTION"
    return "🚨 HIGH RISK"
     

def yes_no_unknown(value) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unknown"


def build_recommendation(result: dict) -> str:
    final = result["final_assessment"]
    liquidity = result["liquidity_analysis"]
    sellability = result["sellability"]

    if final["risk_level"] == "HIGH RISK":
        return (
            "Avoid interacting with this token until manual review is completed. "
            "High-risk indicators were detected."
        )

    if final["risk_level"] == "MEDIUM RISK":
        return (
            "Proceed carefully. Review ownership, mint rights, and liquidity "
            "before making any transaction."
        )

    if liquidity.get("has_liquidity") and sellability.get("status") == "OK":
        return "Basic heuristic checks look acceptable, but manual verification is still recommended."

    return (
        "No major heuristic red flags were found, but the result is limited. "
        "Always verify the contract manually."
    )


def format_security_report(result: dict) -> str:
    token = result["token"]
    contract = result["contract_analysis"]
    liquidity = result["liquidity_analysis"]
    final = result["final_assessment"]

    risk_factors = final["reasons"][:]
    if not risk_factors:
        risk_factors = ["No major heuristic risk factors were detected."]

    lines = [
        "🛡 Token Security Report",
        "",
        "📌 Address:",
        token["address"],
        "",
        "📊 Summary",
        f"• Verdict: {verdict_emoji(final['risk_level'])}",
        f"• Score: {final['risk_score']}/100",
        "",
        "🧾 Contract Details",
        f"• Admin: {contract['owner_address']}",
        f"• Mintable: {yes_no_unknown(contract['mint_function_present'])}",
        f"• Total Supply: {token['total_supply']}",
        "",
        "💧 Liquidity",
        f"• LP Found: {yes_no_unknown(liquidity.get('has_liquidity'))}",
        f"• DEXs: {liquidity.get('dex', 'Unknown')}",
        "",
        "⚠ Risk Factors",
    ]

    for factor in risk_factors:
        lines.append(f"• {factor}")

    lines.extend(
        [
            "",
            "🧠 Recommendation",
            build_recommendation(result),
            "",
            "ℹ Note",
            "This report is heuristic-based.",
        ]
    )

    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[
        InlineKeyboardButton(
            "🛡 Open Token Risk Checker",
            web_app=WebAppInfo(url="https://anti-scam-g7zhk3yy4-nicks-projects-24d5052b.vercel.app")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to Token Risk Checker!\n\nSend any BSC or ETH token address to analyze it for honeypot risks.\n\nOr open the Mini App for a visual interface:",
        reply_markup=reply_markup
    )


async def handle_token_address(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    _ = context
    if not update.message or not update.message.text:
        return

    address = update.message.text.strip()

    if not is_valid_token_address(address):
        await update.message.reply_text(
            "Неверный адрес. Отправь корректный адрес токена."
        )
        return

    await update.message.reply_text("Анализирую токен, подожди немного...")

    try:
        result = analyze_token(address, DEFAULT_NETWORK)
        report_text = format_security_report(result)
        await update.message.reply_text(report_text)
    except Exception:
        await update.message.reply_text(
            "Ошибка при анализе. Попробуй позже."
        )


def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token_address)
    )

    print("Telegram bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
