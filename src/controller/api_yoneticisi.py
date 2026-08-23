from src.middleware.kural_denetleyici import kilit_ve_sinir_kontrolu, islem_basarili_kilidi_ac, hata_durumunda_kilidi_ac
from src.database.veritabani_islemleri import kullanici_getir_veya_olustur, mesaj_kaydet, gecmis_mesajlari_getir
from src.services.prompt_olusturucu import prompt_hazirla
from src.services.llm_istek import yapay_zekadan_cevap_al
# from src.services.mesaj_ozetleyici import token_kontrolu_ve_ozetle (Bunu bir sonraki adımda yazacağız)

def telegram_mesajini_isle(telegram_id, kullanici_mesaji):
    """
    Telegram'dan gelen her yeni mesajın girdiği ana fonksiyondur.
    Tüm modülleri sırasıyla yönetir.
    """
    
    # 1. GÜVENLİK KONTROLÜ (Ara Katman)
    izin_verildi_mi, sistem_mesaji = kilit_ve_sinir_kontrolu(telegram_id)
    if not izin_verildi_mi:
        # Eğer kilitliyse veya kota dolduysa direkt Telegram'a uyarıyı yolla ve işlemi kes
        return sistem_mesaji

    # 2. VERİTABANI: Kullanıcıyı bul ve attığı mesajı kaydet
    kullanici = kullanici_getir_veya_olustur(telegram_id)
    mesaj_kaydet(telegram_id, rol="user", icerik=kullanici_mesaji)

    # 3. ÖZETLEME KONTROLÜ (Burayı şimdilik sembolik bırakıyoruz, özetleyici dosyasında içini dolduracağız)
    # token_kontrolu_ve_ozetle(telegram_id)

    # 4. HAFIZAYI ÇAĞIRMA
    # (Uzun bellek) Kullanıcının tablodaki özetini al
    ozet_metni = kullanici.konusma_ozeti 
    # (Kısa bellek) Son konuşmaları getir
    son_mesajlar = gecmis_mesajlari_getir(telegram_id) 

    # 5. PAKETLEME (Beyin)
    hazir_paket = prompt_hazirla(kullanici_mesaji, ozet_metni, son_mesajlar)

    # 6. DIŞ DÜNYAYA GÖNDERİM (Köprü)
    basarili_mi, ai_cevabi = yapay_zekadan_cevap_al(hazir_paket)

    # 7. SONUÇLANDIRMA VE TEMİZLİK
    if basarili_mi:
        # Yapay zekanın cevabını veritabanına kaydet
        mesaj_kaydet(telegram_id, rol="assistant", icerik=ai_cevabi)
        # İşlem bitti, kilidi aç ve kotayı düş
        islem_basarili_kilidi_ac(telegram_id)
    else:
        # Hata olduysa hakkını yeme, sadece kilidi aç (ai_cevabi burada hata metnidir)
        hata_durumunda_kilidi_ac(telegram_id)

    # En son, Telegram'ın kullanıcıya göstermesi için metni geri döndür
    return ai_cevabi