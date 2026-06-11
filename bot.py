import asyncio
import os
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date
import httpx

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
API_URL = os.getenv("API_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN)

async def morning_notification():
    """Ertalab 8:00 da yuboriladi"""
    today = date.today().isoformat()    TELEGRAM_BOT_TOKEN=8721082815:AAGyu-tITyvEvfGHvfTSl61kf-Xq_thfdG4
    TELEGRAM_CHAT_ID=YOUR_CHAT_ID
    API_URL=http://localhost:8000
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/logs/{today}")
        tasks = response.json()
    
    task_list = "\n".join([f"{t['icon']} {t['name']}" for t in tasks])
    
    message = f"""🌅 *Xayrli tong, Abdulboriy!*

Bugungi vazifalar ({today}):
{task_list}

💪 Kuchli kun bo'lsin!
👉 Ilovani oching va boshlang!"""
    
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode="Markdown"
    )

async def evening_notification():
    """Kechqurun 21:00 da yuboriladi"""
    today = date.today().isoformat()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/logs/{today}")
        tasks = response.json()
        stats_response = await client.get(f"{API_URL}/stats")
        stats = stats_response.json()
    
    completed = sum(1 for t in tasks if t["completed"])
    total = len(tasks)
    
    if completed < total:
        not_done = [f"{t['icon']} {t['name']}" for t in tasks if not t["completed"]]
        not_done_list = "\n".join(not_done)
        
        message = f"""⚠️ *Abdulboriy, bugun tugallanmagan vazifalar bor!*

❌ Bajarilmagan:
{not_done_list}

📊 Natija: {completed}/{total}
🔥 Streak: {stats['streak']} kun

Hali vaqt bor — bajaring! 💪"""
    else:
        message = f"""🎉 *Zo'r! Bugun barcha vazifalar bajarildi!*

✅ {completed}/{total} vazifa bajarildi
🔥 Streak: {stats['streak']} kun ketma-ket!

Yaxshi dam oling! 🌙"""
    
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode="Markdown"
    )

async def main():
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    
    # Ertalab 8:00
    scheduler.add_job(morning_notification, "cron", hour=8, minute=0)
    
    # Kechqurun 21:00
    scheduler.add_job(evening_notification, "cron", hour=21, minute=0)
    
    scheduler.start()
    print("✅ Telegram bot notification service ishga tushdi!")
    
    # Keep running
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
