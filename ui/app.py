import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Proje kök dizinini PYTHONPATH'a ekle (ModuleNotFoundError önlemek için)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_processed  # noqa: E402
from src import config  # noqa: E402

st.set_page_config(
    page_title="YKS Yerleştirme Analizi", 
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile hover efektleri
st.markdown("""
<style>
/* Multiselect ve selectbox hover efektleri */
.stMultiSelect > div > div > div {
    cursor: pointer;
}

.stSelectbox > div > div > div {
    cursor: pointer;
}

/* Multiselect dropdown ok işareti için */
.stMultiSelect > div > div > div > div > svg {
    cursor: pointer;
}

/* Selectbox dropdown ok işareti için */
.stSelectbox > div > div > div > div > svg {
    cursor: pointer;
}

/* Genel hover efekti */
.stMultiSelect:hover, .stSelectbox:hover {
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Sidebar'da UniMonkey logosu ve branding
st.sidebar.markdown("""
<div class="sidebar-logo">
    <h2>🐒 UniMonkey</h2>
</div>
""", unsafe_allow_html=True)

st.title("YKS Yerleştirme Analiz Platformu")

@st.cache_data(show_spinner=True)
def get_data() -> pd.DataFrame:
    return load_processed()

with st.spinner("Veri yükleniyor..."):
    df = get_data()

st.success(f"Toplam satır (işlenmiş): {len(df):,}")

# Sütun adlarını sadeleştirme (tekrar eden kolon grupları için index ekleme opsiyonel)
# Burada orijinal sütunları koruyoruz.

# Filtre bölmesi
with st.sidebar:
    st.header("Filtreler")
    uni_turleri = sorted(df["Üniversite Türü"].dropna().unique().tolist()) if "Üniversite Türü" in df.columns else []
    secilen_tur = st.multiselect("Üniversite Türü", uni_turleri, default=uni_turleri[:3] if len(uni_turleri)>3 else uni_turleri)

    puan_turleri = sorted(df["Puan Türü"].dropna().unique().tolist()) if "Puan Türü" in df.columns else []
    secilen_puan = st.multiselect("Puan Türü", puan_turleri, default=puan_turleri)

    st.markdown("---")
    st.subheader("🗺️ Coğrafi Filtreler")
    
    # Çoklu seçim - Bölge  
    bolgeler = sorted(df["Bölge"].dropna().unique().tolist()) if "Bölge" in df.columns else []
    secilen_bolgeler = st.multiselect("Bölge Seçin", bolgeler, default=bolgeler)

    # Tek seçim - İl (seçilen bölgelere göre)
    if secilen_bolgeler and "Bölge" in df.columns and "İl" in df.columns:
        uygun_iller = df[df["Bölge"].isin(secilen_bolgeler)]["İl"].dropna().unique()
        uygun_iller = ["Tümü"] + sorted(uygun_iller.tolist())
    else:
        uygun_iller = ["Tümü"] + sorted(df["İl"].dropna().unique().tolist()) if "İl" in df.columns else ["Tümü"]
    
    secilen_il = st.selectbox(
        f"İl Seçin ({len(uygun_iller)-1} uygun il)", 
        uygun_iller, 
        index=0
    )

    st.markdown("---")
    st.subheader("📊 Puan & Kontenjan Filtreleri")

    min_puan = st.number_input("En Küçük Puan >=", value=0.0, step=1.0)
    max_puan = st.number_input("En Küçük Puan <=", value=1000.0, step=1.0)

    # Kontenjan aralığı filtresi (ilk 'Kontenjan' kolonu baz alınır)
    kont_range = None
    if "Kontenjan" in df.columns:
        _kont_numeric = pd.to_numeric(df["Kontenjan"], errors='coerce')
        if _kont_numeric.notna().any():
            kmin = int(_kont_numeric.min())
            kmax = int(_kont_numeric.max())
            kont_range = st.slider("Kontenjan aralığı", min_value=kmin, max_value=kmax, value=(kmin, kmax), step=1)

filtreli = df.copy()
if secilen_tur:
    filtreli = filtreli[filtreli["Üniversite Türü"].isin(secilen_tur)]
if secilen_puan:
    filtreli = filtreli[filtreli["Puan Türü"].isin(secilen_puan)]
# Çoklu bölge filtresi
if secilen_bolgeler and "Bölge" in filtreli.columns:
    filtreli = filtreli[filtreli["Bölge"].isin(secilen_bolgeler)]
# Tek il filtresi  
if secilen_il and secilen_il != "Tümü" and "İl" in filtreli.columns:
    filtreli = filtreli[filtreli["İl"] == secilen_il]
if "Kontenjan" in filtreli.columns and 'kont_range' in locals() and kont_range is not None:
    _fk = pd.to_numeric(filtreli["Kontenjan"], errors='coerce')
    filtreli = filtreli[(_fk >= kont_range[0]) & (_fk <= kont_range[1])]

# Puana göre sayısal filtre (bazı hücrelerde '--' olabilir)
if "En Küçük Puan" in filtreli.columns:
    def to_float(x):
        try:
            return float(str(x).replace(',', '.'))
        except ValueError:
            return None
    filtreli = filtreli.assign(_enkucuk=filtreli["En Küçük Puan"].map(to_float))
    filtreli = filtreli[(filtreli["_enkucuk"].isna()) | ((filtreli["_enkucuk"]>=min_puan) & (filtreli["_enkucuk"]<=max_puan))]

st.subheader("Veri Tablosu (İşlenmiş)")
# Index'i 1'den başlat
display_df = filtreli.drop(columns=["_enkucuk"], errors='ignore').head(100).copy()
display_df.index = range(1, len(display_df) + 1)
st.dataframe(display_df, use_container_width=True)

st.caption("İlk 100 satır gösterildi (performans için). Filtreleme tüm veriye uygulanıyor.")

# Basit özetler
st.subheader("📈 Filtreleme Sonuçları")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Gösterilen Program", f"{len(filtreli):,}")
with col2:
    if "İl" in filtreli.columns:
        unique_il = filtreli["İl"].nunique()
        st.metric("İl Sayısı", unique_il)
with col3:
    if "Bölge" in filtreli.columns:
        unique_bolge = filtreli["Bölge"].nunique()
        st.metric("Bölge Sayısı", unique_bolge)
with col4:
    if "Üniversite Adı" in filtreli.columns:
        unique_uni = filtreli["Üniversite Adı"].nunique()
        st.metric("Üniversite Sayısı", unique_uni)

# Doluluk oranı hesaplama (Kontenjan & Yerleşen tekrar eden kolonlar olduğundan ilk çifti kullanıyoruz)
if {"Kontenjan", "Yerleşen"}.issubset(filtreli.columns):
    try:
        kont = pd.to_numeric(filtreli["Kontenjan"], errors='coerce')
        yerl = pd.to_numeric(filtreli["Yerleşen"], errors='coerce')
        doluluk = (yerl.sum()/kont.sum()*100) if kont.sum() else None
        if doluluk is not None:
            st.metric("Toplam Doluluk (%)", f"{doluluk:0.2f}")
    except Exception as e:
        st.write(f"Doluluk hesaplanamadı: {e}")

st.markdown("---")
st.caption("Gelişmiş analizler için yakında ek sayfalar eklenecek.")
