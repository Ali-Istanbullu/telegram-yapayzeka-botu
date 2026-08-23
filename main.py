from fastapi import FastAPI, Request
from src.controller.api_yoneticisi import telegram_mesajini_isle
import httpx
import os
from dotenv import load_dotenv
from logger import logger 

load_dotenv() 

app = FastAPI(title="Sanal Arkadaş API")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "senin_bot_tokenin")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

@app.post("/webhook")
async def telegram_webhook(request: Request):
    logger.info("----- YENİ MESAJ TETİKLENDİ -----")
    try:
        veri = await request.json()
        
        if "message" in veri and "text" in veri["message"]:
            kullanici_mesaji = veri["message"]["text"]
            telegram_id = veri["message"]["chat"]["id"]
            
            logger.info(f"Mesaj alındı - Kullanıcı: {telegram_id}")

            ai_cevabi = telegram_mesajini_isle(telegram_id, kullanici_mesaji)
            
            await telegrama_mesaj_gonder(telegram_id, ai_cevabi)
            logger.info(f"Cevap başarıyla gönderildi - Kullanıcı: {telegram_id}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"WEBHOOK BÜYÜK HATA: {e}", exc_info=True)
        return {"status": "error"}

async def telegrama_mesaj_gonder(chat_id, metin):
    try:
        payload = {"chat_id": chat_id, "text": metin}
        async with httpx.AsyncClient() as client:
            await client.post(TELEGRAM_API_URL, json=payload)
    except Exception as e:
        logger.error(f"Telegrama mesaj gönderilirken hata: {e}")