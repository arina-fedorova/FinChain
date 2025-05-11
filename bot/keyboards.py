from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_account_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_account"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_account")
            ]
        ]
    )
