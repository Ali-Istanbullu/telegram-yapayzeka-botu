import os
import importlib
import pytest

def test_kritik_kutuphaneler_yuklu_mu():
    kutuphaneler = ["fastapi", "uvicorn", "sqlalchemy", "requests", "httpx", "dotenv"]
    for kutuphane in kutuphaneler:
        try:
            importlib.import_module(kutuphane)
        except ImportError:
            pytest.fail(f"KRİTİK BAĞIMLILIK EKSİK: {kutuphane} kurulu değil!")

def test_env_degiskenleri_tanimli_mi():
    # CI/CD ortamında hata vermemesi için sadece varlıklarını veya varsayılan değerleri kontrol et
    assert os.getenv("TELEGRAM_BOT_TOKEN", None) is not None