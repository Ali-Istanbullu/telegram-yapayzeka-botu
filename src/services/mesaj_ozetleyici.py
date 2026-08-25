# DİKKAT: HİÇBİR İMPORT YOK! Ne veritabanı ne LLM. Sadece metin işler.

def ozet_paketi_hazirla(eski_ozet, kisa_bellek_mesajlari):
    """
    API yöneticisinden eski özeti ve geçmiş mesajları alır.
    LLM'in özet çıkarma işleminde kullanacağı listeyi (paketi) hazırlayıp 
    API yöneticisine geri verir. LLM'e kendi gitmez!
    """
    
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

    # Paketi LLM'e göndermiyoruz, Orkestra Şefine (API'ye) geri veriyoruz!
    return ozet_paketi