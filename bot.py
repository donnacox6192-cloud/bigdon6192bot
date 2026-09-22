"""
BigDon6192Bot - A Telegram bot for math calculations and unit conversions.
Author: Senior Developer
Framework: python-telegram-bot v21+
Deployment: Railway
"""

import logging
import os
import re
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# -------------------- Setup --------------------
load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------------------- Safe Math Evaluator --------------------
SAFE_PATTERN = re.compile(r"^[0-9\.\+\-\*\/\(\)\s\^%]+$")


def safe_eval(expression: str) -> float:
    """Safely evaluate a math expression without using eval() on arbitrary input."""
    expression = expression.replace("^", "**")
    if not SAFE_PATTERN.match(expression.replace("**", "^").replace("^", "^")):
        # re-check on original pattern rules
        if not re.match(r"^[0-9\.\+\-\*\/\(\)\s\^%]+$", expression.replace("**", "^")):
            raise ValueError("Invalid characters in expression.")
    # Only allow safe builtins
    allowed = {"__builtins__": None}
    return eval(expression, allowed, {})


# -------------------- Unit Conversion Tables --------------------
# All conversions are to/from a base SI unit
LENGTH_UNITS = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}

WEIGHT_UNITS = {
    "mg": 1e-6, "g": 0.001, "kg": 1.0, "t": 1000.0,
    "oz": 0.0283495, "lb": 0.453592, "stone": 6.35029,
}

TEMPERATURE_UNITS = {"c", "f", "k"}

VOLUME_UNITS = {
    "ml": 0.001, "l": 1.0, "m3": 1000.0,
    "gal": 3.78541, "qt": 0.946353, "pt": 0.473176, "cup": 0.236588,
}

TIME_UNITS = {
    "ms": 0.001, "s": 1.0, "min": 60.0, "h": 3600.0, "day": 86400.0, "week": 604800.0,
}


def convert_temperature(value: float, from_u: str, to_u: str) -> float:
    from_u, to_u = from_u.lower(), to_u.lower()
    # Normalize to Celsius
    if from_u == "c":
        c = value
    elif from_u == "f":
        c = (value - 32) * 5 / 9
    elif from_u == "k":
        c = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {from_u}")

    if to_u == "c":
        return c
    elif to_u == "f":
        return c * 9 / 5 + 32
    elif to_u == "k":
        return c + 273.15
    raise ValueError(f"Unknown temperature unit: {to_u}")


def convert_unit(value: float, from_u: str, to_u: str):
    from_u, to_u = from_u.lower(), to_u.lower()

    if from_u in TEMPERATURE_UNITS or to_u in TEMPERATURE_UNITS:
        if from_u not in TEMPERATURE_UNITS or to_u not in TEMPERATURE_UNITS:
            raise ValueError("Cannot mix temperature with other unit types.")
        return convert_temperature(value, from_u, to_u), "temperature"

    for name, table in [
        ("length", LENGTH_UNITS),
        ("weight", WEIGHT_UNITS),
        ("volume", VOLUME_UNITS),
        ("time", TIME_UNITS),
    ]:
        if from_u in table and to_u in table:
            base = value * table[from_u]
            return base / table[to_u], name

    raise ValueError(f"Unsupported conversion: {from_u} → {to_u}")


# -------------------- Handlers --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🧮 Math Help", callback_data="help_math"),
         InlineKeyboardButton("📏 Unit Help", callback_data="help_units")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ]
    await update.message.reply_text(
        f"👋 *Welcome to BigDon6192Bot!*\n\n"
        f"I can help you with:\n"
        f"• Basic math: `2+2*3`, `(5^2)/4`, `10%3`\n"
        f"• Unit conversion: `100 cm to m`, `5 kg to lb`, `30 c to f`\n\n"
        f"Just send me a message and I'll solve it! 🚀",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 *How to use BigDon6192Bot*\n\n"
        "*Math:*\n"
        "`2 + 2`\n"
        "`(10 * 5) / 2`\n"
        "`5 ^ 3`  (power)\n"
        "`17 % 5` (modulo)\n\n"
        "*Unit Conversion:*\n"
        "`100 cm to m`\n"
        "`5 kg to lb`\n"
        "`30 c to f` (Celsius → Fahrenheit)\n"
        "`2 mi to km`\n"
        "`3 gal to l`\n\n"
        "*Supported categories:* length, weight, temperature, volume, time.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 *BigDon6192Bot*\n"
        "A fast, reliable bot for math and unit conversions.\n\n"
        "Built with ❤️ using python-telegram-bot v21.\n"
        "Deployed on Railway 🚂",
        parse_mode=ParseMode.MARKDOWN,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "help_math":
        await query.edit_message_text(
            "🧮 *Math Examples:*\n`2+2`\n`(4*5)/2`\n`3^4`\n`17%5`",
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data == "help_units":
        await query.edit_message_text(
            "📏 *Unit Examples:*\n`100 cm to m`\n`5 kg to lb`\n`30 c to f`\n`2 mi to km`",
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data == "about":
        await query.edit_message_text(
            "🤖 *BigDon6192Bot*\nMath + Unit converter.\nDeployed on Railway 🚂",
            parse_mode=ParseMode.MARKDOWN,
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()

    # --- Unit conversion pattern: "<number> <from> to <to>" ---
    conv_match = re.match(
        r"^([-+]?\d*\.?\d+)\s*([a-zA-Z°]+)\s*(?:to|in|->|→)\s*([a-zA-Z°]+)$",
        text, re.IGNORECASE,
    )
    if conv_match:
        try:
            value = float(conv_match.group(1))
            from_u = conv_match.group(2).replace("°", "").lower()
            to_u = conv_match.group(3).replace("°", "").lower()
            result, category = convert_unit(value, from_u, to_u)
            await update.message.reply_text(
                f"📏 *{category.capitalize()} Conversion*\n"
                f"`{value} {from_u}` = `{round(result, 6)} {to_u}`",
                parse_mode=ParseMode.MARKDOWN,
            )
        except ValueError as e:
            await update.message.reply_text(f"❌ {e}")
        except Exception as e:
            logger.exception("Conversion error")
            await update.message.reply_text(f"⚠️ Conversion failed: {e}")
        return

    # --- Math expression ---
    if re.match(r"^[0-9\.\+\-\*\/\(\)\s\^%]+$", text):
        try:
            result = safe_eval(text)
            await update.message.reply_text(
                f"🧮 `{text}` = *{round(result, 10) if isinstance(result, float) else result}*",
                parse_mode=ParseMode.MARKDOWN,
            )
        except ZeroDivisionError:
            await update.message.reply_text("❌ Error: Division by zero.")
        except Exception:
            await update.message.reply_text(
                "⚠️ Couldn't compute that. Try `/help` for examples."
            )
        return

    await update.message.reply_text(
        "🤔 I didn't understand that.\nTry a math expression like `2+2` "
        "or a conversion like `100 cm to m`.\nUse /help for more.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:", exc_info=context.error)


# -------------------- Main --------------------
def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("🤖 BigDon6192Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
