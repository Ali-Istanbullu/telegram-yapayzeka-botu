import os
from dotenv import load_dotenv # BUNU EKLEDİK
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Kullanici, Mesaj
from logger import logger

# Önce .env dosyasını zorla okutuyoruz ki sistem boşluğa düşmesin
load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False)



def kullanici_sayisini_getir():
    session = Session()
    try:
        return session.query(Kullanici).count()
    except Exception as e:
        logger.error(f"Kullanıcı sayısı getirilirken DB hatası: {e}", exc_info=True)
        return 999
    finally:
        session.close()

def kullanici_getir_veya_olustur(telegram_id):
    session = Session()
    try:
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if not kullanici:
            kullanici = Kullanici(telegram_id=telegram_id)
            session.add(kullanici)
            session.commit()
        return kullanici
    except Exception as e:
        session.rollback()
        logger.error(f"Kullanıcı oluşturulurken hata (ID: {telegram_id}): {e}", exc_info=True)
        return None
    finally:
        session.close()

def kullanici_kayitli_mi(telegram_id):
    """
    Kullanıcı daha önce sisteme kayıt olmuş mu diye SADECE okur, asla oluşturmaz.
    Kapasite kontrolünde 'bu gerçekten yeni biri mi' sorusuna RAM'e değil
    veritabanına sorarak doğru cevap vermek için var.
    """
    session = Session()
    try:
        return session.query(Kullanici).filter_by(telegram_id=telegram_id).first() is not None
    except Exception as e:
        logger.error(f"Kullanıcı kayıt kontrolünde hata (ID: {telegram_id}): {e}", exc_info=True)
        # DİKKAT: False DÖNMEZ! False burada "kesinlikle yeni kullanıcı" demek ve
        # mevcut bir müşteriyi yanlışlıkla "kapasite doldu"ya sokabilir.
        # None = "bilmiyorum", kural_denetleyici bunu ayrıca ele alır.
        return None
    finally:
        session.close()

def mesaj_kaydet(telegram_id, rol, icerik):
    session = Session()
    try:
        yeni_mesaj = Mesaj(telegram_id=telegram_id, rol=rol, icerik=icerik)
        session.add(yeni_mesaj)
        session.commit()
    except Exception as e:
        session.rollback() 
        logger.error(f"Mesaj kaydedilirken hata (ID: {telegram_id}): {e}", exc_info=True)
    finally:
        session.close()

def gecmis_mesajlari_getir(telegram_id, limit=6):
    session = Session()
    try:
        # Kullanıcının tüm mesajlarını çekip Python'da kesmek yerine,
        # sıralama ve sınırlamayı veritabanına yaptırıyoruz.
        son_mesajlar = (
            session.query(Mesaj)
            .filter_by(telegram_id=telegram_id)
            .order_by(Mesaj.olusturulma_tarihi.desc(), Mesaj.id.desc())
            .limit(limit)
            .all()
        )
        son_mesajlar.reverse()  # DB'den ters (yeni->eski) geldi, kronolojik sıraya çeviriyoruz

        return [{"role": msg.rol, "content": msg.icerik} for msg in son_mesajlar]
    except Exception as e:
        logger.error(f"Geçmiş mesajlar getirilirken hata (ID: {telegram_id}): {e}", exc_info=True)
        return []
    finally:
        session.close()

def gecmisi_temizle(telegram_id):
    """
    Sadece kısa belleği (mesajlar tablosunu) temizler.
    Özet alanına DOKUNMAZ — onun tek sahibi ozeti_guncelle fonksiyonudur.
    """
    session = Session()
    try:
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if kullanici:
            kullanici.mesajlar.clear()     
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Geçmiş temizlenirken hata (ID: {telegram_id}): {e}", exc_info=True)
    finally:
        session.close()

def ozeti_guncelle(telegram_id, yeni_ozet):
    session = Session()
    try:
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if kullanici:
            kullanici.konusma_ozeti = yeni_ozet
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Özet güncellenirken hata (ID: {telegram_id}): {e}", exc_info=True)
    finally:
        session.close()

def gunluk_kullanim_getir(telegram_id):
    """
    SADECE okur, oluşturmaz. Kullanıcının bugünkü mesaj sayısını ve
    son kullanım tarihini DB'den getirir. Kota artık RAM'de değil,
    burada kalıcı - restart olsa da kaybolmaz.
    """
    session = Session()
    try:
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if not kullanici:
            return {"sayi": 0, "tarih": None}
        return {"sayi": kullanici.gunluk_mesaj_sayisi or 0, "tarih": kullanici.gunluk_tarih}
    except Exception as e:
        logger.error(f"Günlük kullanım getirilirken hata (ID: {telegram_id}): {e}", exc_info=True)
        return {"sayi": 0, "tarih": None}
    finally:
        session.close()

def gunluk_kullanim_guncelle(telegram_id, yeni_sayi, yeni_tarih):
    """Günlük mesaj sayısını ve tarihini DB'ye yazar."""
    session = Session()
    try:
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if kullanici:
            kullanici.gunluk_mesaj_sayisi = yeni_sayi
            kullanici.gunluk_tarih = yeni_tarih
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Günlük kullanım güncellenirken hata (ID: {telegram_id}): {e}", exc_info=True)
    finally:
        session.close()