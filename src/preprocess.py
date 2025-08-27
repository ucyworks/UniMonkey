from __future__ import annotations
import pandas as pd
from typing import Optional

# 81 il listesi (tam Türkçe karakterlerle) - TÜM BÜYÜK HARF
TURKISH_CITIES = [
    "ADANA","ADIYAMAN","AFYONKARAHISAR","AĞRI","AKSARAY","AMASYA","ANKARA","ANTALYA","ARDAHAN","ARTVIN","AYDIN",
    "BALIKESIR","BARTIN","BATMAN","BAYBURT","BILECIK","BINGÖL","BITLIS","BOLU","BURDUR","BURSA","ÇANAKKALE","ÇANKIRI",
    "ÇORUM","DENIZLI","DIYARBAKIR","DÜZCE","EDIRNE","ELAZIĞ","ERZINCAN","ERZURUM","ESKIŞEHIR","GAZIANTEP","GIRESUN",
    "GÜMÜŞHANE","HAKKÂRI","HATAY","IĞDIR","ISPARTA","İSTANBUL","İZMIR","KAHRAMANMARAŞ","KARABÜK","KARAMAN","KARS",
    "KASTAMONU","KAYSERI","KILIS","KIRIKKALE","KIRKLARELI","KIRŞEHIR","KOCAELI","KONYA","KÜTAHYA","MALATYA","MANISA",
    "MARDIN","MERSIN","MUĞLA","MUŞ","NEVŞEHIR","NIĞDE","ORDU","OSMANIYE","RIZE","SAKARYA","SAMSUN","SIIRT","SINOP",
    "SIVAS","ŞANLIURFA","ŞIRNAK","TEKIRDAG","TOKAT","TRABZON","TUNCELI","UŞAK","VAN","YALOVA","YOZGAT","ZONGULDAK"
]

CITY_TO_REGION = {
    # Marmara Bölgesi
    "İSTANBUL":"Marmara","KOCAELİ":"Marmara","TEKİRDAĞ":"Marmara","EDİRNE":"Marmara","KIRKLARELİ":"Marmara",
    "YALOVA":"Marmara","ÇANAKKALE":"Marmara","BALIKESİR":"Marmara","BURSA":"Marmara","SAKARYA":"Marmara","BİLECİK":"Marmara",
    
    # Ege Bölgesi  
    "İZMİR":"Ege","AYDIN":"Ege","MUĞLA":"Ege","MANİSA":"Ege","DENİZLİ":"Ege","KÜTAHYA":"Ege","UŞAK":"Ege","AFYONKARAHİSAR":"Ege",
    
    # Akdeniz Bölgesi
    "ANTALYA":"Akdeniz","MERSİN":"Akdeniz","ADANA":"Akdeniz","OSMANİYE":"Akdeniz","HATAY":"Akdeniz",
    "KAHRAMANMARAŞ":"Akdeniz","ISPARTA":"Akdeniz","BURDUR":"Akdeniz",
    
    # İç Anadolu Bölgesi
    "ANKARA":"İç Anadolu","KONYA":"İç Anadolu","ESKİŞEHİR":"İç Anadolu","KAYSERİ":"İç Anadolu","SİVAS":"İç Anadolu",
    "KIRIKKALE":"İç Anadolu","KIRŞEHİR":"İç Anadolu","NİĞDE":"İç Anadolu","NEVŞEHİR":"İç Anadolu","AKSARAY":"İç Anadolu",
    "ÇANKIRI":"İç Anadolu","KARAMAN":"İç Anadolu","YOZGAT":"İç Anadolu",
    
    # Karadeniz Bölgesi
    "TRABZON":"Karadeniz","ORDU":"Karadeniz","GİRESUN":"Karadeniz","RİZE":"Karadeniz","ARTVİN":"Karadeniz",
    "GÜMÜŞHANE":"Karadeniz","SAMSUN":"Karadeniz","SİNOP":"Karadeniz","ZONGULDAK":"Karadeniz","BARTIN":"Karadeniz",
    "KARABÜK":"Karadeniz","KASTAMONU":"Karadeniz","TOKAT":"Karadeniz","ÇORUM":"Karadeniz","BOLU":"Karadeniz",
    "DÜZCE":"Karadeniz","AMASYA":"Karadeniz","BAYBURT":"Karadeniz",
    
    # Doğu Anadolu Bölgesi
    "ERZURUM":"Doğu Anadolu","ERZİNCAN":"Doğu Anadolu","KARS":"Doğu Anadolu","AĞRI":"Doğu Anadolu","ARDAHAN":"Doğu Anadolu",
    "IĞDIR":"Doğu Anadolu","MALATYA":"Doğu Anadolu","ELAZIĞ":"Doğu Anadolu","TUNCELİ":"Doğu Anadolu","BİNGÖL":"Doğu Anadolu",
    "MUŞ":"Doğu Anadolu","BİTLİS":"Doğu Anadolu","VAN":"Doğu Anadolu","HAKKÂRI":"Doğu Anadolu",
    
    # Güneydoğu Anadolu Bölgesi
    "GAZİANTEP":"Güneydoğu Anadolu","ŞANLIURFA":"Güneydoğu Anadolu","DİYARBAKIR":"Güneydoğu Anadolu",
    "MARDİN":"Güneydoğu Anadolu","BATMAN":"Güneydoğu Anadolu","KİLİS":"Güneydoğu Anadolu","SİİRT":"Güneydoğu Anadolu",
    "ŞIRNAK":"Güneydoğu Anadolu","ADIYAMAN":"Güneydoğu Anadolu",
    
    # KKTC (Kuzey Kıbrıs Türk Cumhuriyeti)
    "KKTC-LEFKOŞA":"KKTC","KKTC-GAZİMAĞUSA":"KKTC","KKTC-GİRNE":"KKTC",
    "KKTC-GÜZELYURT":"KKTC","KKTC-LEFKE":"KKTC",
    
    # Diğer Yurtdışı Konumlar
    "BAKÜ-AZERBAYCAN":"Yurtdışı","BİŞKEK-KIRGIZİSTAN":"Yurtdışı",
    "SARAYBOSNA - BOSNA - HERSEK":"Yurtdışı","TÜRKİSTAN-KAZAKİSTAN":"Yurtdışı",
    "TİRAN-ARNAVUTLUK":"Yurtdışı","ÜSKÜP-MAKEDONYA":"Yurtdışı"
}

# Özel üniversite -> şehir eşlemeleri (üniversite adında şehir geçmeyen veya farklı görünen) - TÜM BÜYÜK HARF
SPECIAL_UNI_CITY = {
    "Gebze Teknik Üniversitesi": "KOCAELI",
    "GEBZE": "KOCAELI",  # Gebze tek başına gelirse Kocaeli
    "Boğaziçi Üniversitesi": "İSTANBUL",
    "İhsan Doğramacı Bilkent Üniversitesi": "ANKARA", 
    "Orta Doğu Teknik Üniversitesi": "ANKARA",
    "Çanakkale Onsekiz Mart Üniversitesi": "ÇANAKKALE",
    "İzmir Yüksek Teknoloji Enstitüsü": "İZMIR",
}

# Basit normalizasyon
import re

def _normalize(s: str) -> str:
    return re.sub(r"\s+"," ", s.strip())

def infer_city(university_name: str) -> Optional[str]:
    if not isinstance(university_name, str) or not university_name.strip():
        return None
    uni_clean = _normalize(university_name)
    
    # Özel eşleşme önce (özel durumlar için)
    for key, city in SPECIAL_UNI_CITY.items():
        if key.lower() in uni_clean.lower():
            return city
    
    # KURAL: Sonunda parantez varsa parantez içindekini al, yoksa ilk kelimeyi al
    # 1. Sonunda parantez kontrol et (örn: "Altınbaş Üniversitesi (İSTANBUL)")
    paren_match = re.search(r'\(([^)]+)\)\s*$', uni_clean)
    if paren_match:
        potential_city = paren_match.group(1).strip()
        # Parantez içindeki şehir ismini Türkiye il listesiyle kontrol et (büyük/küçük harf duyarsız)
        for turkish_city in TURKISH_CITIES:
            if turkish_city.lower() == potential_city.lower():
                return turkish_city  # Türkçe liste formatında döndür (büyük harf)
        # Türkiye'de değilse CITY_TO_REGION'da var mı kontrol et (KKTC, yurtdışı)
        for region_city in CITY_TO_REGION.keys():
            if region_city.lower() == potential_city.lower():
                return region_city
        # Hiçbirinde yoksa büyük harfe çevirip döndür  
        return potential_city.upper()
    
    # 2. Parantez yoksa ilk kelimeyi al
    first_word = uni_clean.split()[0] if uni_clean.split() else ""
    if first_word:
        # İlk kelimeyi Türkiye il listesiyle kontrol et (büyük/küçük harf duyarsız)
        for turkish_city in TURKISH_CITIES:
            if turkish_city.lower() == first_word.lower():
                return turkish_city  # Türkçe liste formatında döndür (büyük harf)
        # Türkiye'de değilse CITY_TO_REGION'da var mı kontrol et
        for region_city in CITY_TO_REGION.keys():
            if region_city.lower() == first_word.lower():
                return region_city
        # Eşleşme yoksa büyük harfe çevirip döndür
        return first_word.upper()
    
    return None

import unicodedata

def normalize_turkish(text: str) -> str:
    """Türkçe karakterleri normalize et (büyük/küçük harf ve karakter varyasyonları için)."""
    if not text:
        return ""
    # Unicode normalize + küçük harf
    normalized = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii').lower()
    # Türkçe karakter dönüşümleri
    replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'İ': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    result = text.lower()
    for tr_char, en_char in replacements.items():
        result = result.replace(tr_char, en_char)
    return result

def add_geography(df: pd.DataFrame) -> pd.DataFrame:
    if 'Üniversite Adı' not in df.columns:
        return df
    cities = df['Üniversite Adı'].map(infer_city)
    
    # TÜM ŞEHİR İSİMLERİNİ BÜYÜK HARFE ÇEVİR
    cities = cities.map(lambda x: x.upper() if x else x)
    
    # İl bulunduktan sonra coğrafi bölgeyi eşleştir - basit lowercase ile
    def find_region(city_raw):
        if not city_raw:
            return None
        # Önce direkt eşleştir
        if city_raw in CITY_TO_REGION:
            return CITY_TO_REGION[city_raw]
        # Basit lowercase eşleştir (İ->i dönüşümü manuel)
        city_search = city_raw.replace('İ', 'i').replace('I', 'ı').lower()
        for city_key, region in CITY_TO_REGION.items():
            city_key_search = city_key.replace('İ', 'i').replace('I', 'ı').lower()
            if city_key_search == city_search:
                return region
        return None
    
    regions = cities.map(find_region)
    out = df.copy()
    out.insert(0, 'İl', cities)
    out.insert(1, 'Bölge', regions)
    return out

def add_program_no(df: pd.DataFrame) -> pd.DataFrame:
    if 'Program No' in df.columns:
        return df
    out = df.copy()
    out.insert(0, 'Program No', range(1, len(out)+1))
    return out

def fix_quota_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """Yerleşen > Kontenjan olan satırları düzelt: Yerleşen sayısını Kontenjan ile sınırla."""
    out = df.copy()
    
    # Tüm Kontenjan ve Yerleşen sütunlarını bul (tekrar eden bloklar olabilir)
    kontenjan_cols = [col for col in out.columns if 'Kontenjan' in col]
    yerleşen_cols = [col for col in out.columns if 'Yerleşen' in col]
    
    for kont_col, yerl_col in zip(kontenjan_cols, yerleşen_cols):
        # Sayısal dönüştür
        kont_num = pd.to_numeric(out[kont_col], errors='coerce')
        yerl_num = pd.to_numeric(out[yerl_col], errors='coerce')
        
        # Yerleşen > Kontenjan olan durumları bul
        problem_mask = (yerl_num > kont_num) & kont_num.notna() & yerl_num.notna()
        
        if problem_mask.sum() > 0:
            print(f"DÜZELTİLDİ: {problem_mask.sum()} satırda {yerl_col} > {kont_col} sorunu vardı")
            # Yerleşen sayısını kontenjan ile sınırla
            out.loc[problem_mask, yerl_col] = out.loc[problem_mask, kont_col]
    
    return out

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    out = add_geography(df)
    out = fix_quota_consistency(out)
    return out
