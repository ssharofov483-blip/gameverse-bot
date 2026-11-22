# 🏰 GAMEVERSE — Multiplayer Medieval Kingdom Strategy Game

Production-grade, server-authoritative Telegram strategy game built with **Python 3.12**, **aiogram 3.x**, **FastAPI**, **SQLAlchemy 2.x**, **Alembic**, and **Docker**.

---

## 📖 O'yin Haqida (Game Concept)

**GAMEVERSE** — o'rta asrlar muhitidagi ko'p foydalanuvchili strategik o'yin. Har bir o'yinchi o'z saltanatini barpo etadi, resurslarni ishlab chiqaradi, binolarni yuksaltiradi, armiya yollaydi, PvE bosqichlarida qaroqchilar va ajdaholarga qarshi jang qiladi hamda boshqa o'yinchilar bilan PvP janglarda to'qnash keladi.

### Asosiy xususiyatlar:
- 🏰 **Qirollik va Qurilish**: 8 turdagi binolar (Qirollik qasri, Oltin koni, Yog'och kesish joyi, Temir koni, Ferma, Kazarma, Mudofaa devori, Akademiya).
- 💰 **Avtonom Iqtisodiyot**: Har bir binoning darajasiga qarab soatbay avtomatik resurs ishlab chiqarish va ombor sig'imi nazorati.
- 🪖 **Server-Authoritative Jang Dvigateli**:
  - 5 turdagi jangovar bo'linmalar: Oddiy askar, Kamonchi, Qilichboz, Ritsar (Otliq), Katapulta.
  - Taktik ustunlik matritsasi (Kamonchilar qilichbozlardan kuchli, Ritsarlar kamonchilarni yanchib tashlaydi, Katapultalar qal'a devorlarini parchalaydi).
  - Tasodifiy jang omillari (ob-havo, jang ruhiyati), texnologiya va devor mudofaa bonuslari.
- 👹 **PvE Kampaniyalar**: Goblinlar to'dasi, Qaroqchilar qal'asi, Qora ritsarlar istehkomi, Olovli ajdaho g'ori.
- ⚔️ **PvP Arena**: Boshqa real o'yinchilarning saltanatlariga hujum qilish, o'lja olish va 12 soatlik himoya qalqoni mexanikasi.
- 🤝 **Harbiy Ittifoqlar (Klanlar)**: O'z klani yoki ittifoqini tuzish, umumiy klan xazinasiga hissa qo'shish, a'zolar darajasi.
- 📜 **Kundalik Missiyalar**: Avtomatik yangilanuvchi topshiriqlar va resurs mukofotlari.
- 🛡 **Firibgarlikdan Himoya**: Tranzaksiyalar auditi, idempotency kalitlari va ikki marta sarflashdan to'liq server himoyasi.
- ⚡️ **Admin Boshqaruv Paneli**: REST API orqali umumiy statistika, foydalanuvchilar holati va resurs balansi monitoringi.

---

## 🛠 Texnologiyalar Staki

- **Til**: Python 3.12+
- **Telegram Bot**: `aiogram 3.x` (Asinxron routerlar, inline va reply klaviaturalar)
- **Web & Admin API**: `FastAPI` + `Uvicorn`
- **Ma'lumotlar Bazasi**: `SQLAlchemy 2.x` (Async engine)
  - Mahalliy muhitda: `SQLite (aiosqlite)` — nol qaramlik, darhol ishga tushadi
  - Ishlab chiqarish muhitida: `PostgreSQL (asyncpg)`
- **Migratsiyalar**: `Alembic`
- **Kesh**: `Redis` (yoki mahalliy in-memory kesh bilan avtomatik zaxira)
- **Konteynerizatsiya**: `Docker` & `Docker Compose`
- **Testlash**: `Pytest` + `pytest-asyncio` + `httpx`

---

## 📂 Loyiha Strukturasi

```
gameverse/
├── alembic/                  # Baza migratsiyalari (versions, env.py)
├── app/
│   ├── api/                  # FastAPI Admin REST API
│   │   └── admin_routes.py   # Admin boshqaruv marshrutlari
│   ├── bot/                  # Telegram Bot qatlami
│   │   ├── handlers/         # Uzbek tilidagi handlerlar (start, kingdom, ...)
│   │   ├── keyboards/        # Reply & Inline klaviaturalar
│   │   └── middlewares/      # Avtorizatsiya, antispam throttling
│   ├── core/                 # Sozlamalar, DB sessiyalari, xavfsizlik, kesh
│   │   ├── config.py         # Pydantic Settings
│   │   ├── database.py       # Async SQLAlchemy engine
│   │   ├── cache.py          # Redis / in-memory kesh
│   │   └── security.py       # Admin kalitlari va idempotency
│   ├── engine/               # Server-authoritative o'yin hisob-kitoblari
│   │   ├── constants.py      # Bino narxlari, askar xarakteristikalari
│   │   ├── economy.py        # Resurs to'planishi, sarflanish formulalari
│   │   ├── combat.py         # Ko'p bosqichli jang simulyatori
│   │   └── progression.py    # Daraja, tajriba va kubok formulalari
│   ├── models/               # SQLAlchemy 2.x ma'lumotlar modellari
│   │   ├── user.py, kingdom.py, resource.py, building.py, troop.py, ...
│   ├── repositories/         # Asinxron ma'lumotlar ombori (CRUD)
│   └── services/             # Biznes mantiq xizmatlari
├── tests/                    # 20 ta to'liq avtomatlashtirilgan testlar
├── .env.example              # Konfiguratsiya namunasi
├── docker-compose.yml        # PostgreSQL, Redis va App servislari
├── Dockerfile                # Konteyner yaratish ko'rsatmalari
├── main.py                   # FastAPI + Bot yagona start nuqtasi
├── pytest.ini                # Testlash sozlamalari
└── requirements.txt          # Python paketlari ro'yxati
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Muhitni sozlash
Loyihaning `.env` faylini yarating:
```bash
cp .env.example .env
```
`.env` fayliga o'z parametrlaringizni kiriting:
```ini
BOT_TOKEN=123456789:ABCDefghIJKLmnOPQRstuvWXYZ
BOT_USERNAME=MyGameverseBot
ADMIN_API_KEY=adminkey_super_secret_gameverse_2026
```

### 2. Mahalliy muhitda ishga tushirish (Python)
```bash
# Virtual muhitni faollashtiring
source venv/bin/activate  # yoki venv\Scripts\activate (Windows)

# Baza migratsiyalarini yangilash
alembic upgrade head

# Serverni ishga tushirish (Bot va Admin API birga ishlaydi)
python main.py
```

### 3. Docker orqali ishga tushirish (PostgreSQL + Redis)
```bash
docker compose up -d --build
```

---

## 🤖 Telegram Bot yaratish (BotFather orqali)

1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Bot nomini kiriting: masalan, `GAMEVERSE — Qirollik Strategiyasi`.
4. Bot username kiriting: masalan, `GameverseStrategyBot` (oxiri `bot` bilan tugashi shart).
5. BotFather bergan maxfiy **Token**ni ko'chirib oling.
6. Ushbu tokenni `gameverse/.env` faylidagi `BOT_TOKEN` qatoriga yozing:
   ```ini
   BOT_TOKEN=sizning_botfather_tokeningiz
   ```
7. `python main.py` orqali botni ishga tushiring va Telegramda `/start` bosing!

---

## 🧪 Avtomatlashtirilgan Testlarni O'tkazish

Loyiha 100% testlangan va 20 ta test bilan qamrab olingan:
```bash
pytest -v
```
Testlar quyidagilarni to'liq tekshiradi:
- Iqtisodiyot va resurs hisoblash formulalari
- Ko'p bosqichli jang simulyatori va o'lja taqsimoti
- 9 ta asosiy menyu tugmasining Telegram handlerlari
- Admin API avtorizatsiyasi va boshqaruv nuqtalari
- Klanni ro'yxatdan o'tkazish va kundalik missiyalar
