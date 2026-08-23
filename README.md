# 🤖 Telegram AI Bot Backend (SOLID Architecture)

Bu proje, Telegram arayüzünü kullanarak dış yapay zeka (LLM) servisleriyle veya yerel modellerle (Ollama/Qwen vb.) haberleşen, tamamen modüler ve SOLID prensiplerine uygun tasarlanmış bir arka uç (backend) sistemidir.

## 🏗 Mimari Yapı

Proje, Tek Sorumluluk Prensibi (SRP) gözetilerek 4 ana katmana bölünmüştür:
- **Controller (`main.py` & `api_yoneticisi.py`):** Telegram Webhook'tan gelen veriyi karşılar ve alt servislere dağıtır.
- **Middleware (`kural_denetleyici.py`):** RAM üzerinde spam kontrolü ve günlük token/mesaj limiti denetimi yapar.
- **Services:** 
  - `prompt_olusturucu.py`: Geçmiş özetini ve yeni mesajı LLM formatına dönüştürür.
  - `mesaj_ozetleyici.py`: Token limitini korumak için eski mesajları arkaplanda özetler.
  - `llm_istek.py`: Dış API ile HTTP haberleşmesini yönetir (Hata toleransı içerir).
- **Database (`models.py` & `veritabani_islemleri.py`):** SQLAlchemy ORM kullanılarak sadece kısa/uzun belleğin (mesaj geçmişi ve özetler) kalıcı kaydını tutar.

## 🚀 Kurulum ve Çalıştırma

1. **Projeyi Klonlayın:**
   ```bash
   git clone [https://github.com/kullaniciadin/telegram-ai-bot.git](https://github.com/kullaniciadin/telegram-ai-bot.git)
   cd telegram-ai-bot