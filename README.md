# 🎓 UniMonkey - YKS Yerleştirme Analizi Platformu

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.36%2B-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Pandas-2.2%2B-green.svg" alt="Pandas">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🚀 Proje Hakkında

**UniMonkey**, Türkiye'deki üniversite yerleştirme sistemini (YKS) derinlemesine analiz etmek için geliştirilmiş kapsamlı bir veri analizi platformudur. Bu platform sayesinde:

- 📊 **Detaylı İstatistikler**: Üniversite programları, kontenjanlar ve doluluk oranları
- 🎯 **Bölüm Analizleri**: Popüler ve boş kalan programların karşılaştırması
- 🏛️ **Devlet vs Vakıf**: Üniversite türleri arasındaki farkların analizi
- 💰 **Burslu Program Takibi**: Vakıf üniversitelerindeki burslu fırsatların keşfi
- 🗺️ **Coğrafi Dağılım**: İl ve bölge bazlı program dağılımları
- 📈 **Trend Analizleri**: Yıllar arası değişimler ve eğilimler

## ✨ Öne Çıkan Özellikler

### 🎨 İnteraktif Web Arayüzü
- Modern ve kullanıcı dostu Streamlit tabanlı arayüz
- Gerçek zamanlı filtreler ve etkileşimli grafikler
- Mobil uyumlu tasarım

### 📋 Çok Sayfalı Analiz Sistemi
1. **📊 Temel İstatistikler** - Genel durumun özeti
2. **🎯 Bölüm Doluluk Analizleri** - Detaylı program analizleri
3. **🏛️ Devlet Üniversiteleri** - Devlet üniversitelerine odaklı analiz
4. **🏢 Vakıf & Burslu Programlar** - Özel üniversite ve burs fırsatları
5. **🔬 Fakülte & Bölüm Bazlı** - Derinlemesine akademik birim analizleri

### 🔍 Gelişmiş Filtreleme
- İl ve bölge bazlı filtreleme
- Üniversite türü seçimi (Devlet/Vakıf)
- Kontenjan aralığı ayarları
- Doluluk oranı aralıkları
- Program türü filtreleri (Burslu/Ücretli)

## 📁 Proje Yapısı

```
UniMonkey/
├── 📊 data/                    # Veri dosyaları
│   └── yks_tablo.csv          # Ana YKS yerleştirme verisi
├── 🐍 src/                     # Ana Python modülleri
│   ├── config.py              # Yapılandırma ayarları
│   ├── data_loader.py         # Veri yükleme ve işleme
│   └── preprocess.py          # Veri ön işleme fonksiyonları
├── 🖥️ ui/                      # Web arayüzü
│   ├── app.py                 # Ana Streamlit uygulaması
│   └── pages/                 # Çok sayfalı analiz modülleri
│       ├── 1_📊_Temel_Istatistikler.py
│       ├── 2_🎯_Bolum_Doluluk.py
│       ├── 3_🏛️_Devlet_Analizi.py
│       ├── 4_🏢_Vakif_Burslu.py
│       └── 5_🏛️_Fakulte_Bolum.py
├── 📝 scripts/                 # Yardımcı scriptler
│   ├── show_dataframe.py      # Hızlı veri önizleme
│   └── test_geography.py      # Coğrafi veri testleri
├── 📚 notebooks/               # Jupyter notebook analizleri
├── 🧪 tests/                   # Test dosyaları
├── 📋 requirements.txt         # Python bağımlılıkları
└── 📖 README.md               # Bu dosya
```

## 🛠️ Kurulum

### Sistem Gereksinimleri
- **Python**: 3.8 veya üstü
- **İşletim Sistemi**: Windows, macOS, Linux
- **RAM**: En az 4GB (büyük veri setleri için 8GB+ önerilir)

### Hızlı Kurulum

1. **Projeyi İndirin**
```bash
git clone https://github.com/ucyworks/UniMonkey.git
cd UniMonkey
```

2. **Sanal Ortam Oluşturun** (Önerilir)
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

3. **Bağımlılıkları Yükleyin**
```bash
pip install -r requirements.txt
```

4. **Veri Dosyasını Yerleştirin**
`yks_tablo.csv` dosyasını `data/` klasörüne koyun.

## 🚀 Kullanım

### Web Arayüzünü Başlatma
```bash
streamlit run ui/app.py
```
Tarayıcınızda otomatik olarak `http://localhost:8501` açılacaktır.

### Komut Satırı Araçları

**Hızlı veri önizleme:**
```bash
python -m scripts.show_dataframe
```

**Coğrafi veri testi:**
```bash
python -m scripts.test_geography
```

**Doğrudan veri yükleme:**
```bash
python -m src.data_loader
```

## 📊 Veri Setinin Yapısı

Platform aşağıdaki veri alanlarını analiz eder:

| Alan | Açıklama |
|------|----------|
| `Üniversite Adı` | Üniversitenin tam adı |
| `Fakülte/Yüksekokul Adı` | Akademik birim |
| `Program Adı` | Lisans programının adı |
| `Program Türü` | Normal Öğretim, İkinci Öğretim, vb. |
| `Üniversite Türü` | Devlet, Vakıf |
| `Burs Türü` | Tam Burslu, Yarı Burslu, Ücretli |
| `Kontenjan` | Program kontenjan sayısı |
| `Yerleşen` | Yerleşen öğrenci sayısı |
| `İl` | Üniversitenin bulunduğu il |
| `Bölge` | Coğrafi bölge |

## 🎯 Analiz Türleri

### 📈 Temel İstatistikler
- Toplam program, kontenjan, yerleşen sayıları
- Genel doluluk oranları
- İl ve bölge dağılımları
- En popüler üniversiteler

### 🔍 Bölüm Doluluk Analizleri
- En dolu ve en boş programlar
- Bölüm bazlı doluluk oranları
- Trend analizleri
- Karşılaştırmalı grafikler

### 🏛️ Devlet Üniversiteleri Analizi
- Devlet üniversitelerine özel istatistikler
- İl bazlı devlet üniversitesi dağılımı
- Kontenjan büyüklüğü analizleri
- En boş devlet programları

### 💰 Vakıf ve Burslu Program Analizleri
- Burslu vs ücretli program karşılaştırması
- Vakıf üniversitelerinin durumu
- Burs oranları analizi
- Şehir bazlı vakıf üniversitesi dağılımı

### 🔬 Fakülte ve Bölüm Detay Analizleri
- Fakülte türlerine göre analiz
- Program kategorileri
- Alan bazlı istatistikler
- Popüler vs boş bölüm karşılaştırması

## 🎨 Görselleştirme Özellikleri

- **📊 Çubuk Grafikler**: Karşılaştırmalı analizler
- **🥧 Pasta Grafikleri**: Dağılım analizleri  
- **📈 Çizgi Grafikleri**: Trend analizleri
- **📍 Coğrafi Haritalar**: İl/bölge dağılımları *(yakında)*
- **📋 Etkileşimli Tablolar**: Detaylı veri görüntüleme
- **🎯 KPI Kartları**: Önemli metriklerin vurgulanması

## 🔧 Konfigürasyon

### Veri Ayarları
`src/config.py` dosyasından aşağıdaki ayarları değiştirebilirsiniz:

```python
# Veri dosyası konumları
RAW_DATA_FILE = DATA_DIR / "yks_tablo.csv"
LEGACY_RAW_DATA_FILE = BASE_DIR / "yks_tablo.csv"

# Gelecekteki konfigürasyonlar buraya eklenecek
```

### Streamlit Ayarları
`.streamlit/config.toml` dosyası oluşturarak arayüz ayarlarını özelleştirebilirsiniz.

## 🤝 Katkıda Bulunma

1. **Fork** edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. **Pull Request** oluşturun

### Geliştirici Notları
- Kod standartlarına uygun yazın
- Yeni özellikler için testler ekleyin
- Dokümantasyonu güncel tutun

## 📋 Yapılacaklar (Roadmap)

### v1.1.0 - Geliştirilmiş Analizler
- [ ] Makine öğrenmesi tabanlı tahmin modelleri
- [ ] Daha gelişmiş istatistiksel analizler
- [ ] Excel/PDF rapor exportu

### v1.2.0 - Görselleştirme Geliştirmeleri  
- [ ] Coğrafi harita entegrasyonu
- [ ] 3D görselleştirmeler
- [ ] Animasyonlu grafikler

### v1.3.0 - Kullanıcı Deneyimi
- [ ] Kişiselleştirilmiş dashboard'lar
- [ ] Favori analizler sistemi
- [ ] Karşılaştırma araçları

### v2.0.0 - Platform Genişletmesi
- [ ] Çoklu yıl karşılaştırması
- [ ] API desteği
- [ ] Mobil uygulama

## 🐛 Bilinen Sorunlar

- Çok büyük veri setlerinde performans sorunu yaşanabilir
- Bazı Türkçe karakter encoding sorunları olabilir
- İnternet Explorer desteği sınırlıdır

Sorunları [Issues](https://github.com/ucyworks/UniMonkey/issues) sekmesinden bildirebilirsiniz.

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👨‍💻 Geliştirici

**UniMonkey v1.0.0+1** 

🌐 [ucyworks.com](https://ucyworks.com) tarafından geliştirilmiştir.

---

<div align="center">
  <p>⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!</p>
  <p>📧 Sorularınız için: <a href="mailto:info@ucyworks.com">info@ucyworks.com</a></p>
</div>
