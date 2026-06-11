import asyncio
import os
import httpx
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = os.getenv("API_URL", "http://localhost:8000")

async def morning_notification():
    bot = Bot(token=BOT_TOKEN)
    today = date.today().isoformat()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/logs/{today}")
        tasks = r.json()
    task_list = "\n".join([f"{t['icon']} {t['name']}" for t in tasks])
    await bot.send_message(chat_id=CHAT_ID, text=f"🌅 *Xayrli tong, Abdulboriy!*\n\nBugungi vazifalar:\n{task_list}\n\n💪 Kuchli kun bo'lsin!", parse_mode="Markdown")

async def evening_notification():
    bot = Bot(token=BOT_TOKEN)
    today = date.today().isoformat()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/logs/{today}")
        tasks = r.json()
        sr = await client.get(f"{API_URL}/stats")
        stats = sr.json()
    done = sum(1 for t in tasks if t["completed"])
    total = len(tasks)
    if done < total:
        not_done = "\n".join([f"{t['icon']} {t['name']}" for t in tasks if not t["completed"]])
        msg = f"⚠️ *Abdulboriy, vazifalar tugallanmagan!*\n\n❌ Bajarilmagan:\n{not_done}\n\n📊 {done}/{total}\n🔥 Streak: {stats['streak']} kun"
    else:
        msg = f"🎉 *Zo'r! Barcha vazifalar bajarildi!*\n\n✅ {done}/{total}\n🔥 Streak: {stats['streak']} kun!"
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

async def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ TELEGRAM_BOT_TOKEN yoki TELEGRAM_CHAT_ID yo'q!")
        return
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(morning_notification, "cron", hour=8, minute=0)
    scheduler.add_job(evening_notification, "cron", hour=21, minute=0)
    scheduler.start()
    print("✅ Bot scheduler ishga tushdi!")
    while True:
        await asyncio.sleep(60)
