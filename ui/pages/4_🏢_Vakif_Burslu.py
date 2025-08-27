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

st.title("🏢 Vakıf Üniversiteleri ve Burslu Program Analizleri")

@st.cache_data
def get_data():
    return load_processed()

df = get_data()

# Vakıf üniversiteleri filtrele
if 'Üniversite Türü' in df.columns:
    vakif_df = df[df['Üniversite Türü'].str.contains('Vakıf', case=False, na=False)]
else:
    st.error("Üniversite Türü sütunu bulunamadı!")
    st.stop()

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

if not vakif_df.empty:
    vakif_df = vakif_df.copy()
    vakif_df['Doluluk_Orani'] = vakif_df.apply(calculate_occupancy, axis=1)
    vakif_df['Bos_Kontenjan'] = pd.to_numeric(vakif_df['Kontenjan'], errors='coerce') - pd.to_numeric(vakif_df['Yerleşen'], errors='coerce')

    # Filtre seçenekleri
    st.sidebar.header("🔍 Vakıf Üniversiteleri Filtreleri")

    # Bölge filtresi
    if 'Bölge' in vakif_df.columns:
        bolge_listesi = ['Tümü'] + sorted(vakif_df['Bölge'].dropna().unique().tolist())
        secili_bolge = st.sidebar.selectbox("Bölge Seç", bolge_listesi)
        if secili_bolge != 'Tümü':
            vakif_df = vakif_df[vakif_df['Bölge'] == secili_bolge]

    # Şehir filtresi
    if 'İl' in vakif_df.columns:
        sehir_listesi = ['Tümü'] + sorted(vakif_df['İl'].dropna().unique().tolist())
        secili_sehir = st.sidebar.selectbox("Şehir Seç", sehir_listesi)
        if secili_sehir != 'Tümü':
            vakif_df = vakif_df[vakif_df['İl'] == secili_sehir]

    # Burslu program filtresi
    burs_durumu = st.sidebar.selectbox("Program Türü", ["Tümü", "Sadece Burslu", "Sadece Ücretli"])

    # Program türüne göre filtrele
    if burs_durumu != "Tümü":
        vakif_df['Burslu_Program'] = vakif_df['Program Adı'].str.contains('Burslu|BURSLU|%50|%25|%75|%100', case=False, na=False)
        if burs_durumu == "Sadece Burslu":
            vakif_df = vakif_df[vakif_df['Burslu_Program'] == True]
        else:  # Sadece Ücretli
            vakif_df = vakif_df[vakif_df['Burslu_Program'] == False]

    # Kontenjan aralığı filtresi
    min_kontenjan = st.sidebar.number_input("Minimum Kontenjan", min_value=0, value=0, step=25)
    vakif_df = vakif_df[pd.to_numeric(vakif_df['Kontenjan'], errors='coerce') >= min_kontenjan]

    # Doluluk oranı filtresi
    doluluk_araligi = st.sidebar.slider("Doluluk Oranı Aralığı (%)", 0, 100, (0, 100), step=5)
    vakif_df = vakif_df[
        (vakif_df['Doluluk_Orani'] >= doluluk_araligi[0]) & 
        (vakif_df['Doluluk_Orani'] <= doluluk_araligi[1])
    ]

    st.sidebar.caption("💡 Filtreler tüm sekmelerdeki analizleri etkiler. Burslu/Ücretli filtresi ile istediğiniz program türünü seçebilirsiniz.")

st.markdown("---")

# Genel özet
if not vakif_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Vakıf Programı", f"{len(vakif_df):,}")
    with col2:
        total_kontenjan = pd.to_numeric(vakif_df['Kontenjan'], errors='coerce').sum()
        st.metric("Toplam Kontenjan", f"{total_kontenjan:,.0f}")
    with col3:
        total_yerlesen = pd.to_numeric(vakif_df['Yerleşen'], errors='coerce').sum()
        st.metric("Toplam Yerleşen", f"{total_yerlesen:,.0f}")
    with col4:
        genel_doluluk = (total_yerlesen / total_kontenjan * 100) if total_kontenjan > 0 else 0
        st.metric("Genel Doluluk", f"{genel_doluluk:.1f}%")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["💰 Burslu/Ücretli Analizi", "🏢 Vakıf Üniversiteleri", "📍 Şehir/Bölge Durumu", "📊 Karşılaştırmalı Analiz"])

with tab1:
    st.header("Burslu ve Ücretli Program Analizleri")
    
    if not vakif_df.empty:
        # Program adında "burslu" geçenleri tespit et
        vakif_df_copy = vakif_df.copy()
        vakif_df_copy['Burslu_Program'] = vakif_df_copy['Program Adı'].str.contains('Burslu|BURSLU|%50|%25|%75|%100', case=False, na=False)
        
        burslu_programs = vakif_df_copy[vakif_df_copy['Burslu_Program'] == True].copy()
        ucretli_programs = vakif_df_copy[vakif_df_copy['Burslu_Program'] == False].copy()
        
        # Özet
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎓 Burslu Programlar")
            if not burslu_programs.empty:
                st.metric("Burslu Program Sayısı", len(burslu_programs))
                burslu_doluluk = burslu_programs['Doluluk_Orani'].mean()
                st.metric("Ortalama Doluluk", f"{burslu_doluluk:.1f}%")
                
                # Burs oranına göre kategorizasyon
                burslu_programs['Burs_Kategorisi'] = 'Diğer Burslu'
                burslu_programs.loc[burslu_programs['Program Adı'].str.contains('%100|100%', case=False, na=False), 'Burs_Kategorisi'] = '%100 Burslu'
                burslu_programs.loc[burslu_programs['Program Adı'].str.contains('%75|75%', case=False, na=False), 'Burs_Kategorisi'] = '%75 Burslu'
                burslu_programs.loc[burslu_programs['Program Adı'].str.contains('%50|50%', case=False, na=False), 'Burs_Kategorisi'] = '%50 Burslu'
                burslu_programs.loc[burslu_programs['Program Adı'].str.contains('%25|25%', case=False, na=False), 'Burs_Kategorisi'] = '%25 Burslu'
                
                # Burs kategorisi dağılımı
                burs_dagilim = burslu_programs['Burs_Kategorisi'].value_counts()
                fig_pie = px.pie(
                    values=burs_dagilim.values,
                    names=burs_dagilim.index,
                    title="Burs Oranı Dağılımı"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Burslu program bulunamadı.")
        
        with col2:
            st.subheader("💸 Ücretli Programlar")
            if not ucretli_programs.empty:
                st.metric("Ücretli Program Sayısı", len(ucretli_programs))
                ucretli_doluluk = ucretli_programs['Doluluk_Orani'].mean()
                st.metric("Ortalama Doluluk", f"{ucretli_doluluk:.1f}%")
            else:
                st.info("Ücretli program bulunamadı.")
        
        # Karşılaştırmalı analiz
        if not burslu_programs.empty and not ucretli_programs.empty:
            st.subheader("Burslu vs Ücretli Program Karşılaştırması")
            
            # Doluluk oranı karşılaştırma
            comparison_data = pd.DataFrame({
                'Program Türü': ['Burslu', 'Ücretli'],
                'Ortalama Doluluk': [burslu_doluluk, ucretli_doluluk],
                'Program Sayısı': [len(burslu_programs), len(ucretli_programs)]
            })
            
            fig = px.bar(
                comparison_data,
                x='Program Türü',
                y='Ortalama Doluluk',
                color='Program Sayısı',
                title="Burslu vs Ücretli Programlarda Ortalama Doluluk"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # En boş burslu programlar
            st.subheader("En Boş Kalan Burslu Programlar")
            
            if not burslu_programs.empty:
                en_bos_burslu = burslu_programs.nsmallest(15, 'Doluluk_Orani')
                
                if not en_bos_burslu.empty:
                    fig = px.bar(
                        en_bos_burslu.head(10),
                        y='Program Adı',
                        x='Doluluk_Orani',
                        color='Burs_Kategorisi',
                        title="En Boş 10 Burslu Program",
                        orientation='h',
                        labels={
                            'Program Adı': 'Program Adı',
                            'Doluluk_Orani': '% Doluluk Oranı',
                            'Burs_Kategorisi': 'Burs Kategorisi'
                        },
                        hover_data=['Üniversite Adı', 'İl', 'Kontenjan', 'Yerleşen']
                    )
                    fig.update_xaxes(title="% Doluluk Oranı", ticksuffix="%")
                    fig.update_yaxes(title="Program Adı")
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("📊 Bu grafik en boş 10 burslu programı gösterir. Çubuk uzunluğu doluluk oranını, renk ise burs kategorisini temsil eder.")
                    
                    # Özet bilgiler
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1:
                        st.metric("Toplam Burslu Program", len(burslu_programs))
                    with col_b2:
                        ortalama_burslu_doluluk = burslu_programs['Doluluk_Orani'].mean()
                        st.metric("Ortalama Doluluk", f"{ortalama_burslu_doluluk:.1f}%")
                    with col_b3:
                        en_bos_burslu_doluluk = en_bos_burslu['Doluluk_Orani'].min()
                        st.metric("En Boş Program Doluluk", f"{en_bos_burslu_doluluk:.1f}%")
                else:
                    st.info("Filtrelere uygun burslu program bulunamadı.")
            else:
                st.warning("Seçilen kriterlere uygun burslu program bulunamadı. Filtreleri değiştirerek tekrar deneyin.")

with tab2:
    st.header("Vakıf Üniversiteleri Detaylı Analizi")
    
    if not vakif_df.empty and 'Üniversite Adı' in vakif_df.columns:
        # Üniversite bazında analiz
        uni_analiz = vakif_df.groupby('Üniversite Adı').agg({
            'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Program Adı': 'count'
        }).reset_index()
        
        uni_analiz['Doluluk_Orani'] = (uni_analiz['Yerleşen'] / uni_analiz['Kontenjan'] * 100)
        uni_analiz['Bos_Kontenjan'] = uni_analiz['Kontenjan'] - uni_analiz['Yerleşen']
        
        # En boş vakıf üniversiteleri
        st.subheader("En Boş Kalan Vakıf Üniversiteleri")
        en_bos_vakif = uni_analiz.nsmallest(15, 'Doluluk_Orani')
        
        fig = px.scatter(
            en_bos_vakif,
            x='Kontenjan',
            y='Doluluk_Orani',
            size='Bos_Kontenjan',
            hover_data=['Üniversite Adı'],
            title="En Boş 15 Vakıf Üniversitesi"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # En başarılı vakıf üniversiteleri
        st.subheader("En Dolu Vakıf Üniversiteleri")
        en_dolu_vakif = uni_analiz.nlargest(15, 'Doluluk_Orani')
        
        fig = px.bar(
            en_dolu_vakif,
            y='Üniversite Adı',
            x='Doluluk_Orani',
            title="En Dolu 15 Vakıf Üniversitesi",
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Kontenjan büyüklüğüne göre kategorize etme
        st.subheader("Kontenjan Büyüklüğüne Göre Vakıf Üniversiteleri")
        
        uni_analiz['Kategori'] = pd.cut(
            uni_analiz['Kontenjan'],
            bins=[0, 500, 1500, 3000, float('inf')],
            labels=['Küçük (0-500)', 'Orta (501-1500)', 'Büyük (1501-3000)', 'Çok Büyük (3000+)']
        )
        
        kategori_analiz = uni_analiz.groupby('Kategori', observed=True).agg({
            'Doluluk_Orani': 'mean',
            'Üniversite Adı': 'count'
        }).reset_index()
        
        fig = px.bar(
            kategori_analiz,
            x='Kategori',
            y='Doluluk_Orani',
            color='Üniversite Adı',
            title="Kontenjan Büyüklüğüne Göre Ortalama Doluluk",
            labels={'Üniversite Adı': 'Üniversite Sayısı'}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Vakıf Üniversitelerinde Şehir/Bölge Durumu")
    
    if not vakif_df.empty:
        # Şehir analizi
        if 'İl' in vakif_df.columns:
            st.subheader("Şehirlere Göre Vakıf Üniversitesi Durumu")
            
            sehir_analiz = vakif_df.groupby('İl').agg({
                'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Üniversite Adı': 'nunique'
            }).reset_index()
            
            sehir_analiz['Doluluk_Orani'] = (sehir_analiz['Yerleşen'] / sehir_analiz['Kontenjan'] * 100)
            
            # En fazla vakıf üniversitesi olan şehirler
            en_fazla_vakif = sehir_analiz.nlargest(10, 'Üniversite Adı')
            
            fig = px.bar(
                en_fazla_vakif,
                x='İl',
                y='Üniversite Adı',
                color='Doluluk_Orani',
                title="En Fazla Vakıf Üniversitesi Olan Şehirler",
                labels={'Üniversite Adı': 'Vakıf Üniversite Sayısı'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Bölge analizi
        if 'Bölge' in vakif_df.columns:
            st.subheader("Bölgelere Göre Vakıf Üniversiteleri")
            
            bolge_analiz = vakif_df.groupby('Bölge').agg({
                'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Program Adı': 'count'
            }).reset_index()
            
            bolge_analiz['Doluluk_Orani'] = (bolge_analiz['Yerleşen'] / bolge_analiz['Kontenjan'] * 100)
            
            fig = px.bar(
                bolge_analiz.sort_values('Doluluk_Orani'),
                x='Bölge',
                y='Doluluk_Orani',
                color='Program Adı',
                title="Bölgelere Göre Vakıf Üniversiteleri Doluluk Oranı",
                labels={'Program Adı': 'Program Sayısı'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Vakıf vs Devlet Karşılaştırması")
    
    # Devlet üniversiteleri de dahil edelim
    devlet_df = df[df['Üniversite Türü'].str.contains('Devlet', case=False, na=False)] if 'Üniversite Türü' in df.columns else pd.DataFrame()
    
    if not vakif_df.empty and not devlet_df.empty:
        devlet_df = devlet_df.copy()
        devlet_df['Doluluk_Orani'] = devlet_df.apply(calculate_occupancy, axis=1)
        
        # Genel karşılaştırma
        vakif_ortalama = vakif_df['Doluluk_Orani'].mean()
        devlet_ortalama = devlet_df['Doluluk_Orani'].mean()
        
        comparison_df = pd.DataFrame({
            'Üniversite Türü': ['Vakıf', 'Devlet'],
            'Ortalama Doluluk': [vakif_ortalama, devlet_ortalama],
            'Program Sayısı': [len(vakif_df), len(devlet_df)]
        })
        
        fig = px.bar(
            comparison_df,
            x='Üniversite Türü',
            y='Ortalama Doluluk',
            color='Program Sayısı',
            title="Vakıf vs Devlet Üniversiteleri Ortalama Doluluk Karşılaştırması"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Doluluk dağılımı karşılaştırması
        st.subheader("Doluluk Oranı Dağılımı Karşılaştırması")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=vakif_df['Doluluk_Orani'].dropna(),
            name='Vakıf',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=devlet_df['Doluluk_Orani'].dropna(),
            name='Devlet',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.update_layout(
            title="Vakıf vs Devlet Üniversiteleri Doluluk Oranı Dağılımı",
            xaxis_title="Doluluk Oranı (%)",
            yaxis_title="Program Sayısı",
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Özet istatistikler
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Vakıf Üniversiteleri")
            st.metric("Ortalama Doluluk", f"{vakif_ortalama:.1f}%")
            st.metric("Medyan Doluluk", f"{vakif_df['Doluluk_Orani'].median():.1f}%")
            bos_vakif = len(vakif_df[vakif_df['Doluluk_Orani'] < 50])
            st.metric("<%50 Dolu Program", bos_vakif)
        
        with col2:
            st.subheader("Devlet Üniversiteleri")
            st.metric("Ortalama Doluluk", f"{devlet_ortalama:.1f}%")
            st.metric("Medyan Doluluk", f"{devlet_df['Doluluk_Orani'].median():.1f}%")
            bos_devlet = len(devlet_df[devlet_df['Doluluk_Orani'] < 50])
            st.metric("<%50 Dolu Program", bos_devlet)
    
    else:
        st.warning("Karşılaştırma için yeterli veri bulunamadı.")

st.markdown("---")
st.caption("🏢 Bu analizler vakıf üniversiteleri ve burslu programlar odaklıdır.")
