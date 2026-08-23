import datetime
from src.database.veritabani_islemleri import kullanici_sayisini_getir, kullanici_getir_veya_olustur

# RAM (Bellek) üzerinde yaşayacak geçici durum sözlükleri
aktif_islemler = {}  
# Format: {telegram_id: True/False} -> True ise sistem o an o kişiye cevap üretiyordur.

gunluk_kullanim = {} 
# Format: {telegram_id: {"sayi": 15, "tarih": "2026-08-22"}} 
# Tarihi de tutuyoruz ki gece 00:00 olduğunda veritabanı sıfırlamasıyla uğraşmadan kotayı otomatik yenileyelim.

GUNLUK_LIMIT = 25
MAKSIMUM_KULLANICI_KAPASITESI = 3 # SOLID: Sabitler (Magic Numbers) her zaman en üstte tanımlanır

def kilit_ve_sinir_kontrolu(telegram_id):
    """Kullanıcının mesaj atma hakkı olup olmadığını ve o an işlemde olup olmadığını denetler."""
    bugun = datetime.date.today().isoformat()
    
    # --- YENİ EKLENEN KAPASİTE KONTROLÜ BURADA OLMALI ---
    # Eğer adam daha önce kaydolmuşsa (RAM'de varsa) sıkıntı yok, sayıma girmez.
    if telegram_id not in gunluk_kullanim: 
        mevcut_kisi_sayisi = kullanici_sayisini_getir()
        if mevcut_kisi_sayisi >= MAKSIMUM_KULLANICI_KAPASITESI:
             return False, "Kapasitemiz doldu! Kendi ücretsiz yapay zeka botunu kurmak için açık kaynak kodlarımızı ve kurulum rehberini inceleyebilirsin: https://github.com/senin-kullanici-adin/senin-repon"
    # ----------------------------------------------------

    # 1. Günlük Limit Kontrolü ve Otomatik Tarih Sıfırlaması
    kullanici_durumu = gunluk_kullanim.get(telegram_id, {"sayi": 0, "tarih": bugun})
    
    # Eğer yeni bir güne girilmişse sayacı sıfırla
    if kullanici_durumu["tarih"] != bugun:
        kullanici_durumu = {"sayi": 0, "tarih": bugun}
        
    if kullanici_durumu["sayi"] >= GUNLUK_LIMIT:
        return False, "Bugünlük mesaj limitin doldu. Yarın tekrar görüşürüz!"

    # 2. Spam / Kilit Kontrolü
    if aktif_islemler.get(telegram_id) == True:
        return False, "Şu an sana cevap hazırlıyorum, lütfen bekle..."

    # Her iki testten de geçildiyse: Kullanıcıya kilidi vur ki art arda mesaj atamasın
    aktif_islemler[telegram_id] = True
    gunluk_kullanim[telegram_id] = kullanici_durumu # RAM'deki sözlüğü güncelle
    
    return True, "Devam"


def islem_basarili_kilidi_ac(telegram_id):
    """
    Yapay zeka başarılı bir şekilde cevap döndüğünde API yöneticisi bunu çağırır.
    Kilidi açar ve kullanıcının günlük kotasını 1 düşürür (sayıyı 1 artırır).
    """
    if telegram_id in aktif_islemler:
        aktif_islemler[telegram_id] = False
        
    if telegram_id in gunluk_kullanim:
        gunluk_kullanim[telegram_id]["sayi"] += 1


def hata_durumunda_kilidi_ac(telegram_id):
    """
    Eğer dışarıdaki LLM API'si çökerse veya timeout yersen API yöneticisi bunu çağırır.
    Kullanıcının kotasından HARCAMADAN sadece kilidi açar ki kullanıcı tekrar deneyebilsin.
    """
    if telegram_id in aktif_islemler:
        aktif_islemler[telegram_id] = False