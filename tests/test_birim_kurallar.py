import pytest
from src.middleware.kural_denetleyici import kilit_ve_sinir_kontrolu, aktif_islemler, gunluk_kullanim
from src.services.prompt_olusturucu import prompt_hazirla

# --- KURAL DENETLEYİCİ TESTLERİ ---
def test_kapasite_siniri(monkeypatch):
    # Veritabanını yormadan, DB'den 3 (sınır) dönmüş gibi simüle ediyoruz (Mocking)
    monkeypatch.setattr("src.middleware.kural_denetleyici.kullanici_sayisini_getir", lambda: 3)
    
    # Sisteme ilk defa giren bir ID
    izin, mesaj = kilit_ve_sinir_kontrolu(999999)
    
    assert izin is False
    assert "Kapasitemiz doldu" in mesaj

def test_kilit_sistemi(monkeypatch):
    monkeypatch.setattr("src.middleware.kural_denetleyici.kullanici_sayisini_getir", lambda: 1)
    
    # İlk mesaj: İzin vermeli ve kilitlemeli
    izin1, _ = kilit_ve_sinir_kontrolu(111)
    assert izin1 is True
    assert aktif_islemler[111] is True

    # İkinci mesaj (kilit açılmadan): Reddetmeli
    izin2, mesaj2 = kilit_ve_sinir_kontrolu(111)
    assert izin2 is False
    assert "lütfen bekle" in mesaj2

# --- PROMPT OLUŞTURUCU TESTLERİ ---
def test_prompt_hazirlama_temel():
    mesaj = "Merhaba dünya"
    paket = prompt_hazirla(mesaj)
    
    assert len(paket) == 2 # System ve User
    assert paket[1]["role"] == "user"
    assert paket[1]["content"] == "Merhaba dünya"