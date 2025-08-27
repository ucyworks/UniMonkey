# YKS Yerleştirme Analizi

Bu proje, `yks_tablo.csv` dosyasındaki YKS yerleştirme verilerini analiz etmek için hazırlanmıştır.

## Proje Yapısı
```
YKS/
  data/                # Ham veri (yks_tablo.csv buraya taşınabilir)
    yks_tablo.csv        # Ham CSV (henüz data/ içine taşınmadı)
  src/                 # Python modülleri
    config.py          # Yol & sabit tanımları
    data_loader.py     # Veri yükleme & önizleme fonksiyonları
  scripts/             # Komut satırı yardımcı araçları
    show_dataframe.py  # DataFrame önizleme scripti
  notebooks/           # Analiz Jupyter defterleri
  tests/               # Testler (ileride eklenecek)
  requirements.txt     # Bağımlılıklar
  README.md            # Bu dosya
  
```

## Kurulum
1. Sanal ortam (önerilir):
```
python -m venv .venv
.venv\Scripts\activate
```
2. Bağımlılıklar:
```
pip install -r requirements.txt
```

## Hızlı Başlangıç
CSV'yi yükleyip ilk satırları görmek için:
```
python -m scripts.show_dataframe
```

Alternatif: Doğrudan modülü çalıştırın:
```
python -m src.data_loader
```

### Arayüz (Streamlit)
Veriyi web arayüzünde incelemek için:
```
pip install -r requirements.txt  # (henüz kurulmadıysa)
streamlit run ui/app.py
```
Tarayıcı otomatik açılmazsa çıktıda verilen URL'yi (genelde http://localhost:8501) kopyalayın.

## Notlar
- `yks_tablo.csv` dosyasını `data/` klasörüne taşırsanız hiçbir kodu değiştirmenize gerek yok.
- Kod farklı encoding denemeleri yaparak dosyayı okumaya çalışır.

## Sonraki Adımlar (Plan)
- Sütun adlarını standardize etme (lowercase, Türkçe karakter temizleme)
- Temel istatistikler: bölüm bazında kontenjan, yerleşen, doluluk oranı
- Puan türü & şehir bazlı dağılımlar
- Tercih tahmin / basit modelleme (opsiyonel)
- Eksik veri ve aykırı değer analizi

## Lisans
İç kullanım analizi.
