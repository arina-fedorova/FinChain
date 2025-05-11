import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from supabase import create_client
from langchain_agent import parse_account_message
from db import get_or_create_user
from keyboards import confirm_account_kb
import html

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Supabase connection
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Temporary storage for user accounts
user_temp_accounts = {}

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    telegram_user = message.from_user
    get_or_create_user(message.from_user)
    await message.answer(f"👋 Hello, {telegram_user.first_name}! \n ✅ You are registered and ready to track your finances!")

@dp.message(F.text)
async def handle_freeform_account_message(message: Message):
    user_id = message.from_user.id
    user_data = supabase.table("users").select("id").eq("telegram_id", user_id).execute().data
    if not user_data:
        await message.answer("⚠️ You are not registered. Use /start first.")
        return

    await message.answer("🧠 Let me try to understand your account...")
    try:
        result = parse_account_message(message.text)
        
        # Empty result check
        if not result or result == {}:
            await message.answer("⚠️ I couldn't extract account info. Try rephrasing.")
            return

        # Save to temporary storage
        user_temp_accounts[message.from_user.id] = result

        await message.answer(
                f"🔍 I found:\n\n"
                f"🏦 Account: {result['name']}\n"
                f"💱 Currency: {result['currency']}\n"
                f"💰 Balance: {result['initial_balance']}\n\n"
                f"✅ Confirm to save or ❌ Cancel.",
                reply_markup=confirm_account_kb()
            )
    except Exception as e:
        print("❌ Agent failed:", str(e))
        await message.answer(f"❌ Couldn't parse that. Try rephrasing.\n\nError: {html.escape(str(e))}")

@dp.callback_query(F.data == "confirm_account")
async def confirm_account_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_temp_accounts.get(user_id)

    if not data:
        await callback.message.edit_text("⚠️ No data to confirm.")
        return
    
    currency_code = data["currency"]
    currency = supabase.table("currencies").select("id").eq("code", currency_code).execute().data

    if not currency:
        await callback.message.edit_text(f"⚠️ Unknown currency: {currency_code}. Please check and try again.")
        return
    
    # Recieve user ID from Supabase
    user_data = supabase.table("users").select("id").eq("telegram_id", user_id).execute().data
    if not user_data:
        await callback.message.edit_text("⚠️ User not found. Use /start.")
        return
    user_uuid = user_data[0]["id"]

    # DB insert
    supabase.table("accounts").insert({
        "user_id": user_uuid,
        "name": data["name"],
        "currency_id": currency[0]["id"],
        "initial_balance": data["initial_balance"],
        "is_archived": False,
        "type": "manual",
        "rate_source": "manual"
    }).execute()

    # Revove from temporary storage
    user_temp_accounts.pop(user_id)

    await callback.message.edit_text("✅ Account saved!")

@dp.callback_query(F.data == "cancel_account")
async def cancel_account_handler(callback: CallbackQuery):
    user_temp_accounts.pop(callback.from_user.id, None)
    await callback.message.edit_text("❌ Account was not saved.")

async def main():
    print("✅ Bot is running in polling mode...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())