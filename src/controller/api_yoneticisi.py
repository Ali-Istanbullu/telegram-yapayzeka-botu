from logger import logger
from src.middleware.kural_denetleyici import (
    kilit_ve_sinir_kontrolu, 
    islem_basarili_kilidi_ac, 
    hata_durumunda_kilidi_ac,
    ozetleme_gerekli_mi,  # Yargıca özetleme lazım mı diye sorma kuralı
    OZETLEME_SINIRI       # YENİ: "Kaç mesaj çekilecek" sayısı artık tek kaynaktan geliyor
)
from src.database.veritabani_islemleri import (
    kullanici_sayisini_getir, 
    kullanici_kayitli_mi,
    kullanici_getir_veya_olustur, 
    mesaj_kaydet, 
    gecmis_mesajlari_getir,
    gecmisi_temizle,          # API'nin elleriyle temizlik yapması için
    ozeti_guncelle,           # API'nin elleriyle özet yazması için
    gunluk_kullanim_getir,    # YENİ: günlük kotayı DB'den oku
    gunluk_kullanim_guncelle  # YENİ: günlük kotayı DB'ye yaz
)

from src.services.prompt_olusturucu import prompt_hazirla
from src.services.llm_istek import yapay_zekadan_cevap_al
from src.services.mesaj_ozetleyici import ozet_paketi_hazirla # YENİ: Sadece paket sarıcı!

def telegram_mesajini_isle(telegram_id, kullanici_mesaji):
    """
    Sistemin yegane Orkestra Şefi. 
    Tüm modüller bu dosyaya hizmet eder, hiçbir modül birbiriyle direkt konuşmaz.
    """
    
        # 1. GÜVENLİK KONTROLÜ (Yargıca Sor)
    toplam_kullanici = kullanici_sayisini_getir()
    kayitli_mi = kullanici_kayitli_mi(telegram_id)
    bugunku_kullanim = gunluk_kullanim_getir(telegram_id)  # DB'den oku, RAM'e güvenme
    izin_verildi_mi, sistem_mesaji, kullanim_durumu = kilit_ve_sinir_kontrolu(
        telegram_id, toplam_kullanici, kayitli_mi, bugunku_kullanim
    )
    if not izin_verildi_mi:
        return sistem_mesaji

        # 2. VERİTABANI YAZMA'DAN İTİBAREN HER ŞEY GÜVENCE ALTINDA
    # Kilit zaten açıldı (adım 1'de). Burada patlayan HERHANGİ bir hata
    # kullanıcıyı kalıcı kilitli bırakmasın diye tüm süreç try/except içinde.
    try:
        # 2. VERİTABANI YAZMA
        kullanici = kullanici_getir_veya_olustur(telegram_id)
        mesaj_kaydet(telegram_id, rol="user", icerik=kullanici_mesaji)

        # =========================================================================
        # 3. ÖZETLEME / TOKEN YÖNETİMİ
        # =========================================================================
        kisa_bellek = gecmis_mesajlari_getir(telegram_id, limit=OZETLEME_SINIRI)
        mevcut_mesaj_sayisi = len(kisa_bellek)

        if ozetleme_gerekli_mi(mevcut_mesaj_sayisi):

            eski_ozet = kullanici.konusma_ozeti

            ozet_paketi = ozet_paketi_hazirla(eski_ozet, kisa_bellek)
            # Özetleme, yaratıcılık değil sadakat ister - düşük sıcaklık kullanıyoruz.
            basarili_mi_ozet, yeni_ozet = yapay_zekadan_cevap_al(ozet_paketi, sicaklik=0.3)

            if basarili_mi_ozet:
                gecmisi_temizle(telegram_id)
                ozeti_guncelle(telegram_id, yeni_ozet)

                # Veritabanı temizlendiği için aşağıda hata çıkmasın diye kullanıcıyı tazele!
                kullanici = kullanici_getir_veya_olustur(telegram_id)

                # Temizlik, bu turun kullanıcı mesajını da sildi (içeriği zaten özete işlendi).
                # Geçmişin karşılıksız bir "assistant" mesajıyla başlamaması için
                # bu turun kullanıcı mesajını temizlenmiş tabloya yeniden yazıyoruz.
                mesaj_kaydet(telegram_id, rol="user", icerik=kullanici_mesaji)
        # =========================================================================

        # 4. HAFIZAYI ÇAĞIRMA (Normal Cevap Süreci)
        ozet_metni = kullanici.konusma_ozeti
        son_mesajlar = gecmis_mesajlari_getir(telegram_id)

        # 5. PAKETLEME (Beyin)
        hazir_paket = prompt_hazirla(kullanici_mesaji, ozet_metni, son_mesajlar)

        # 6. DIŞ DÜNYAYA GÖNDERİM (Köprü)
        basarili_mi, ai_cevabi = yapay_zekadan_cevap_al(hazir_paket)

                # 7. SONUÇLANDIRMA VE TEMİZLİK
        if basarili_mi:
            mesaj_kaydet(telegram_id, rol="assistant", icerik=ai_cevabi)
            yeni_kullanim_durumu = islem_basarili_kilidi_ac(telegram_id, kullanim_durumu)
            gunluk_kullanim_guncelle(telegram_id, yeni_kullanim_durumu["sayi"], yeni_kullanim_durumu["tarih"])
        else:
            hata_durumunda_kilidi_ac(telegram_id)

        return ai_cevabi

    except Exception as e:
        # Beklenmedik HERHANGİ bir hata: kilidi mutlaka aç, kullanıcı tekrar deneyebilsin.
        logger.error(f"Orkestra Şefinde beklenmedik hata (ID: {telegram_id}): {e}", exc_info=True)
        hata_durumunda_kilidi_ac(telegram_id)
        return "Sistemde beklenmedik bir hata oluştu. Lütfen tekrar dener misin?"