import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
import src.database.veritabani_islemleri as db

# Testler başlamadan önce geçici, RAM üzerinde bir veritabanı kur (Test bitince uçar)
@pytest.fixture(autouse=True)
def test_veritabanini_kur(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db, "Session", TestSession)

def test_kullanici_olusturma_ve_sayma():
    # 2 farklı kullanıcı oluştur
    db.kullanici_getir_veya_olustur(123)
    db.kullanici_getir_veya_olustur(456)
    
    sayi = db.kullanici_sayisini_getir()
    assert sayi == 2

def test_mesaj_kaydetme_ve_gecmis_getirme():
    # Kullanıcı 789 için 2 mesaj kaydet
    db.kullanici_getir_veya_olustur(789)
    db.mesaj_kaydet(789, "user", "Selam")
    db.mesaj_kaydet(789, "assistant", "Merhaba, nasılsın?")
    
    # Geçmişi çağır
    gecmis = db.gecmis_mesajlari_getir(789)
    
    assert len(gecmis) == 2
    assert gecmis[0]["content"] == "Selam"
    assert gecmis[1]["role"] == "assistant"