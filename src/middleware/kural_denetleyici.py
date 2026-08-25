import datetime


# RAM (Bellek) üzerinde yaşayacak geçici durum sözlüğü.
# NOT: Sadece "spam kilidi" için kullanılıyor - bu bilgi tek bir mesajın işlenmesi
# süresince yaşayan, saniyelik bir durum olduğu için RAM'de kalması sorun değil.
# Günlük kota ARTIK BURADA DEĞİL - kalıcı olması gerektiği için veritabanında tutuluyor.
aktif_islemler = {}  
# Format: {telegram_id: True/False} -> True ise sistem o an o kişiye cevap üretiyordur.

OZETLEME_SINIRI = 10
GUNLUK_LIMIT = 25
MAKSIMUM_KULLANICI_KAPASITESI = 3 # SOLID: Sabitler (Magic Numbers) her zaman en üstte tanımlanır

def kilit_ve_sinir_kontrolu(telegram_id, toplam_kullanici, kayitli_mi, bugunku_kullanim):
    """
    Kullanıcının mesaj atma hakkı olup olmadığını ve o an işlemde olup olmadığını denetler.
    
    bugunku_kullanim: API'nin veritabanından okuyup gönderdiği {"sayi": int, "tarih": str|None} bilgisi.
    Dönüş: (izin_verildi_mi, mesaj_veya_devam, guncel_kullanim_durumu)
           guncel_kullanim_durumu, API'nin işlem sonunda DB'ye yazması için geri veriliyor.
    """
    bugun = datetime.date.today().isoformat()
    
    # --- KAPASİTE KONTROLÜ ---
    if kayitli_mi is False: 
        if toplam_kullanici >= MAKSIMUM_KULLANICI_KAPASITESI:
             return False, "Kapasitemiz doldu! Kendi ücretsiz yapay zeka botunu kurmak için açık kaynak kodlarımızı ve kurulum rehberini inceleyebilirsin: https://github.com/senin-kullanici-adin/senin-repon", None
    # ----------------------------------------------------

    # 1. Günlük Limit Kontrolü ve Otomatik Tarih Sıfırlaması (artık DB'den gelen veriyle)
    if bugunku_kullanim["tarih"] != bugun:
        kullanici_durumu = {"sayi": 0, "tarih": bugun}
    else:
        kullanici_durumu = dict(bugunku_kullanim)
        
    if kullanici_durumu["sayi"] >= GUNLUK_LIMIT:
        return False, "Bugünlük mesaj limitin doldu. Yarın tekrar görüşürüz!", kullanici_durumu

    # 2. Spam / Kilit Kontrolü (RAM'de kalmaya devam ediyor, çok kısa ömürlü)
    if aktif_islemler.get(telegram_id) == True:
        return False, "Şu an sana cevap hazırlıyorum, lütfen bekle...", kullanici_durumu

    aktif_islemler[telegram_id] = True
    
    return True, "Devam", kullanici_durumu

def islem_basarili_kilidi_ac(telegram_id, kullanim_durumu):
    """
    Yapay zeka başarılı bir şekilde cevap döndüğünde API yöneticisi bunu çağırır.
    Kilidi açar ve günlük kullanım sayısını 1 artırıp API'ye geri döner ki
    API bunu veritabanına yazsın (kural_denetleyici veritabanına kendi dokunmaz).
    """
    if telegram_id in aktif_islemler:
        aktif_islemler[telegram_id] = False

    return {"sayi": kullanim_durumu["sayi"] + 1, "tarih": kullanim_durumu["tarih"]}


def hata_durumunda_kilidi_ac(telegram_id):
    """
    Eğer dışarıdaki LLM API'si çökerse veya timeout yersen API yöneticisi bunu çağırır.
    Kullanıcının kotasından HARCAMADAN sadece kilidi açar ki kullanıcı tekrar deneyebilsin.
    """
    if telegram_id in aktif_islemler:
        aktif_islemler[telegram_id] = False


def ozetleme_gerekli_mi(mevcut_mesaj_sayisi):
    """
    Sadece API Yöneticisinden (Orkestra Şefinden) gelen sayıyı alır.
    Mesaj sayısı sınırı aştıysa özetleme iznini (True) verir, aşmadıysa (False) döner.
    Hiçbir veritabanına bağlanmaz!
    """
    if mevcut_mesaj_sayisi >= OZETLEME_SINIRI:
        return True
    return False        