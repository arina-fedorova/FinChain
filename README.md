# FinChain

**FinChain** is a personal finance assistant powered by Telegram, LangChain, and Supabase.

It allows you to:
- Add accounts in natural language (e.g. "I have around 250 dollars on my travel card")
- Store and manage your balances
- Track your finances via chat
- (Soon) forecast, categorize, and visualize spending

## 🚀 Stack
- **Python 3.9+**
- **LangChain** + OpenAI (GPT-4o)
- **Supabase** (PostgreSQL)
- **Aiogram** (Telegram bot framework)

## 🛠 Setup

1. Clone the repo  
2. Copy `.env.example` → `.env` and fill in your Supabase & OpenAI credentials  
3. Create database with `database/schema.sql`  
4. Install deps:  
```bash
   pip install -r requirements.txt
```

## 🧩 DB Schema

All database structure is in [`database/schema.sql`](database/schema.sql)

## 📦 Roadmap

- [x] Add accounts via AI
- [ ] Add transactions
- [ ] Weekly spending limits
- [ ] Natural language analytics
- [ ] Multicurrency support