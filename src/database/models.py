from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Kullanici(Base):
    __tablename__ = 'kullanicilar'

    # Benzersiz Telegram Kullanıcı Kimliği
    telegram_id = Column(BigInteger, primary_key=True) 
    
        # Uzun Bellek (Mesajlar çok uzadığında buraya özet kaydedilecek)
    konusma_ozeti = Column(Text, nullable=True)          

    # Günlük Kota Takibi (RAM yerine kalıcı olsun diye - restart'ta sıfırlanmasın)
    gunluk_mesaj_sayisi = Column(Integer, default=0, nullable=False)
    gunluk_tarih = Column(String(10), nullable=True)  # "2026-08-25" formatında

    # İlişki Bağlantısı: Bir kullanıcının birden çok mesajı olabilir          

    # İlişki Bağlantısı: Bir kullanıcının birden çok mesajı olabilir
    # cascade özelliği, kullanıcı sıfırlandığında mesajların da silinmesini sağlar
    mesajlar = relationship(
        "Mesaj", 
        back_populates="kullanici", 
        cascade="all, delete-orphan",
        order_by="Mesaj.olusturulma_tarihi" # Her zaman kronolojik sırayla gelir
    )

class Mesaj(Base):
    __tablename__ = 'mesajlar'

    # Mesaj Kimliği ve Kullanıcı Bağlantısı
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey('kullanicilar.telegram_id'))
    
    # Kısa Bellek Yapısı (Yapay zekanın anlayacağı format için)
    rol = Column(String(20), nullable=False)             # 'user' veya 'assistant'
    icerik = Column(Text, nullable=False)                # Mesaj metni
    olusturulma_tarihi = Column(DateTime, default=datetime.utcnow) 

    # Geriye dönük ilişki
    kullanici = relationship("Kullanici", back_populates="mesajlar")