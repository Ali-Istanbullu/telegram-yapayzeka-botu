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
        return 0
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
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if not kullanici:
            return []
            
        son_mesajlar = kullanici.mesajlar[-limit:]
        return [{"role": msg.rol, "content": msg.icerik} for msg in son_mesajlar]
    except Exception as e:
        logger.error(f"Geçmiş mesajlar getirilirken hata (ID: {telegram_id}): {e}", exc_info=True)
        return []
    finally:
        session.close()

def gecmisi_temizle(telegram_id):
    session = Session()
    try:
        kullanici = session.query(Kullanici).filter_by(telegram_id=telegram_id).first()
        if kullanici:
            kullanici.konusma_ozeti = None 
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