import os import json import requests from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

Bot Token

TOKEN = "7943181442:AAEJFlauEPGIUhlYd07IN6j4_BMyNw_IT8U"

Static USDT Address (TRC20)

USDT_ADDRESS = "TJvGvaVXPR8vo68txc59cGUCvp3jtPr36S"

Book Database

BOOKS = { "Romance": [ {"id": "r1", "title": "Love & Fate", "price": 2.5, "file": "books/love_and_fate.pdf"}, {"id": "r2", "title": "Dear Heart", "price": 3.0, "file": "books/dear_heart.pdf"}, ], "Fiction": [ {"id": "f1", "title": "Time Loop", "price": 2.0, "file": "books/time_loop.pdf"}, ] }

Track user session (in-memory)

USER_SESSIONS = {}

Handle /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): buttons = [ [InlineKeyboardButton(genre, callback_data=f"genre_{genre}")] for genre in BOOKS ] buttons += [[InlineKeyboardButton("Help", callback_data="help"), InlineKeyboardButton("Customer Care", callback_data="support")]] await update.message.reply_text("Welcome! Choose a genre:", reply_markup=InlineKeyboardMarkup(buttons))

Handle genre/book selection

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() data = query.data

if data.startswith("genre_"):
    genre = data.split("_")[1]
    USER_SESSIONS[query.from_user.id] = {"genre": genre}
    books = BOOKS[genre]
    buttons = [
        [InlineKeyboardButton(f"{book['title']} ({book['price']} USDT)", callback_data=f"book_{book['id']}")] for book in books
    ]
    buttons += [[InlineKeyboardButton("Back", callback_data="back")]]
    await query.edit_message_text(f"Books in {genre}:", reply_markup=InlineKeyboardMarkup(buttons))

elif data.startswith("book_"):
    book_id = data.split("_")[1]
    user_data = USER_SESSIONS.get(query.from_user.id, {})
    genre = user_data.get("genre")
    book = next((b for b in BOOKS[genre] if b['id'] == book_id), None)
    if book:
        USER_SESSIONS[query.from_user.id]["book"] = book
        await query.edit_message_text(
            f"*{book['title']}*\nPrice: {book['price']} USDT\n\nPay to this TRC20 address:\n`{USDT_ADDRESS}`\n\nSend TXID or screenshot after payment.",
            parse_mode="Markdown"
        )

elif data == "help":
    await query.edit_message_text("To buy a book, select a genre, choose a book, pay using USDT (TRC20), then send the TXID or screenshot. We'll verify and send your book.")

elif data == "support":
    await query.edit_message_text("Customer Care: @YourSupportHandle")

elif data == "back":
    await start(update, context)

Handle user messages (proof submission)

async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id user_session = USER_SESSIONS.get(user_id)

if not user_session or "book" not in user_session:
    await update.message.reply_text("Please choose a book first using /start.")
    return

book = user_session["book"]
await update.message.reply_text("Verifying payment. Please wait...")

# Simulated auto-verification (replace with real API call to TronGrid)
txid_or_proof = update.message.text or "screenshot"
if len(txid_or_proof) >= 8:  # Simple mock check
    await context.bot.send_document(chat_id=update.effective_chat.id, document=InputFile(book["file"]))
    await update.message.reply_text("Thank you! Here's your book.")
else:
    await update.message.reply_text("Invalid TXID. Please try again.")

Start the bot

app = ApplicationBuilder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CallbackQueryHandler(handle_buttons)) app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_proof)) app.run_polling()

