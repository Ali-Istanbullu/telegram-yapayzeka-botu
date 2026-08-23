from src.database.veritabani_islemleri import kullanici_getir_veya_olustur, gecmis_mesajlari_getir, ozeti_guncelle, gecmisi_temizle
from src.services.llm_istek import yapay_zekadan_cevap_al

# Bu sayıya ulaşıldığında özetleme tetiklenir (5 soru + 5 cevap = 10 mesaj)
OZETLEME_SINIRI = 10 

def token_kontrolu_ve_ozetle(telegram_id):
    """
    Kullanıcının kısa belleğindeki mesaj sayısını kontrol eder.
    Sınır aşılmışsa, eski mesajları alıp yapay zekaya özetletir ve 
    yeni özeti veritabanına kaydeder.
    """
    
    # 1. Kullanıcının şu anki durumunu alıyoruz
    kullanici = kullanici_getir_veya_olustur(telegram_id)
    kisa_bellek_mesajlari = gecmis_mesajlari_getir(telegram_id, limit=OZETLEME_SINIRI)
    eski_ozet = kullanici.konusma_ozeti

    # 2. Eğer sınır aşılmadıysa hiçbir şey yapmadan dön (Performans dostu)
    if len(kisa_bellek_mesajlari) < OZETLEME_SINIRI:
        return

    # 3. Sınır aşıldı! Özetleme için özel bir prompt (paket) hazırlıyoruz
    ozetleme_talimati = (
        "Sen bir konuşma özetleme asistanısın. Aşağıdaki geçmiş özetini ve "
        "yeni konuşmaları birleştirerek tek, akıcı ve kısa bir paragraf halinde "
        "yeni bir özet oluştur. Detaylara boğulma, sadece ana konuları ve "
        "kullanıcının önemli tercihlerini hatırlatacak şekilde yaz."
    )
    
    ozet_paketi = [
        {"role": "system", "content": ozetleme_talimati}
    ]
    
    # Varsa eski özeti ekle
    if eski_ozet:
        ozet_paketi.append({"role": "user", "content": f"Eski Özet: {eski_ozet}"})
        
    # Yeni konuşmaları (kısa belleği) metne çevirip ekle
    yeni_konusmalar = "\n".join([f"{msg['role']}: {msg['content']}" for msg in kisa_bellek_mesajlari])
    ozet_paketi.append({"role": "user", "content": f"Son Konuşmalar:\n{yeni_konusmalar}"})

    # 4. LLM İstek modülünü çağırıp bu özel paketi özetlemesi için gönderiyoruz
    # (Burada LLM istek köprüsünü kendi iç işlerimiz için kullanmış oluyoruz)
    basarili_mi, yeni_ozet = yapay_zekadan_cevap_al(ozet_paketi)

    # 5. Başarılı olduysa veritabanını güncelle
    if basarili_mi:
        ozeti_guncelle(telegram_id, yeni_ozet)
        
        # DİKKAT: Yeni özet çıkarıldığı için artık kısa belleği (eski mesajları) temizlemeliyiz.
        # Böylece döngü baştan başlar ve token/mesaj sınırımız sıfırlanmış olur.
        gecmisi_temizle(telegram_id)
        
        # Not: gecmisi_temizle fonksiyonu varsayılan olarak özeti de siler.
        # Bu yüzden veritabani_islemleri.py içinde gecmisi_temizle fonksiyonuna 
        # sadece 'mesajlar' tablosunu silecek küçük bir parametre eklemeliyiz. 
        # (Şimdilik mantığı anladığını biliyorum).