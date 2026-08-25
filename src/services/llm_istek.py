import os
import requests
from logger import logger

def yapay_zekadan_cevap_al(mesaj_paketi, sicaklik=0.7):
    API_URL = os.getenv("LLM_API_URL")
    API_KEY = os.getenv("LLM_API_KEY")
    MODEL_ADI = os.getenv("LLM_MODEL_NAME")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ADI,
        "messages": mesaj_paketi,
        "temperature": sicaklik
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Groq Reddedildi! Kod: {response.status_code}, Sebep: {response.text}")

        response.raise_for_status()
        veri = response.json()
        return True, veri["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        logger.warning("Yapay zeka API Timeout yedi.")
        return False, "Yapay zeka şu an çok yoğun, zaman aşımına uğradı. Birazdan tekrar dener misin?"
    except Exception as e:
        logger.error(f"Yapay zeka API bağlantı hatası: {e}")
        return False, "Sistemde geçici bir bağlantı sorunu var. Lütfen daha sonra tekrar dene."+{str(e)}