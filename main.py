from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date, datetime
import sqlite3
import os
import threading

app = FastAPI(title="Life Tracker - Abdulboriy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "tracker.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            icon TEXT DEFAULT '📌'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            UNIQUE(task_id, date)
        )
    """)
    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        default_tasks = [
            ("Nonushta", "kun", "🍳"),
            ("IELTS Dars", "talim", "📚"),
            ("Kali Linux / Dasturlash", "talim", "💻"),
            ("Kitob O'qish", "talim", "📖"),
            ("Kechki Ovqat", "kun", "🍽️"),
            ("Sport / Yurish", "sog'liq", "🏃"),
        ]
        c.executemany("INSERT INTO tasks (name, category, icon) VALUES (?, ?, ?)", default_tasks)
    conn.commit()
    conn.close()

init_db()

class TaskCreate(BaseModel):
    name: str
    category: str
    icon: str = "📌"

class LogUpdate(BaseModel):
    task_id: int
    date: str
    completed: bool

@app.get("/")
def root():
    return {"message": "Life Tracker API ishlayapti! ✅"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(t) for t in tasks]

@app.post("/tasks")
def create_task(task: TaskCreate):
    conn = get_db()
    conn.execute("INSERT INTO tasks (name, category, icon) VALUES (?, ?, ?)",
        (task.name, task.category, task.icon))
    conn.commit()
    conn.close()
    return {"message": "Vazifa qo'shildi ✅"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.execute("DELETE FROM daily_logs WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Vazifa o'chirildi ✅"}

@app.get("/logs/{date}")
def get_logs(date: str):
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    logs = conn.execute("SELECT * FROM daily_logs WHERE date = ?", (date,)).fetchall()
    log_map = {l["task_id"]: l["completed"] for l in logs}
    result = []
    for task in tasks:
        result.append({
            "task_id": task["id"],
            "name": task["name"],
            "category": task["category"],
            "icon": task["icon"],
            "completed": bool(log_map.get(task["id"], 0))
        })
    conn.close()
    return result

@app.post("/logs")
def update_log(log: LogUpdate):
    conn = get_db()
    conn.execute("""
        INSERT INTO daily_logs (task_id, date, completed)
        VALUES (?, ?, ?)
        ON CONFLICT(task_id, date) DO UPDATE SET completed = ?
    """, (log.task_id, log.date, int(log.completed), int(log.completed)))
    conn.commit()
    conn.close()
    return {"message": "Yangilandi ✅"}

@app.get("/stats")
def get_stats():
    conn = get_db()
    stats = conn.execute("""
        SELECT date, COUNT(*) as total, SUM(completed) as done
        FROM daily_logs GROUP BY date ORDER BY date DESC LIMIT 30
    """).fetchall()
    all_dates = conn.execute("""
        SELECT date, COUNT(*) as total, SUM(completed) as done
        FROM daily_logs GROUP BY date ORDER BY date DESC
    """).fetchall()
    streak = 0
    for row in all_dates:
        if row["done"] == row["total"] and row["total"] > 0:
            streak += 1
        else:
            break
    conn.close()
    return {"daily": [dict(s) for s in stats], "streak": streak}

@app.get("/stats/weekly")
def get_weekly():
    conn = get_db()
    weekly = conn.execute("""
        SELECT t.name, t.icon, t.category,
               COUNT(l.id) as total_days,
               SUM(l.completed) as completed_days
        FROM tasks t
        LEFT JOIN daily_logs l ON t.id = l.task_id
        WHERE l.date >= date('now', '-7 days')
        GROUP BY t.id
    """).fetchall()
    conn.close()
    return [dict(w) for w in weekly]

def run_bot():
    import asyncio
    from bot import main as bot_main
    asyncio.run(bot_main())

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
