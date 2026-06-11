# ⚡ Life Tracker — Abdulboriy

Kunlik vazifalarni kuzatish, IELTS + Kali Linux + hayot rejasi uchun.

---

## 📁 Loyiha Tuzilmasi

```
life-tracker/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── bot.py           # Telegram notifications
│   ├── requirements.txt
│   └── railway.toml
└── frontend/
    └── index.html       # Dashboard
```

---

## 🚀 Railway ga Deploy Qilish

### 1. Railway account ochish
- https://railway.app ga kir
- GitHub bilan login qil

### 2. Backend deploy
```bash
# GitHub ga push qil
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/SENING_USERNAME/life-tracker.git
git push -u origin main
```
- Railway da "New Project" → "Deploy from GitHub repo"
- `backend` papkasini tanla
- Deploy tugagach URL olasan: `https://XXXX.railway.app`

### 3. Frontend sozlash
- `frontend/index.html` ichida shu qatorni o'zgartir:
```javascript
const API_URL = "https://XXXX.railway.app"; // Railway URL shu yerga
```

### 4. Telegram Bot sozlash (ixtiyoriy)
Railway da Environment Variables qo'sh:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Bot tokenni @BotFather dan ol.
Chat ID ni @userinfobot dan ol.

---

## 💻 Local ishga tushirish

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Keyin `frontend/index.html` ni brauzerda och.
`API_URL` ni `http://localhost:8000` ga o'zgartir.

---

## 📊 API Endpoints

| Method | URL | Nima qiladi |
|--------|-----|-------------|
| GET | /tasks | Barcha vazifalar |
| POST | /tasks | Yangi vazifa qo'sh |
| DELETE | /tasks/{id} | Vazifani o'chir |
| GET | /logs/{date} | Kun logi |
| POST | /logs | Logni yangilash |
| GET | /stats | Streak + statistika |
