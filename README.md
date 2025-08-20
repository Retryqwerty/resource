
# Geo Backend (Render-ready)

## Files in repo root
- main.py
- requirements.txt
- Dockerfile

## Local test
```
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deploy on Render
1. Створи порожній GitHub-репозиторій (наприклад, geo-backend).
2. Завантаж ці три файли в **корінь** репозиторію.
3. На render.com → New → Web Service → підключи цей репозиторій.
4. Render сам побачить `Dockerfile`. Тисни **Create Web Service**.
5. Дочекайся статусу **Live**. Ти отримаєш URL типу `https://<name>.onrender.com`.

## Endpoints
- POST /scan  { "lat": 50.45, "lon": 30.52, "precision": 7 }
- POST /claim { "user": "demo", "cell": "<geohash>" }
- GET  /claims

## Note
SQLite (`game.db`) зберігається в контейнері. Для продакшена краще Render Disk або зовнішню БД.
