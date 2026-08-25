import datetime
import pytest
from src.middleware.kural_denetleyici import (
    kilit_ve_sinir_kontrolu,
    islem_basarili_kilidi_ac,
    hata_durumunda_kilidi_ac,
    aktif_islemler,
    GUNLUK_LIMIT,
    MAKSIMUM_KULLANICI_KAPASITESI,
)
from src.services.prompt_olusturucu import prompt_hazirla


@pytest.fixture(autouse=True)
def kilitleri_temizle():
    """
    aktif_islemler modül seviyesinde (RAM'de) kalıcı bir sözlük.
    Testler birbirini etkilemesin diye her testten önce/sonra temizliyoruz.
    """
    aktif_islemler.clear()
    yield
    aktif_islemler.clear()


# --- KURAL DENETLEYİCİ TESTLERİ ---

def test_kapasite_siniri_yeni_kullaniciyi_reddeder():
    # Yeni (kayıtsız) bir kullanıcı, kapasite dolu iken gelirse reddedilmeli
    izin, mesaj, _ = kilit_ve_sinir_kontrolu(
        telegram_id=999999,
        toplam_kullanici=MAKSIMUM_KULLANICI_KAPASITESI,
        kayitli_mi=False,
        bugunku_kullanim={"sayi": 0, "tarih": None},
    )

    assert izin is False
    assert "Kapasitemiz doldu" in mesaj


def test_kapasite_siniri_kayitli_kullaniciyi_etkilemez():
    # Kapasite dolu olsa bile, ZATEN KAYITLI bir kullanıcı bloklanmamalı
    izin, _, _ = kilit_ve_sinir_kontrolu(
        telegram_id=42,
        toplam_kullanici=MAKSIMUM_KULLANICI_KAPASITESI,
        kayitli_mi=True,
        bugunku_kullanim={"sayi": 0, "tarih": None},
    )

    assert izin is True


def test_kapasite_bilinmiyorsa_kullanici_bloklanmaz():
    # kayitli_mi=None -> DB hatası oldu, "bilmiyoruz" demek.
    # Mevcut bir müşteriyi yanlışlıkla riske atmamak için kapasite kapısı kapanmamalı.
    izin, _, _ = kilit_ve_sinir_kontrolu(
        telegram_id=42,
        toplam_kullanici=MAKSIMUM_KULLANICI_KAPASITESI,
        kayitli_mi=None,
        bugunku_kullanim={"sayi": 0, "tarih": None},
    )

    assert izin is True


def test_kilit_sistemi_ust_uste_mesaji_reddeder():
    ortak_kullanim = {"sayi": 0, "tarih": None}

    # İlk mesaj: izin vermeli ve kilitlemeli
    izin1, _, _ = kilit_ve_sinir_kontrolu(111, 1, True, ortak_kullanim)
    assert izin1 is True
    assert aktif_islemler[111] is True

    # İkinci mesaj (kilit açılmadan): reddetmeli
    izin2, mesaj2, _ = kilit_ve_sinir_kontrolu(111, 1, True, ortak_kullanim)
    assert izin2 is False
    assert "lütfen bekle" in mesaj2


def test_kilit_acilinca_tekrar_mesaj_atilabilir():
    ortak_kullanim = {"sayi": 0, "tarih": None}

    izin1, _, kullanim_durumu = kilit_ve_sinir_kontrolu(222, 1, True, ortak_kullanim)
    assert izin1 is True

    islem_basarili_kilidi_ac(222, kullanim_durumu)
    assert aktif_islemler[222] is False

    izin2, _, _ = kilit_ve_sinir_kontrolu(222, 1, True, ortak_kullanim)
    assert izin2 is True


def test_gunluk_limit_dolunca_reddeder():
    bugun = datetime.date.today().isoformat()

    izin, mesaj, _ = kilit_ve_sinir_kontrolu(
        telegram_id=333,
        toplam_kullanici=1,
        kayitli_mi=True,
        bugunku_kullanim={"sayi": GUNLUK_LIMIT, "tarih": bugun},
    )

    assert izin is False
    assert "limitin doldu" in mesaj


def test_gun_degisince_sayac_sifirlanir():
    izin, _, kullanim_durumu = kilit_ve_sinir_kontrolu(
        telegram_id=444,
        toplam_kullanici=1,
        kayitli_mi=True,
        bugunku_kullanim={"sayi": GUNLUK_LIMIT, "tarih": "2000-01-01"},  # eski/farklı bir gün
    )

    assert izin is True
    assert kullanim_durumu["sayi"] == 0


def test_islem_basarili_kilidi_ac_sayaci_bir_artirir():
    aktif_islemler[555] = True  # gerçek akışta kilit zaten kilit_ve_sinir_kontrolu'de açılmış olurdu
    kullanim_durumu = {"sayi": 5, "tarih": "2026-08-25"}
    yeni_durum = islem_basarili_kilidi_ac(555, kullanim_durumu)

    assert yeni_durum["sayi"] == 6
    assert yeni_durum["tarih"] == "2026-08-25"
    assert aktif_islemler[555] is False


def test_hata_durumunda_kilit_acilir():
    aktif_islemler[666] = True
    hata_durumunda_kilidi_ac(666)
    assert aktif_islemler[666] is False


# --- PROMPT OLUŞTURUCU TESTLERİ ---

def test_prompt_hazirlama_temel():
    mesaj = "Merhaba dünya"
    paket = prompt_hazirla(mesaj)

    assert len(paket) == 2  # System ve User
    assert paket[1]["role"] == "user"
    assert paket[1]["content"] == "Merhaba dünya"