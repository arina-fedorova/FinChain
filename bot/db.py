import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_user(telegram_user) -> dict:
    telegram_id = telegram_user.id

    # Check if user already exists
    existing_user = (
        supabase.table("users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    if existing_user.data:
        return existing_user.data[0]

    # Create new user
    response = (
        supabase.table("users")
        .insert({
            "telegram_id": telegram_id,
            "chat_id": telegram_user.id,
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name
        })
        .execute()
    )

    return response.data[0]