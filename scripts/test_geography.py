from src.data_loader import load_yks_table
from src.preprocess import infer_city, CITY_TO_REGION, add_geography

# Test için ilk 10 satırı al
df = load_yks_table()
sample_unis = df['Üniversite Adı'].head(10).tolist()

print("TEST: İl ve Bölge Eşleştirme")
print("=" * 50)

for uni in sample_unis:
    city = infer_city(uni)
    # Manuel region bulma
    def find_region_debug(city_raw):
        if not city_raw:
            return "ŞEHİR YOK"
        if city_raw in CITY_TO_REGION:
            return CITY_TO_REGION[city_raw] + " (DIREKT)"
        city_search = city_raw.replace('İ', 'i').replace('I', 'ı').lower()
        for city_key, region in CITY_TO_REGION.items():
            city_key_search = city_key.replace('İ', 'i').replace('I', 'ı').lower()
            if city_key_search == city_search:
                return region + f" (EŞLEŞTI: {city_key})"
        return "BULUNAMADI"
    
    region = find_region_debug(city)
    print(f"Üniversite: {uni}")
    print(f"  İl: {city}")
    print(f"  Bölge: {region}")
    print("-" * 30)

# Gerçek fonksiyonu test et
print("\nGERÇEK FONKSİYON TESTİ:")
df_geo = add_geography(df.head(3))
print(df_geo[['İl', 'Bölge', 'Üniversite Adı']].to_string())
