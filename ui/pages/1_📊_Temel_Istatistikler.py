import streamlit as st
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_processed  # noqa: E402

st.title("📊 Temel İstatistikler")

@st.cache_data
def get_data():
    return load_processed()

df = get_data()

st.markdown("### Genel Bilgiler")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Toplam Program", f"{len(df):,}")
with col2:
    if "İl" in df.columns:
        st.metric("İl", df["İl"].nunique())
with col3:
    if "Bölge" in df.columns:
        st.metric("Bölge", df["Bölge"].nunique())
with col4:
    if "Üniversite Türü" in df.columns:
        st.metric("Üni. Türü", df["Üniversite Türü"].nunique())

st.markdown("### Doluluk Oranları (İlk Kolon Çifti)")
if {"Kontenjan", "Yerleşen"}.issubset(df.columns):
    kont = pd.to_numeric(df["Kontenjan"], errors='coerce')
    yerl = pd.to_numeric(df["Yerleşen"], errors='coerce')
    doluluk = (yerl.sum()/kont.sum()*100) if kont.sum() else None
    if doluluk is not None:
        st.progress(min(1.0, doluluk/100))
        st.write(f"Genel doluluk: **{doluluk:0.2f}%**")

st.markdown("### Puan Türüne Göre Ortalama En Küçük Puan")
if {"Puan Türü", "En Küçük Puan"}.issubset(df.columns):
    def to_float(x):
        try:
            return float(str(x).replace(',', '.'))
        except ValueError:
            return None
    temp = df.assign(_enk= df["En Küçük Puan"].map(to_float))
    grp = temp.groupby("Puan Türü", dropna=True)["_enk"].mean().dropna().sort_values(ascending=False)
    st.bar_chart(grp)
else:
    st.info("Gerekli kolonlar yok.")

st.markdown("### Bölgelere Göre Program Dağılımı")
if "Bölge" in df.columns:
    bolge_dagilim = df["Bölge"].value_counts().dropna()
    st.bar_chart(bolge_dagilim)

st.markdown("### En Çok Program Olan İlk 15 İl")
if "İl" in df.columns:
    il_dagilim = df["İl"].value_counts().dropna().head(15)
    st.bar_chart(il_dagilim)

st.caption("✨ Daha detaylı analizler için diğer sekmeleri inceleyiniz: Bölüm Doluluk, Devlet Analizi, Vakıf/Burslu Analizi ve Fakülte/Bölüm Analizleri.")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 14px; padding: 20px 0;'>
        UniMonkey v1.0.0+1 | <a href='https://ucyworks.com' target='_blank' style='color: #0066cc; text-decoration: none;'>ucyworks.com</a> tarafından geliştirilmiştir.
    </div>
    """, 
    unsafe_allow_html=True
)