def prompt_hazirla(kullanici_mesaji, ozet_metni=None, son_mesajlar=None):
    """
    Sistem karakterini, konuşma özetini (uzun bellek), son mesajları (kısa bellek) 
    ve yeni mesajı birleştirerek LLM API'sine gönderilecek JSON (liste) paketini oluşturur.
    """
    
    # Parametre boş gelirse hata vermemesi için boş liste ataması
    if son_mesajlar is None:
        son_mesajlar = []

    # 1. Ana Karakterimiz (Persona)
    # Bu kısmı ileride botun karakterini değiştirmek istersen güncelleyebilirsin.
        ana_karakter = (
        "Sen samimi, esprili ve yardımsever bir sanal arkadaşsın. "
        "Karşısındakiyle resmi olmayan, günlük bir dille sohbet edersin. "
        "Cevapların KISA ve doğal olsun - gerçek bir arkadaş gibi birkaç cümleyle "
        "konuş, uzun paragraflar veya başlıklı listeler yazma. "
        "Kendi düşünme sürecini, planını veya iç muhakemeni ASLA gösterme - "
        "sadece doğrudan son cevabı yaz, 'Answer:' ya da 'What I did:' gibi "
        "meta açıklamalar ekleme. "
        "Eğer sana geçmiş konularla ilgili bir şey sorulursa, aşağıdaki 'Geçmiş Konuşma Özeti'ni "
        "kendi anılarınmış gibi kabul ederek cevap ver."
    )

    # 2. Uzun Bellek (Özet) Entegrasyonu
    # Eğer veritabanından bir özet metni gelmişse, bunu "System" komutunun içine gizliyoruz.
    if ozet_metni:
        sistem_mesaji = f"{ana_karakter}\n\nGeçmiş Konuşma Özeti:\n{ozet_metni}"
    else:
        sistem_mesaji = ana_karakter

    # 3. Paketlemenin Başlangıcı: Sistem Mesajı en üste konur
    mesaj_paketi = [
        {"role": "system", "content": sistem_mesaji}
    ]

    # 4. Kısa Bellek: Veritabanından gelen son mesajlar araya eklenir
    # Format zaten uygun geldiği için doğrudan extend ediyoruz 
    # Örn: [{"role": "user", "content": "Selam"}, {"role": "assistant", "content": "Naber?"}]
    mesaj_paketi.extend(son_mesajlar)

    # 5. Güncel Mesaj: Kullanıcının Telegram'dan attığı yepyeni mesaj en alta eklenir
    mesaj_paketi.append(
        {"role": "user", "content": kullanici_mesaji}
    )

    return mesaj_paketi