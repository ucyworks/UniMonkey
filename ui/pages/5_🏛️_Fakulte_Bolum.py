import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_processed  # noqa: E402

st.title("🏛️ Fakülte ve Bölüm Bazlı Detaylı Analizler")

@st.cache_data
def get_data():
    return load_processed()

df = get_data()

# Doluluk oranı hesapla
def calculate_occupancy(row):
    try:
        kontenjan = pd.to_numeric(row['Kontenjan'], errors='coerce')
        yerlesen = pd.to_numeric(row['Yerleşen'], errors='coerce')
        if pd.isna(kontenjan) or pd.isna(yerlesen) or kontenjan <= 0:
            return np.nan
        return (yerlesen / kontenjan) * 100
    except:
        return np.nan

df = df.copy()
df['Doluluk_Orani'] = df.apply(calculate_occupancy, axis=1)
df['Bos_Kontenjan'] = pd.to_numeric(df['Kontenjan'], errors='coerce') - pd.to_numeric(df['Yerleşen'], errors='coerce')

# Filtre seçenekleri
st.sidebar.header("🔍 Fakülte & Bölüm Filtreleri")

# Program kategorisi oluştur (program adına göre)
def categorize_program(program_adi):
    program_adi = str(program_adi).lower()
    if any(word in program_adi for word in ['mühendislik', 'engineering', 'endüstri']):
        return 'Mühendislik'
    elif any(word in program_adi for word in ['tip', 'diş hekimliği', 'veteriner', 'eczacılık', 'hemşire']):
        return 'Sağlık Bilimleri'
    elif any(word in program_adi for word in ['hukuk', 'law']):
        return 'Hukuk'
    elif any(word in program_adi for word in ['işletme', 'ekonomi', 'iktisat', 'maliye', 'muhasebe']):
        return 'İş ve Ekonomi'
    elif any(word in program_adi for word in ['eğitim', 'öğretmen', 'pedagoji']):
        return 'Eğitim Bilimleri'
    elif any(word in program_adi for word in ['sosyal', 'psikoloji', 'sosyoloji', 'felsefe', 'tarih']):
        return 'Sosyal Bilimler'
    elif any(word in program_adi for word in ['fen', 'matematik', 'fizik', 'kimya', 'biyoloji']):
        return 'Fen Bilimleri'
    elif any(word in program_adi for word in ['sanat', 'müzik', 'resim', 'tasarım']):
        return 'Güzel Sanatlar'
    elif any(word in program_adi for word in ['iletişim', 'gazetecilik', 'medya']):
        return 'İletişim'
    else:
        return 'Diğer'

df['Program_Kategorisi'] = df['Program Adı'].apply(categorize_program)

# Üniversite türü filtresi
if 'Üniversite Türü' in df.columns:
    uni_turu_listesi = ['Tümü'] + sorted(df['Üniversite Türü'].dropna().unique().tolist())
    secili_uni_turu = st.sidebar.selectbox("Üniversite Türü", uni_turu_listesi)
    if secili_uni_turu != 'Tümü':
        df = df[df['Üniversite Türü'] == secili_uni_turu]

# Bölge filtresi
if 'Bölge' in df.columns:
    bolge_listesi = ['Tümü'] + sorted(df['Bölge'].dropna().unique().tolist())
    secili_bolge = st.sidebar.selectbox("Bölge Seç", bolge_listesi)
    if secili_bolge != 'Tümü':
        df = df[df['Bölge'] == secili_bolge]

# Şehir filtresi
if 'İl' in df.columns:
    sehir_listesi = ['Tümü'] + sorted(df['İl'].dropna().unique().tolist())
    secili_sehir = st.sidebar.selectbox("Şehir Seç", sehir_listesi)
    if secili_sehir != 'Tümü':
        df = df[df['İl'] == secili_sehir]

# Fakülte filtresi
if 'Fakülte/Yüksekokul Adı' in df.columns:
    fakulte_listesi = ['Tümü'] + sorted(df['Fakülte/Yüksekokul Adı'].dropna().unique().tolist()[:50])  # İlk 50 fakulte
    secili_fakulte = st.sidebar.selectbox("Fakülte/Yüksekokul", fakulte_listesi)
    if secili_fakulte != 'Tümü':
        df = df[df['Fakülte/Yüksekokul Adı'] == secili_fakulte]

# Kontenjan aralığı filtresi
min_kontenjan = st.sidebar.number_input("Minimum Kontenjan", min_value=0, value=0, step=50)
df = df[pd.to_numeric(df['Kontenjan'], errors='coerce') >= min_kontenjan]

# Doluluk oranı filtresi
doluluk_araligi = st.sidebar.slider("Doluluk Oranı Aralığı (%)", 0, 100, (0, 100), step=5)
df = df[
    (df['Doluluk_Orani'] >= doluluk_araligi[0]) & 
    (df['Doluluk_Orani'] <= doluluk_araligi[1])
]

st.sidebar.caption("💡 Filtreler tüm sekmelerdeki analizleri etkiler. Fakülte filtresi ile spesifik birimler üzerinde odaklanabilirsiniz.")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Fakülte Analizleri", 
    "📚 Bölüm Analizleri", 
    "🔬 Alan Bazlı", 
    "🎯 Popüler vs Boş", 
    "📈 Trend Analizleri"
])

with tab1:
    st.header("Fakülte/Yüksekokul Bazlı Analizler")
    
    if 'Fakülte/Yüksekokul Adı' in df.columns:
        # Fakülte analizi
        fakulte_analiz = df.groupby('Fakülte/Yüksekokul Adı').agg({
            'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Program Adı': 'count',
            'Üniversite Adı': 'nunique'
        }).reset_index()
        
        fakulte_analiz['Doluluk_Orani'] = (fakulte_analiz['Yerleşen'] / fakulte_analiz['Kontenjan'] * 100)
        fakulte_analiz['Bos_Kontenjan'] = fakulte_analiz['Kontenjan'] - fakulte_analiz['Yerleşen']
        
        # Fakülte türlerini kategorize et
        fakulte_analiz['Fakulte_Turu'] = 'Diğer'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('Mühendislik', case=False, na=False), 'Fakulte_Turu'] = 'Mühendislik'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('Tıp', case=False, na=False), 'Fakulte_Turu'] = 'Tıp'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('İktisadi|İktisat|İşletme', case=False, na=False), 'Fakulte_Turu'] = 'İktisadi'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('Eğitim', case=False, na=False), 'Fakulte_Turu'] = 'Eğitim'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('Fen|Fen-Edebiyat', case=False, na=False), 'Fakulte_Turu'] = 'Fen-Edebiyat'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('Meslek Yüksekokulu', case=False, na=False), 'Fakulte_Turu'] = 'MYO'
        fakulte_analiz.loc[fakulte_analiz['Fakülte/Yüksekokul Adı'].str.contains('Hukuk', case=False, na=False), 'Fakulte_Turu'] = 'Hukuk'
        
        # Fakülte türüne göre doluluk analizi
        st.subheader("Fakülte Türlerine Göre Doluluk Durumu")
        
        tur_analiz = fakulte_analiz.groupby('Fakulte_Turu').agg({
            'Doluluk_Orani': 'mean',
            'Program Adı': 'sum',
            'Bos_Kontenjan': 'sum'
        }).reset_index().sort_values('Doluluk_Orani')
        
        fig = px.bar(
            tur_analiz,
            x='Fakulte_Turu',
            y='Doluluk_Orani',
            color='Program Adı',
            title="Fakülte Türlerine Göre Ortalama Doluluk Oranı",
            labels={'Program Adı': 'Toplam Program Sayısı'}
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # En boş fakülteler
        st.subheader("En Boş Kalan Fakülte/Yüksekokullar")
        en_bos_fakulteler = fakulte_analiz.nsmallest(20, 'Doluluk_Orani')
        
        fig = px.scatter(
            en_bos_fakulteler.head(15),
            x='Kontenjan',
            y='Doluluk_Orani',
            size='Bos_Kontenjan',
            color='Fakulte_Turu',
            hover_data=['Fakülte/Yüksekokul Adı'],
            title="En Boş 15 Fakülte/Yüksekokul"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Fakülte türü dağılımı
        st.subheader("Fakülte Türü Dağılımı")
        tur_dagilim = fakulte_analiz['Fakulte_Turu'].value_counts()
        
        fig_pie = px.pie(
            values=tur_dagilim.values,
            names=tur_dagilim.index,
            title="Fakülte/Yüksekokul Türü Dağılımı"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.header("Program/Bölüm Bazlı Detaylı Analizler")
    
    # Program kategorilerini oluştur
    df['Program_Kategorisi'] = 'Diğer'
    
    # Mühendislik bölümleri
    df.loc[df['Program Adı'].str.contains('Mühendisliği|Mühendislik', case=False, na=False), 'Program_Kategorisi'] = 'Mühendislik'
    
    # Tıp bölümleri
    df.loc[df['Program Adı'].str.contains('Tıp|Diş Hekimliği|Veteriner|Eczacılık', case=False, na=False), 'Program_Kategorisi'] = 'Sağlık'
    
    # Eğitim bölümleri
    df.loc[df['Program Adı'].str.contains('Öğretmenliği|Eğitimi', case=False, na=False), 'Program_Kategorisi'] = 'Eğitim'
    
    # İşletme ve İktisat
    df.loc[df['Program Adı'].str.contains('İşletme|İktisat|Maliye|Ekonomi', case=False, na=False), 'Program_Kategorisi'] = 'İşletme-İktisat'
    
    # Hukuk
    df.loc[df['Program Adı'].str.contains('Hukuk', case=False, na=False), 'Program_Kategorisi'] = 'Hukuk'
    
    # Sosyal bilimler
    df.loc[df['Program Adı'].str.contains('Psikoloji|Sosyoloji|Felsefe|Tarih|Coğrafya', case=False, na=False), 'Program_Kategorisi'] = 'Sosyal Bilimler'
    
    # Fen bilimleri
    df.loc[df['Program Adı'].str.contains('Matematik|Fizik|Kimya|Biyoloji', case=False, na=False), 'Program_Kategorisi'] = 'Fen Bilimleri'
    
    # Program kategorilerine göre analiz
    st.subheader("Program Kategorilerine Göre Doluluk Analizi")
    
    kategori_analiz = df.groupby('Program_Kategorisi').agg({
        'Doluluk_Orani': ['mean', 'median'],
        'Program Adı': 'count',
        'Bos_Kontenjan': 'sum'
    }).reset_index()
    
    kategori_analiz.columns = ['Kategori', 'Ortalama_Doluluk', 'Medyan_Doluluk', 'Program_Sayisi', 'Toplam_Bos_Kontenjan']
    kategori_analiz = kategori_analiz.sort_values('Ortalama_Doluluk')
    
    fig = px.bar(
        kategori_analiz,
        x='Kategori',
        y='Ortalama_Doluluk',
        color='Toplam_Bos_Kontenjan',
        title="Program Kategorilerine Göre Ortalama Doluluk"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    # En boş bölümler kategorilere göre
    st.subheader("Kategorilere Göre En Boş Bölümler")
    
    kategori_secim = st.selectbox(
        "Kategori Seç",
        ['Tümü'] + sorted(df['Program_Kategorisi'].unique().tolist())
    )
    
    if kategori_secim == 'Tümü':
        filtered_df = df
    else:
        filtered_df = df[df['Program_Kategorisi'] == kategori_secim]
    
    en_bos_bolumler = filtered_df.nsmallest(20, 'Doluluk_Orani')
    
    if not en_bos_bolumler.empty:
        fig = px.bar(
            en_bos_bolumler.head(10),
            y='Program Adı',
            x='Doluluk_Orani',
            color='Üniversite Türü',
            title=f"En Boş 10 Bölüm - {kategori_secim}",
            orientation='h',
            labels={
                'Program Adı': 'Program Adı',
                'Doluluk_Orani': '% Doluluk Oranı',
                'Üniversite Türü': 'Üniversite Türü'
            },
            hover_data=['Üniversite Adı', 'İl', 'Kontenjan', 'Yerleşen', 'Bos_Kontenjan']
        )
        fig.update_xaxes(title="% Doluluk Oranı", ticksuffix="%")
        fig.update_yaxes(title="Program Adı")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"📊 Bu grafik {kategori_secim} kategorisindeki en boş 10 programı gösterir. Çubuk uzunluğu doluluk oranını, renk ise üniversite türünü temsil eder.")
        
        # Özet istatistikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Seçilen Kategori Program Sayısı", len(filtered_df))
        with col2:
            ortalama_doluluk = filtered_df['Doluluk_Orani'].mean()
            st.metric("Ortalama Doluluk", f"{ortalama_doluluk:.1f}%")
        with col3:
            en_bos_doluluk = en_bos_bolumler['Doluluk_Orani'].min()
            st.metric("En Boş Program Doluluk", f"{en_bos_doluluk:.1f}%")
        with col4:
            toplam_bos = filtered_df['Bos_Kontenjan'].sum()
            st.metric("Toplam Boş Kontenjan", f"{toplam_bos:,.0f}")
    else:
        st.warning(f"'{kategori_secim}' kategorisinde filtrelere uygun program bulunamadı.")

with tab3:
    st.header("Alan Bazlı Derinlemesine Analiz")
    
    # Puan türüne göre alan analizi
    if 'Puan Türü' in df.columns:
        st.subheader("Puan Türlerine Göre Detaylı Analiz")
        
        puan_analiz = df.groupby('Puan Türü').agg({
            'Doluluk_Orani': ['mean', 'min', 'max'],
            'Program Adı': 'count',
            'Bos_Kontenjan': 'sum'
        }).reset_index()
        
        puan_analiz.columns = ['Puan_Turu', 'Ortalama', 'Minimum', 'Maksimum', 'Program_Sayisi', 'Bos_Kontenjan']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Ortalama Doluluk',
            x=puan_analiz['Puan_Turu'],
            y=puan_analiz['Ortalama'],
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            name='Program Sayısı',
            x=puan_analiz['Puan_Turu'],
            y=puan_analiz['Program_Sayisi'],
            yaxis='y2',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title="Puan Türlerine Göre Doluluk ve Program Sayısı",
            xaxis_title="Puan Türü",
            yaxis=dict(title="Doluluk Oranı (%)"),
            yaxis2=dict(title="Program Sayısı", overlaying='y', side='right')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Her puan türünde en boş bölümler
        st.subheader("Puan Türlerine Göre En Boş Bölümler")
        
        for puan_turu in sorted(df['Puan Türü'].dropna().unique()):
            puan_df = df[df['Puan Türü'] == puan_turu]
            en_bos = puan_df.nsmallest(5, 'Doluluk_Orani')
            
            if not en_bos.empty:
                with st.expander(f"{puan_turu} - En Boş 5 Bölüm"):
                    display_cols = ['Program Adı', 'Üniversite Adı', 'İl', 'Kontenjan', 'Yerleşen', 'Doluluk_Orani']
                    available_cols = [col for col in display_cols if col in en_bos.columns]
                    st.dataframe(en_bos[available_cols].round(1), use_container_width=True)

with tab4:
    st.header("Popüler vs Boş Bölüm Analizleri")
    
    # En popüler (tam dolu) vs en boş karşılaştırması
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 En Popüler Bölümler (Tam Dolu)")
        tam_dolu = df[df['Doluluk_Orani'] >= 100].nlargest(15, 'Doluluk_Orani')
        
        if not tam_dolu.empty:
            fig = px.bar(
                tam_dolu.head(10),
                y='Program Adı',
                x='Doluluk_Orani',
                color='Program_Kategorisi',
                title="En Popüler 10 Bölüm",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Tam Dolu Bölüm Sayısı", len(tam_dolu))
        else:
            st.info("Tam dolu bölüm bulunamadı.")
    
    with col2:
        st.subheader("❄️ En Boş Bölümler")
        en_bos = df.nsmallest(15, 'Doluluk_Orani')
        
        if not en_bos.empty:
            fig = px.bar(
                en_bos.head(10),
                y='Program Adı',
                x='Doluluk_Orani',
                color='Program_Kategorisi',
                title="En Boş 10 Bölüm",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            bos_oran = len(df[df['Doluluk_Orani'] < 50]) / len(df[df['Doluluk_Orani'].notna()]) * 100
            st.metric("Boş Bölüm Oranı (%50<)", f"{bos_oran:.1f}%")
    
    # Kontenjan büyüklüğü vs popülerlik analizi
    st.subheader("Kontenjan Büyüklüğü vs Popülerlik İlişkisi")
    
    kontenjan_numeric = pd.to_numeric(df['Kontenjan'], errors='coerce')
    valid_data = df[df['Doluluk_Orani'].notna() & kontenjan_numeric.notna()]
    
    if not valid_data.empty:
        fig = px.scatter(
            valid_data.sample(min(1000, len(valid_data))),  # Sample alarak performansı artır
            x='Kontenjan',
            y='Doluluk_Orani',
            color='Program_Kategorisi',
            size='Bos_Kontenjan',
            title="Kontenjan vs Doluluk İlişkisi"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.header("Trend ve İçgörü Analizleri")
    
    # Üniversite türü vs bölüm kategorisi matrisi
    st.subheader("Üniversite Türü - Program Kategorisi Doluluk Matrisi")
    
    if 'Üniversite Türü' in df.columns:
        matrix_data = df.groupby(['Üniversite Türü', 'Program_Kategorisi'])['Doluluk_Orani'].mean().unstack()
        
        if not matrix_data.empty:
            fig = px.imshow(
                matrix_data.values,
                labels=dict(x="Program Kategorisi", y="Üniversite Türü", color="Ortalama Doluluk"),
                x=matrix_data.columns,
                y=matrix_data.index,
                title="Üniversite Türü - Program Kategorisi Doluluk Haritası"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Bölge bazında program kategorisi analizi
    if 'Bölge' in df.columns:
        st.subheader("Bölgesel Program Tercihleri")
        
        bolge_kategori = df.groupby(['Bölge', 'Program_Kategorisi']).size().unstack(fill_value=0)
        
        # En fazla programa sahip 5 kategori
        top_kategoriler = df['Program_Kategorisi'].value_counts().head(5).index
        bolge_kategori_top = bolge_kategori[top_kategoriler]
        
        fig = px.bar(
            bolge_kategori_top.reset_index(),
            x='Bölge',
            y=top_kategoriler.tolist(),
            title="Bölgelere Göre Popüler Program Kategorileri"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Özet istatistikler ve öneriler
    st.subheader("📋 Özet ve İçgörüler")
    
    insights = []
    
    # En boş kategori
    kategori_ortalama = df.groupby('Program_Kategorisi')['Doluluk_Orani'].mean().sort_values()
    if not kategori_ortalama.empty:
        insights.append(f"🔴 **En boş program kategorisi**: {kategori_ortalama.index[0]} ({kategori_ortalama.iloc[0]:.1f}% doluluk)")
    
    # En dolu kategori
    if len(kategori_ortalama) > 0:
        insights.append(f"🟢 **En dolu program kategorisi**: {kategori_ortalama.index[-1]} ({kategori_ortalama.iloc[-1]:.1f}% doluluk)")
    
    # Genel boşluk oranı
    total_kontenjan = pd.to_numeric(df['Kontenjan'], errors='coerce').sum()
    total_yerlesen = pd.to_numeric(df['Yerleşen'], errors='coerce').sum()
    genel_doluluk = (total_yerlesen / total_kontenjan * 100) if total_kontenjan > 0 else 0
    insights.append(f"📊 **Genel doluluk oranı**: {genel_doluluk:.1f}%")
    
    bos_program_sayisi = len(df[df['Doluluk_Orani'] < 50])
    insights.append(f"⚠️ **%50'den az dolu program sayısı**: {bos_program_sayisi:,}")
    
    for insight in insights:
        st.markdown(insight)

st.markdown("---")
st.caption("🔍 Bu sayfa fakülte ve bölüm bazlı derinlemesine analizler sunmaktadır.")
