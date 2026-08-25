import logging
from logging.handlers import RotatingFileHandler
import sys
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("SanalArkadasBot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')

# 1) Dosyaya yaz (local geliştirme için hâlâ faydalı)
dosya_handler = RotatingFileHandler(
    "logs/sistem_loglari.log", maxBytes=1048576, backupCount=3, encoding="utf-8"
)
dosya_handler.setFormatter(formatter)

# 2) stdout'a da yaz - Render (ve genel olarak her PaaS) sadece stdout/stderr'i
# canlı log ekranında gösterir. Bu handler olmadan üretimdeki hiçbir
# logger.error()/warning() çağrısı hiçbir yerde görünmüyordu.
konsol_handler = logging.StreamHandler(sys.stdout)
konsol_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(dosya_handler)
    logger.addHandler(konsol_handler)