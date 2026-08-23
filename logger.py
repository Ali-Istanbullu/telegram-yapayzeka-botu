import logging
from logging.handlers import RotatingFileHandler
import os

# Logların tutulacağı klasörü oluştur (Eğer yoksa)
if not os.path.exists("logs"):
    os.makedirs("logs")

# Logger nesnemizi oluşturuyoruz
logger = logging.getLogger("SanalArkadasBot")
logger.setLevel(logging.INFO)

# RotatingFileHandler: Maksimum 1 MB boyutunda dosya yapar, sadece son 3 dosyayı tutar.
# Bu sayede sunucu hafızası asla dolmaz!
handler = RotatingFileHandler(
    "logs/sistem_loglari.log", maxBytes=1048576, backupCount=3, encoding="utf-8"
)

# Profesyonel log formatı: Yıl-Ay-Gün Saat - Dosya/Modül - Hata Tipi - Mesaj Detayı
formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Handler'ı logger'a ekliyoruz (Çift eklemeyi önlemek için kontrol ediyoruz)
if not logger.handlers:
    logger.addHandler(handler)