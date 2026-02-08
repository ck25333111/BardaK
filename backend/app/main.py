#────────────────────────────────────────
# backend/app/main.py
# Точка входа FastAPI
#────────────────────────────────────────

from fastapi import FastAPI

app = FastAPI(title="BardaK API")

@app.get("/health")
async def health():
    return {"status": "ok"}
