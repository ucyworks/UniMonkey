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

st.title("🏛️ Devlet Üniversiteleri Analizi")

@st.cache_data
def get_data():
    return load_processed()

df = get_data()

# Sadece devlet üniversiteleri
if 'Üniversite Türü' in df.columns:
    devlet_df = df[df['Üniversite Türü'].str.contains('Devlet', case=False, na=False)]
else:
    st.error("Üniversite Türü sütunu bulunamadı!")
    st.stop()

if devlet_df.empty:
    st.error("Devlet üniversitesi verisi bulunamadı!")
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

devlet_df = devlet_df.copy()
devlet_df['Doluluk_Orani'] = devlet_df.apply(calculate_occupancy, axis=1)
devlet_df['Bos_Kontenjan'] = pd.to_numeric(devlet_df['Kontenjan'], errors='coerce') - pd.to_numeric(devlet_df['Yerleşen'], errors='coerce')

# Filtre seçenekleri
st.sidebar.header("🔍 Devlet Üniversiteleri Filtreleri")

# Bölge filtresi
if 'Bölge' in devlet_df.columns:
    bolge_listesi = ['Tümü'] + sorted(devlet_df['Bölge'].dropna().unique().tolist())
    secili_bolge = st.sidebar.selectbox("Bölge Seç", bolge_listesi)
    if secili_bolge != 'Tümü':
        devlet_df = devlet_df[devlet_df['Bölge'] == secili_bolge]

# Şehir filtresi
if 'İl' in devlet_df.columns:
    sehir_listesi = ['Tümü'] + sorted(devlet_df['İl'].dropna().unique().tolist())
    secili_sehir = st.sidebar.selectbox("Şehir Seç", sehir_listesi)
    if secili_sehir != 'Tümü':
        devlet_df = devlet_df[devlet_df['İl'] == secili_sehir]

# Kontenjan aralığı filtresi
min_kontenjan = st.sidebar.number_input("Minimum Kontenjan", min_value=0, value=0, step=50)
devlet_df = devlet_df[pd.to_numeric(devlet_df['Kontenjan'], errors='coerce') >= min_kontenjan]

# Doluluk oranı filtresi
doluluk_araligi = st.sidebar.slider("Doluluk Oranı Aralığı (%)", 0, 100, (0, 100), step=5)
devlet_df = devlet_df[
    (devlet_df['Doluluk_Orani'] >= doluluk_araligi[0]) & 
    (devlet_df['Doluluk_Orani'] <= doluluk_araligi[1])
]

st.sidebar.caption("💡 Filtreler tüm sekmelerdeki analizleri etkiler. Bölge ve şehir filtrelerini kullanarak detaylı incelemeler yapabilirsiniz.")

st.markdown("---")

# Genel özet
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Toplam Devlet Programı", f"{len(devlet_df):,}")
with col2:
    total_kontenjan = pd.to_numeric(devlet_df['Kontenjan'], errors='coerce').sum()
    st.metric("Toplam Kontenjan", f"{total_kontenjan:,.0f}")
with col3:
    total_yerlesen = pd.to_numeric(devlet_df['Yerleşen'], errors='coerce').sum()
    st.metric("Toplam Yerleşen", f"{total_yerlesen:,.0f}")
with col4:
    genel_doluluk = (total_yerlesen / total_kontenjan * 100) if total_kontenjan > 0 else 0
    st.metric("Genel Doluluk", f"{genel_doluluk:.1f}%")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📍 Şehir/Bölge Analizi", "🏫 Üniversite Analizi", "📚 Fakülte Analizi", "🔍 Detaylı İncelemeler"])

with tab1:
    st.header("Devlet Üniversitelerinde Şehir/Bölge Bazlı Durum")
    
    if devlet_df.empty:
        st.warning("Seçilen filtrelere uygun devlet üniversitesi verisi bulunamadı.")
    else:
        # Bölge-by-bölge detaylı analiz
        if 'Bölge' in devlet_df.columns and secili_bolge == 'Tümü':
            st.subheader("🌍 Bölgelere Göre Kapsamlı Analiz")
            
            bolge_analiz = devlet_df.groupby('Bölge').agg({
                'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Program Adı': 'count',
                'Üniversite Adı': 'nunique',
                'İl': 'nunique'
            }).reset_index()
            
            bolge_analiz.columns = ['Bölge', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 'Program_Sayisi', 'Uni_Sayisi', 'Sehir_Sayisi']
            bolge_analiz['Doluluk_Orani'] = (bolge_analiz['Toplam_Yerlesen'] / bolge_analiz['Toplam_Kontenjan'] * 100)
            bolge_analiz['Bos_Kontenjan'] = bolge_analiz['Toplam_Kontenjan'] - bolge_analiz['Toplam_Yerlesen']
            bolge_analiz['Bos_Yuzde'] = (bolge_analiz['Bos_Kontenjan'] / bolge_analiz['Toplam_Kontenjan'] * 100)
            
            bolge_analiz = bolge_analiz.dropna(subset=['Bölge'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bölge doluluk çubuk grafiği
                fig_bolge = px.bar(
                    bolge_analiz.sort_values('Doluluk_Orani'),
                    x='Bölge',
                    y='Doluluk_Orani',
                    color='Bos_Kontenjan',
                    title="Bölgelere Göre Devlet Üniversiteleri Doluluk Oranı",
                    labels={'Doluluk_Orani': '% Doluluk Oranı', 'Bos_Kontenjan': 'Boş Kontenjan'},
                    color_continuous_scale='Reds'
                )
                fig_bolge.update_xaxes(tickangle=45)
                fig_bolge.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                st.plotly_chart(fig_bolge, use_container_width=True)
                st.caption("📊 Bu grafik bölgelerin devlet üniversitelerindeki doluluk oranlarını gösterir. X ekseni bölgeleri, Y ekseni doluluk yüzdesini gösterir. Renk yoğunluğu boş kontenjan miktarını temsil eder - koyu renkler daha fazla boş kontenjan anlamına gelir.")
                
                # Bölge pasta grafiği
                fig_pie_bolge = px.pie(
                    bolge_analiz,
                    values='Program_Sayisi',
                    names='Bölge',
                    title="Bölgelere Göre Program Dağılımı",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
                )
                fig_pie_bolge.update_traces(
                    textposition='inside', 
                    textinfo='label+percent',  
                    textfont_size=12,
                    textfont_color="white",
                    textfont_family="Arial Black",
                    marker=dict(
                        line=dict(color='white', width=3)
                    ),
                    pull=[0.1 if val == bolge_analiz['Program_Sayisi'].max() else 0 for val in bolge_analiz['Program_Sayisi']],
                    hovertemplate='<b>Bölge:</b> %{label}<br><b>Program Sayısı:</b> %{value}<br><b>Toplam Yüzdesi:</b> %{percent}<br><extra></extra>'
                )
                fig_pie_bolge.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=11),
                        title=dict(
                            text="<b>Bölgeler</b>",
                            font=dict(size=12)
                        )
                    ),
                    font=dict(size=12),
                    title_font=dict(size=16, color='darkblue'),
                    margin=dict(l=20, r=120, t=50, b=20)
                )
                st.plotly_chart(fig_pie_bolge, use_container_width=True)
                st.caption("🥧 Bu pasta grafiği devlet üniversitesi programlarının bölgelere göre dağılımını gösterir. Her dilim bir bölgeyi temsil eder ve o bölgedeki toplam program sayısının oranını gösterir.")
            
            with col2:
                # Scatter plot - Kontenjan vs Doluluk
                fig_scatter_bolge = px.scatter(
                    bolge_analiz,
                    x='Toplam_Kontenjan',
                    y='Doluluk_Orani',
                    size='Program_Sayisi',
                    color='Bölge',
                    title="Bölge Bazlı Kontenjan-Doluluk İlişkisi",
                    labels={
                        'Toplam_Kontenjan': 'Toplam Kontenjan', 
                        'Doluluk_Orani': '% Doluluk Oranı',
                        'Program_Sayisi': 'Program Sayısı',
                        'Bölge': 'Bölge'
                    },
                    hover_data={
                        'Uni_Sayisi': True, 
                        'Sehir_Sayisi': True
                    }
                )
                fig_scatter_bolge.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                st.plotly_chart(fig_scatter_bolge, use_container_width=True)
                st.caption("🎯 Bu scatter plot bölgelerin toplam kontenjanı ile doluluk oranı arasındaki ilişkiyi gösterir. Her nokta bir bölgeyi temsil eder. Nokta büyüklüğü program sayısını, renk ise bölgeyi gösterir. Sağ üstteki noktalar hem büyük hem de dolu bölgelerdir.")
                
                # Bar chart - Boş kontenjan
                fig_bar_bos = px.bar(
                    bolge_analiz.sort_values('Bos_Kontenjan', ascending=False),
                    x='Bölge',
                    y='Bos_Kontenjan',
                    title="Bölgelere Göre Toplam Boş Kontenjan",
                    labels={
                        'Bölge': 'Bölge',
                        'Bos_Kontenjan': 'Boş Kontenjan',
                        'Doluluk_Orani': '% Doluluk Oranı'
                    },
                    color='Doluluk_Orani',
                    color_continuous_scale='RdYlGn'
                )
                fig_bar_bos.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar_bos, use_container_width=True)
                st.caption("📈 Bu grafik bölgelerdeki toplam boş kontenjan sayısını gösterir. Yüksek çubuklar o bölgede daha fazla boş kontenjan olduğunu, renk ise doluluk oranını gösterir (yeşil yüksek, kırmızı düşük doluluk).")
            
            # Detaylı bölge tablosu
            st.subheader("📋 Bölge Bazlı Detaylı İstatistikler")
            table_df = bolge_analiz.sort_values('Doluluk_Orani').copy()
            table_df.columns = ['Bölge', 'Toplam Kontenjan', 'Toplam Yerleşen', 'Program Sayısı', 
                              'Üniversite Sayısı', 'Şehir Sayısı', '% Doluluk Oranı', 'Boş Kontenjan', '% Boş Yüzde']
            
            st.dataframe(
                table_df,
                column_config={
                    'Toplam Kontenjan': st.column_config.NumberColumn(format="%d"),
                    'Toplam Yerleşen': st.column_config.NumberColumn(format="%d"),
                    'Program Sayısı': st.column_config.NumberColumn(format="%d"),
                    'Üniversite Sayısı': st.column_config.NumberColumn(format="%d"),
                    'Şehir Sayısı': st.column_config.NumberColumn(format="%d"),
                    '% Doluluk Oranı': st.column_config.NumberColumn(format="%.1f%%"),
                    'Boş Kontenjan': st.column_config.NumberColumn(format="%d"),
                    '% Boş Yüzde': st.column_config.NumberColumn(format="%.1f%%")
                },
                use_container_width=True
            )
        
        # Şehir analizi
        if 'İl' in devlet_df.columns:
            st.subheader(f"🏙️ En Boş Kalan Devlet Üniversitesi Şehirleri {f'({secili_bolge} Bölgesi)' if secili_bolge != 'Tümü' else ''}")
            
            sehir_analiz = devlet_df.groupby('İl').agg({
                'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Program Adı': 'count',
                'Üniversite Adı': 'nunique',
                'Bölge': 'first'
            }).reset_index()
            
            sehir_analiz.columns = ['Sehir', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 'Program_Sayisi', 'Uni_Sayisi', 'Bolge']
            sehir_analiz['Doluluk_Orani'] = (sehir_analiz['Toplam_Yerlesen'] / sehir_analiz['Toplam_Kontenjan'] * 100)
            sehir_analiz['Bos_Kontenjan'] = sehir_analiz['Toplam_Kontenjan'] - sehir_analiz['Toplam_Yerlesen']
            sehir_analiz['Bos_Yuzde'] = (sehir_analiz['Bos_Kontenjan'] / sehir_analiz['Toplam_Kontenjan'] * 100)
            
            if not sehir_analiz.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # En boş şehirler
                    en_bos_sehirler = sehir_analiz.dropna(subset=['Sehir']).nsmallest(15, 'Doluluk_Orani')
                    
                    fig_sehir = px.bar(
                        en_bos_sehirler,
                        y='Sehir',
                        x='Doluluk_Orani',
                        color='Bolge',
                        title=f"En Boş 15 Şehir {f'({secili_bolge} Bölgesi)' if secili_bolge != 'Tümü' else ''}",
                        orientation='h',
                        labels={
                            'Doluluk_Orani': '% Doluluk Oranı',
                            'Sehir': 'Şehir',
                            'Bolge': 'Bölge',
                            'Program_Sayisi': 'Program Sayısı',
                            'Uni_Sayisi': 'Üniversite Sayısı',
                            'Bos_Kontenjan': 'Boş Kontenjan'
                        },
                        hover_data=['Program_Sayisi', 'Uni_Sayisi', 'Bos_Kontenjan']
                    )
                    fig_sehir.update_xaxes(title="% Doluluk Oranı", ticksuffix="%")
                    st.plotly_chart(fig_sehir, use_container_width=True)
                    st.caption("🏙️ Bu yatay çubuk grafik en boş devlet üniversitesi şehirlerini gösterir. Uzun çubuklar daha yüksek doluluk oranını, renkler ise şehrin bulunduğu bölgeyi temsil eder.")
                
                with col2:
                    # En çok boş kontenjan
                    en_bos_kontenjan_sehir = sehir_analiz.nlargest(15, 'Bos_Kontenjan')
                    
                    fig_bos_kont = px.bar(
                        en_bos_kontenjan_sehir,
                        y='Sehir',
                        x='Bos_Kontenjan',
                        color='Doluluk_Orani',
                        title="En Çok Boş Kontenjanı Olan 15 Şehir",
                        orientation='h',
                        labels={
                            'Bos_Kontenjan': 'Boş Kontenjan',
                            'Sehir': 'Şehir',
                            'Doluluk_Orani': '% Doluluk Oranı'
                        },
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_bos_kont, use_container_width=True)
                    st.caption("📊 Bu grafik en çok boş kontenjanı olan şehirleri gösterir. Çubuk uzunluğu boş kontenjan miktarını, renk yoğunluğu ise doluluk oranını temsil eder (koyu kırmızı = düşük doluluk).")
                
                # Şehir özelinde detaylı filtre
                if st.checkbox("📊 Detaylı Şehir Analizi Göster"):
                    secilen_sehir_analiz = st.selectbox(
                        "Analiz Edilecek Şehiri Seçin:",
                        sehir_analiz['Sehir'].sort_values().tolist()
                    )
                    
                    secilen_sehir_detay = devlet_df[devlet_df['İl'] == secilen_sehir_analiz]
                    
                    if not secilen_sehir_detay.empty:
                        st.write(f"**{secilen_sehir_analiz} Şehri Devlet Üniversiteleri Detayı:**")
                        
                        # Üniversite bazlı analiz
                        uni_detay = secilen_sehir_detay.groupby('Üniversite Adı').agg({
                            'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                            'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                            'Program Adı': 'count'
                        }).reset_index()
                        
                        uni_detay['Doluluk_Orani'] = (uni_detay['Yerleşen'] / uni_detay['Kontenjan'] * 100)
                        uni_detay['Bos_Kontenjan'] = uni_detay['Kontenjan'] - uni_detay['Yerleşen']
                        
                        # Metrics
                        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
                        with col_met1:
                            st.metric("Toplam Üniversite", len(uni_detay))
                        with col_met2:
                            st.metric("Toplam Program", len(secilen_sehir_detay))
                        with col_met3:
                            ortalama_doluluk = uni_detay['Doluluk_Orani'].mean()
                            st.metric("Ortalama Doluluk", f"{ortalama_doluluk:.1f}%")
                        with col_met4:
                            toplam_bos = uni_detay['Bos_Kontenjan'].sum()
                            st.metric("Toplam Boş Kontenjan", f"{toplam_bos:,.0f}")
                        
                        # Şehir içi üniversite karşılaştırması
                        if len(uni_detay) > 1:
                            fig_sehir_uni = px.bar(
                                uni_detay.sort_values('Doluluk_Orani'),
                                x='Üniversite Adı',
                                y='Doluluk_Orani',
                                color='Bos_Kontenjan',
                                title=f"{secilen_sehir_analiz} Şehri Devlet Üniversiteleri Karşılaştırması",
                                labels={
                                    'Üniversite Adı': 'Üniversite Adı',
                                    'Doluluk_Orani': '% Doluluk Oranı',
                                    'Bos_Kontenjan': 'Boş Kontenjan'
                                }
                            )
                            fig_sehir_uni.update_xaxes(tickangle=45)
                            fig_sehir_uni.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                            st.plotly_chart(fig_sehir_uni, use_container_width=True)
                            st.caption(f"🏫 Bu grafik {secilen_sehir_analiz} şehrindeki devlet üniversitelerinin doluluk oranlarını karşılaştırır. Her çubuk bir üniversiteyi, renk yoğunluğu ise boş kontenjan miktarını gösterir.")
                        
                        st.dataframe(uni_detay.sort_values('Doluluk_Orani'), use_container_width=True)

with tab2:
    st.header(f"Üniversite Bazında Analiz {f'({secili_bolge} Bölgesi)' if secili_bolge != 'Tümü' else ''}")
    
    if devlet_df.empty:
        st.warning("Seçilen filtrelere uygun devlet üniversitesi verisi bulunamadı.")
    else:
        # Üniversite performansı
        if 'Üniversite Adı' in devlet_df.columns:
            uni_analiz = devlet_df.groupby('Üniversite Adı').agg({
                'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'Program Adı': 'count',
                'İl': 'first',
                'Bölge': 'first'
            }).reset_index()
            
            uni_analiz.columns = ['Uni_Adi', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 'Program_Sayisi', 'Sehir', 'Bolge']
            uni_analiz['Doluluk_Orani'] = (uni_analiz['Toplam_Yerlesen'] / uni_analiz['Toplam_Kontenjan'] * 100)
            uni_analiz['Bos_Kontenjan'] = uni_analiz['Toplam_Kontenjan'] - uni_analiz['Toplam_Yerlesen']
            uni_analiz['Bos_Yuzde'] = (uni_analiz['Bos_Kontenjan'] / uni_analiz['Toplam_Kontenjan'] * 100)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # En boş üniversiteler
                st.subheader("En Boş Kalan Devlet Üniversiteleri")
                en_bos_uniler = uni_analiz.nsmallest(20, 'Doluluk_Orani')
                
                fig_scatter_uni = px.scatter(
                    en_bos_uniler,
                    x='Toplam_Kontenjan',
                    y='Doluluk_Orani',
                    size='Bos_Kontenjan',
                    color='Bolge',
                    hover_data=['Uni_Adi', 'Sehir', 'Program_Sayisi'],
                    title="En Boş 20 Devlet Üniversitesi (Kontenjan vs Doluluk)",
                    labels={
                        'Doluluk_Orani': '% Doluluk Oranı', 
                        'Toplam_Kontenjan': 'Toplam Kontenjan',
                        'Bos_Kontenjan': 'Boş Kontenjan',
                        'Bolge': 'Bölge',
                        'Uni_Adi': 'Üniversite Adı',
                        'Sehir': 'Şehir',
                        'Program_Sayisi': 'Program Sayısı'
                    }
                )
                fig_scatter_uni.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                st.plotly_chart(fig_scatter_uni, use_container_width=True)
                st.caption("🎯 Bu scatter plot en boş 20 devlet üniversitesinin kontenjan-doluluk ilişkisini gösterir. X ekseni toplam kontenjan, Y ekseni doluluk oranı, nokta büyüklüğü boş kontenjan, renk ise bölgeyi temsil eder.")
                
                # En çok boş kontenjan
                st.subheader("En Çok Boş Kontenjanı Olan Üniversiteler")
                en_bos_kontenjan_uni = uni_analiz.nlargest(15, 'Bos_Kontenjan')
                
                fig_bar_bos_uni = px.bar(
                    en_bos_kontenjan_uni.head(10),
                    y='Uni_Adi',
                    x='Bos_Kontenjan',
                    color='Doluluk_Orani',
                    title="En Çok Boş Kontenjanı Olan 10 Devlet Üniversitesi",
                    orientation='h',
                    labels={
                        'Uni_Adi': 'Üniversite Adı',
                        'Bos_Kontenjan': 'Boş Kontenjan',
                        'Doluluk_Orani': '% Doluluk Oranı'
                    },
                    color_continuous_scale='RdYlBu'
                )
                st.plotly_chart(fig_bar_bos_uni, use_container_width=True)
                st.caption("📊 Bu yatay çubuk grafik en fazla boş kontenjanı olan devlet üniversitelerini gösterir. Çubuk uzunluğu boş kontenjan sayısını, renk ise doluluk oranını temsil eder.")
            
            with col2:
                # En başarılı üniversiteler
                st.subheader("En Dolu Devlet Üniversiteleri")
                en_dolu_uniler = uni_analiz.nlargest(15, 'Doluluk_Orani')
                
                fig_bar_dolu = px.bar(
                    en_dolu_uniler,
                    y='Uni_Adi',
                    x='Doluluk_Orani',
                    color='Bolge',
                    title="En Dolu 15 Devlet Üniversitesi",
                    orientation='h',
                    labels={
                        'Doluluk_Orani': '% Doluluk Oranı',
                        'Uni_Adi': 'Üniversite Adı',
                        'Bolge': 'Bölge'
                    }
                )
                fig_bar_dolu.update_xaxes(title="% Doluluk Oranı", ticksuffix="%")
                st.plotly_chart(fig_bar_dolu, use_container_width=True)
                st.caption("🏆 Bu grafik en dolu 15 devlet üniversitesini gösterir. Çubuk uzunluğu doluluk oranını, renkler ise üniversitenin bulunduğu bölgeyi temsil eder.")
                
                # Üniversite büyüklüğü analizi
                st.subheader("Üniversite Büyüklüğü vs Doluluk")
                fig_size_perf = px.scatter(
                    uni_analiz,
                    x='Program_Sayisi',
                    y='Doluluk_Orani',
                    size='Toplam_Kontenjan',
                    color='Bolge',
                    hover_data=['Uni_Adi', 'Sehir'],
                    title="Program Sayısı vs Doluluk Oranı İlişkisi",
                    labels={
                        'Program_Sayisi': 'Program Sayısı', 
                        'Doluluk_Orani': '% Doluluk Oranı',
                        'Toplam_Kontenjan': 'Toplam Kontenjan',
                        'Bolge': 'Bölge',
                        'Uni_Adi': 'Üniversite Adı',
                        'Sehir': 'Şehir'
                    }
                )
                fig_size_perf.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                st.plotly_chart(fig_size_perf, use_container_width=True)
                st.caption("🔍 Bu scatter plot üniversitelerin program sayısı ile doluluk oranı arasındaki ilişkiyi analiz eder. Nokta büyüklüğü toplam kontenjanı, renk bölgeyi gösterir. Sağ üstteki noktalar hem çok programlı hem de dolu üniversitelerdir.")
            
            # Özet istatistikler
            st.subheader("📊 Üniversite Performans Özetleri")
            col_met1, col_met2, col_met3, col_met4, col_met5 = st.columns(5)
            
            with col_met1:
                st.metric("Toplam Üniversite", len(uni_analiz))
            with col_met2:
                ortalama_doluluk = uni_analiz['Doluluk_Orani'].mean()
                st.metric("Ortalama Doluluk", f"{ortalama_doluluk:.1f}%")
            with col_met3:
                bos_uni_sayisi = len(uni_analiz[uni_analiz['Doluluk_Orani'] < 70])
                st.metric("<%70 Dolu Üniversite", bos_uni_sayisi)
            with col_met4:
                tam_dolu_uni = len(uni_analiz[uni_analiz['Doluluk_Orani'] >= 100])
                st.metric("Tam Dolu Üniversite", tam_dolu_uni)
            with col_met5:
                toplam_bos_kont = uni_analiz['Bos_Kontenjan'].sum()
                st.metric("Toplam Boş Kontenjan", f"{toplam_bos_kont:,.0f}")
            
            # Detaylı tablo
            if st.checkbox("📋 Detaylı Üniversite Tablosu Göster"):
                display_df = uni_analiz.sort_values('Doluluk_Orani')[['Uni_Adi', 'Sehir', 'Bolge', 'Toplam_Kontenjan', 
                                                                    'Toplam_Yerlesen', 'Program_Sayisi', 'Doluluk_Orani', 
                                                                    'Bos_Kontenjan', 'Bos_Yuzde']].copy()
                display_df.columns = ['Üniversite Adı', 'Şehir', 'Bölge', 'Toplam Kontenjan', 'Toplam Yerleşen', 
                                    'Program Sayısı', '% Doluluk Oranı', 'Boş Kontenjan', '% Boş Yüzde']
                
                st.dataframe(
                    display_df,
                    column_config={
                        'Toplam Kontenjan': st.column_config.NumberColumn(format="%d"),
                        'Toplam Yerleşen': st.column_config.NumberColumn(format="%d"),
                        'Program Sayısı': st.column_config.NumberColumn(format="%d"),
                        '% Doluluk Oranı': st.column_config.NumberColumn(format="%.1f%%"),
                        'Boş Kontenjan': st.column_config.NumberColumn(format="%d"),
                        '% Boş Yüzde': st.column_config.NumberColumn(format="%.1f%%")
                    },
                    use_container_width=True
                )

with tab3:
    st.header("Fakülte/Yüksekokul Bazında Analiz")
    
    if 'Fakülte/Yüksekokul Adı' in devlet_df.columns:
        # Fakülte analizi
        fakulte_analiz = devlet_df.groupby('Fakülte/Yüksekokul Adı').agg({
            'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Program Adı': 'count'
        }).reset_index()
        
        fakulte_analiz['Doluluk_Orani'] = (fakulte_analiz['Yerleşen'] / fakulte_analiz['Kontenjan'] * 100)
        fakulte_analiz['Bos_Kontenjan'] = fakulte_analiz['Kontenjan'] - fakulte_analiz['Yerleşen']
        
        # En boş fakülteler
        st.subheader("En Boş Kalan Fakülte/Yüksekokullar (Devlet)")
        en_bos_fakulteler = fakulte_analiz.dropna(subset=['Fakülte/Yüksekokul Adı']).nsmallest(20, 'Doluluk_Orani')
        
        fig = px.bar(
            en_bos_fakulteler.head(10),
            y='Fakülte/Yüksekokul Adı',
            x='Doluluk_Orani',
            color='Program Adı',
            title="En Boş 10 Fakülte/Yüksekokul (Devlet Üniversiteleri)",
            orientation='h',
            labels={'Program Adı': 'Program Sayısı'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # En dolu fakülteler
        st.subheader("En Dolu Fakülte/Yüksekokullar (Devlet)")
        en_dolu_fakulteler = fakulte_analiz.dropna(subset=['Fakülte/Yüksekokul Adı']).nlargest(15, 'Doluluk_Orani')
        
        fig = px.bar(
            en_dolu_fakulteler,
            y='Fakülte/Yüksekokul Adı',
            x='Doluluk_Orani',
            title="En Dolu 15 Fakülte/Yüksekokul (Devlet Üniversiteleri)",
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Fakülte türlerine göre pasta grafiği
        st.subheader("Fakülte/Yüksekokul Türlerinin Dağılımı")
        
        try:
            # Fakülte türlerini çıkar
            fakulte_turleri = fakulte_analiz['Fakülte/Yüksekokul Adı'].str.extract(r'(Fakültesi|Yüksekokulu|Enstitüsü|Meslek Yüksekokulu)', expand=False)
            fakulte_sayilari = fakulte_turleri.fillna('Diğer').value_counts()
            
            if not fakulte_sayilari.empty:
                fig_pie = px.pie(
                    values=fakulte_sayilari.values,
                    names=fakulte_sayilari.index,
                    title="Devlet Üniversitelerinde Birim Türü Dağılımı"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Birim türü dağılımı hesaplanamadı.")
        except Exception as e:
            st.info("Birim türü analizi şu anda kullanılamıyor.")

with tab4:
    st.header(f"Detaylı İncelemeler {f'({secili_bolge} Bölgesi)' if secili_bolge != 'Tümü' else ''}")
    
    if devlet_df.empty:
        st.warning("Seçilen filtrelere uygun devlet üniversitesi verisi bulunamadı.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # Puan türü bazında analiz
            if 'Puan Türü' in devlet_df.columns:
                st.subheader("Puan Türüne Göre Devlet Üniversiteleri Durumu")
                
                puan_analiz = devlet_df.groupby('Puan Türü').agg({
                    'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                    'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                    'Program Adı': 'count'
                }).reset_index()
                
                puan_analiz['Doluluk_Orani'] = (puan_analiz['Yerleşen'] / puan_analiz['Kontenjan'] * 100)
                puan_analiz['Bos_Kontenjan'] = puan_analiz['Kontenjan'] - puan_analiz['Yerleşen']
                
                fig_puan = px.bar(
                    puan_analiz.sort_values('Doluluk_Orani'),
                    x='Puan Türü',
                    y='Doluluk_Orani',
                    color='Program Adı',
                    title="Puan Türüne Göre Devlet Üniversiteleri Doluluk Oranı",
                    labels={
                        'Program Adı': 'Program Sayısı', 
                        'Doluluk_Orani': '% Doluluk Oranı',
                        'Puan Türü': 'Puan Türü'
                    }
                )
                fig_puan.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                st.plotly_chart(fig_puan, use_container_width=True)
                st.caption("📚 Bu grafik puan türlerine göre devlet üniversitelerinin doluluk oranlarını gösterir. Y ekseni doluluk oranı, renk yoğunluğu ise o puan türündeki program sayısını temsil eder.")
                
                # Puan türü pasta grafiği
                fig_pie_puan = px.pie(
                    puan_analiz,
                    values='Program Adı',
                    names='Puan Türü',
                    title="Puan Türlerine Göre Program Dağılımı",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                )
                fig_pie_puan.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    textfont_size=11,
                    textfont_color="white",
                    textfont_family="Arial Black",
                    marker=dict(
                        line=dict(color='white', width=3)
                    ),
                    pull=[0.1 if val == puan_analiz['Program Adı'].max() else 0 for val in puan_analiz['Program Adı']],
                    hovertemplate='<b>Puan Türü:</b> %{label}<br><b>Program Sayısı:</b> %{value}<br><b>Toplam Yüzdesi:</b> %{percent}<br><extra></extra>'
                )
                fig_pie_puan.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=10),
                        title=dict(
                            text="<b>Puan Türleri</b>",
                            font=dict(size=11)
                        )
                    ),
                    font=dict(size=12),
                    title_font=dict(size=16, color='darkblue'),
                    margin=dict(l=20, r=120, t=50, b=20)
                )
                st.plotly_chart(fig_pie_puan, use_container_width=True)
                st.caption("🥧 Bu pasta grafiği devlet üniversitesi programlarının puan türlerine göre dağılımını gösterir. Her dilim bir puan türünü ve o türdeki program sayısının oranını temsil eder.")
        
        with col2:
            # Doluluk kategorileri analizi
            st.subheader("Devlet Üniversiteleri Doluluk Kategorileri")
            
            # Doluluk kategorilerini oluştur
            devlet_df_temp = devlet_df.copy()
            doluluk_kategorileri = pd.cut(
                devlet_df_temp['Doluluk_Orani'].dropna(),
                bins=[0, 50, 70, 85, 100, float('inf')],
                labels=['%0-50 Düşük', '%51-70 Orta', '%71-85 İyi', '%86-100 Yüksek', '%100+ Tam Dolu']
            )
            
            kategori_dagilim = doluluk_kategorileri.value_counts()
            
            if not kategori_dagilim.empty:
                fig_pie_kategori = px.pie(
                    values=kategori_dagilim.values,
                    names=kategori_dagilim.index,
                    title="Devlet Üniversitesi Programlarının Doluluk Kategorileri",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                )
                fig_pie_kategori.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    textfont_size=11,
                    textfont_color="white",
                    textfont_family="Arial Black",
                    marker=dict(
                        line=dict(color='white', width=3)
                    ),
                    pull=[0.1 if val == kategori_dagilim.max() else 0 for val in kategori_dagilim.values],
                    hovertemplate='<b>Kategori:</b> %{label}<br><b>Program Sayısı:</b> %{value}<br><b>Toplam Yüzdesi:</b> %{percent}<br><extra></extra>'
                )
                fig_pie_kategori.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=10),
                        title=dict(
                            text="<b>Doluluk Kategorileri</b>",
                            font=dict(size=11)
                        )
                    ),
                    font=dict(size=12),
                    title_font=dict(size=16, color='darkblue'),
                    margin=dict(l=20, r=120, t=50, b=20)
                )
                st.plotly_chart(fig_pie_kategori, use_container_width=True)
                st.caption("🎯 Bu pasta grafiği devlet üniversitesi programlarının doluluk kategorilerine göre dağılımını gösterir. Her dilim bir doluluk aralığını temsil eder (%0-50 Düşük, %51-70 Orta, vb.).")
            
            # Histogram - doluluk dağılımı
            fig_hist_doluluk = px.histogram(
                devlet_df_temp,
                x='Doluluk_Orani',
                nbins=25,
                title="Devlet Üniversitesi Programları Doluluk Dağılımı",
                labels={
                    'Doluluk_Orani': '% Doluluk Oranı', 
                    'count': 'Program Sayısı'
                },
                color_discrete_sequence=['#FF6B6B']
            )
            fig_hist_doluluk.update_xaxes(title="% Doluluk Oranı", ticksuffix="%")
            fig_hist_doluluk.add_vline(
                x=devlet_df_temp['Doluluk_Orani'].mean(), 
                line_dash="dash", 
                line_color="red", 
                annotation_text=f"Ortalama: {devlet_df_temp['Doluluk_Orani'].mean():.1f}%"
            )
            st.plotly_chart(fig_hist_doluluk, use_container_width=True)
            st.caption("📊 Bu histogram devlet üniversitesi programlarının doluluk oranı dağılımını gösterir. X ekseni doluluk yüzdesi, Y ekseni o yüzdeye sahip program sayısını gösterir. Kırmızı çizgi ortalama doluluk oranını işaret eder.")
        
        # En düşük puanlı boş bölümler
        st.subheader("En Düşük Puanlı Boş Devlet Bölümleri")
        
        # En Küçük Puan sütunu varsa analiz yap
        if 'En Küçük Puan' in devlet_df.columns:
            def safe_float_convert(x):
                try:
                    return float(str(x).replace(',', '.'))
                except:
                    return np.nan
            
            devlet_puan_analiz = devlet_df.copy()
            devlet_puan_analiz['En_Kucuk_Puan_Float'] = devlet_puan_analiz['En Küçük Puan'].apply(safe_float_convert)
            
            # Doluluk oranı düşük ve puan bilgisi olan bölümler
            dusuk_dolu_puanli = devlet_puan_analiz[
                (devlet_puan_analiz['Doluluk_Orani'] < 80) & 
                (devlet_puan_analiz['En_Kucuk_Puan_Float'].notna())
            ].nsmallest(20, 'En_Kucuk_Puan_Float')
            
            if not dusuk_dolu_puanli.empty:
                col_puan1, col_puan2 = st.columns(2)
                
                with col_puan1:
                    fig_scatter_puan = px.scatter(
                        dusuk_dolu_puanli,
                        x='En_Kucuk_Puan_Float',
                        y='Doluluk_Orani',
                        size='Bos_Kontenjan',
                        color='Bölge' if 'Bölge' in dusuk_dolu_puanli.columns else None,
                        hover_data=['Program Adı', 'Üniversite Adı', 'İl'],
                        title="Düşük Puanlı ve Boş Kalan Devlet Bölümleri",
                        labels={
                            'En_Kucuk_Puan_Float': 'En Küçük Puan', 
                            'Doluluk_Orani': '% Doluluk Oranı',
                            'Bos_Kontenjan': 'Boş Kontenjan',
                            'Bölge': 'Bölge',
                            'Program Adı': 'Program Adı',
                            'Üniversite Adı': 'Üniversite Adı',
                            'İl': 'Şehir'
                        }
                    )
                    fig_scatter_puan.update_yaxes(title="% Doluluk Oranı", ticksuffix="%")
                    st.plotly_chart(fig_scatter_puan, use_container_width=True)
                    st.caption("🎯 Bu scatter plot düşük puanlı ve boş kalan devlet bölümlerini analiz eder. X ekseni en küçük puan, Y ekseni doluluk oranı, nokta büyüklüğü boş kontenjan miktarını gösterir. Sol alttaki noktalar hem düşük puanlı hem de boş kalan bölümlerdir.")
                
                with col_puan2:
                    # En düşük puanlı programlar tablosu
                    st.write("**En Düşük Puanlı ve Boş Kalan 10 Program:**")
                    puan_tablo = dusuk_dolu_puanli.head(10)[['Program Adı', 'Üniversite Adı', 'İl', 
                                                           'En_Kucuk_Puan_Float', 'Doluluk_Orani', 'Bos_Kontenjan']].copy()
                    puan_tablo.columns = ['Program', 'Üniversite', 'Şehir', 'En Küçük Puan', '% Doluluk', 'Boş Kontenjan']
                    puan_tablo['% Doluluk'] = puan_tablo['% Doluluk'].round(1)
                    puan_tablo['En Küçük Puan'] = puan_tablo['En Küçük Puan'].round(2)
                    
                    st.dataframe(puan_tablo, use_container_width=True, height=400)
            else:
                st.info("Puan bilgisi olan düşük doluluk oranına sahip program bulunamadı.")
        
        # Genel özet istatistikler
        st.subheader("📈 Filtrelenmiş Veri Özet İstatistikleri")
        
        col_ozet1, col_ozet2, col_ozet3, col_ozet4, col_ozet5 = st.columns(5)
        
        with col_ozet1:
            total_programs = len(devlet_df)
            st.metric("Toplam Program", f"{total_programs:,}")
        
        with col_ozet2:
            unique_unis = devlet_df['Üniversite Adı'].nunique()
            st.metric("Üniversite Sayısı", unique_unis)
        
        with col_ozet3:
            unique_cities = devlet_df['İl'].nunique() if 'İl' in devlet_df.columns else 0
            st.metric("Şehir Sayısı", unique_cities)
        
        with col_ozet4:
            avg_occupancy = devlet_df['Doluluk_Orani'].mean()
            st.metric("Ortalama Doluluk", f"{avg_occupancy:.1f}%")
        
        with col_ozet5:
            total_empty = devlet_df['Bos_Kontenjan'].sum()
            st.metric("Toplam Boş Kontenjan", f"{total_empty:,.0f}")

st.markdown("---")
st.caption("📊 Bu analizler sadece devlet üniversiteleri için hazırlanmıştır.")

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
