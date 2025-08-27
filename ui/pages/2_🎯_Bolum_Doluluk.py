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

# CSS hover efektleri ekle
st.markdown("""
<style>
div[data-testid="stSelectbox"] > div > div {
    cursor: pointer;
}
div[data-testid="stNumberInput"] > div > div {
    cursor: pointer;
}
.stSelectbox:hover {
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.title("🎯 Bölüm Doluluk Analizleri")

@st.cache_data
def get_data():
    return load_processed()

df = get_data()

# Doluluk oranını hesaplayan fonksiyon
def calculate_occupancy(row):
    try:
        kontenjan = pd.to_numeric(row['Kontenjan'], errors='coerce')
        yerlesen = pd.to_numeric(row['Yerleşen'], errors='coerce')
        if pd.isna(kontenjan) or pd.isna(yerlesen) or kontenjan <= 0:
            return np.nan
        return (yerlesen / kontenjan) * 100
    except:
        return np.nan

# Doluluk oranı hesapla
df['Doluluk_Orani'] = df.apply(calculate_occupancy, axis=1)
df['Bos_Kontenjan'] = pd.to_numeric(df['Kontenjan'], errors='coerce') - pd.to_numeric(df['Yerleşen'], errors='coerce')

# Bölüm bazlı birleştirilmiş veri oluştur
def create_department_analysis(data_df):
    """Aynı bölüm adındaki tüm programları birleştirip analiz oluştur"""
    bolum_analiz = data_df.groupby('Program Adı', as_index=False).agg({
        'Kontenjan': lambda x: pd.to_numeric(x, errors='coerce').sum(),
        'Yerleşen': lambda x: pd.to_numeric(x, errors='coerce').sum(),
        'Üniversite Adı': ['count', 'nunique'],  # Program sayısı ve Üniversite sayısı
        'İl': 'nunique',  # Farklı şehir sayısı
        'Üniversite Türü': lambda x: list(x.unique()),  # Üniversite türleri
        'Bölge': lambda x: list(x.dropna().unique()) if x.dropna().any() else ['Bilinmiyor']  # Bölgeler
    })
    
    # Çoklu level sütunları düzelt
    bolum_analiz.columns = ['Program_Adi', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 
                           'Program_Sayisi', 'Uni_Sayisi', 'Sehir_Sayisi', 
                           'Uni_Turleri', 'Bolgeler']
    
    # İstatistikleri hesapla
    bolum_analiz['Doluluk_Orani'] = (bolum_analiz['Toplam_Yerlesen'] / bolum_analiz['Toplam_Kontenjan'] * 100).round(2)
    bolum_analiz['Bos_Kontenjan'] = bolum_analiz['Toplam_Kontenjan'] - bolum_analiz['Toplam_Yerlesen']
    bolum_analiz['Bos_Yuzde'] = ((bolum_analiz['Bos_Kontenjan'] / bolum_analiz['Toplam_Kontenjan']) * 100).round(2)
    
    # Üniversite türü kategorisi (çoğunluk)
    bolum_analiz['Ana_Uni_Turu'] = bolum_analiz['Uni_Turleri'].apply(
        lambda x: max(set(x), key=x.count) if x else 'Bilinmiyor'
    )
    
    return bolum_analiz

# Bölüm bazlı analizi oluştur
department_df = create_department_analysis(df)

# Filtre seçenekleri - Bölüm bazlı filtreler
st.sidebar.header("🔍 Bölüm Bazlı Filtreler")

# Üniversite türü filtresi (çoğunluk türü)
uni_turleri = ['Tümü'] + sorted(department_df['Ana_Uni_Turu'].dropna().unique().tolist())
secili_uni_turu = st.sidebar.selectbox("Ağırlıklı Üniversite Türü", uni_turleri)
if secili_uni_turu != 'Tümü':
    department_df = department_df[department_df['Ana_Uni_Turu'] == secili_uni_turu]

# Kontenjan aralığı filtresi (toplam kontenjan)
min_kontenjan = st.sidebar.number_input("Minimum Toplam Kontenjan", min_value=0, value=0, step=100)
department_df = department_df[department_df['Toplam_Kontenjan'] >= min_kontenjan]

# Üniversite sayısı filtresi
min_uni_sayisi = st.sidebar.number_input("Minimum Üniversite Sayısı", min_value=1, value=1, step=1)
st.sidebar.caption("💡 Bu filtre bölümün kaç üniversitede açıldığını belirler. Örnek: Min=5 → En az 5 üniversitede açılan yaygın bölümler")
department_df = department_df[department_df['Uni_Sayisi'] >= min_uni_sayisi]

st.markdown("---")

# Ana analizler
tab1, tab2, tab3, tab4 = st.tabs(["🔴 En Boş Bölümler", "📊 Doluluk Dağılımı", "🏢 Kontenjan Büyüklüğü", "🎯 Tam Doluluk Analizi"])

with tab1:
    st.header("En Boş Kalan Bölümler (Türkiye Geneli)")
    
    # Sıralama kriterleri
    col1, col2 = st.columns(2)
    with col1:
        siralama_kriteri = st.selectbox(
            "Sıralama Kriteri",
            ["Boş Kontenjan Sayısına Göre", "Boş Yüzdesine Göre", "Toplam Kontenjan Sayısına Göre"]
        )
    
    with col2:
        gosterim_sayisi = st.selectbox("Gösterilecek Bölüm Sayısı", [10, 15, 20, 30], index=1)
    
    # Sıralama yap
    if not department_df.empty:
        if siralama_kriteri == "Boş Kontenjan Sayısına Göre":
            sorted_df = department_df.nlargest(gosterim_sayisi, 'Bos_Kontenjan')
            x_col, x_title = 'Bos_Kontenjan', 'Boş Kontenjan Sayısı'
            color_col, color_title = 'Doluluk_Orani', '% Doluluk Oranı'
        elif siralama_kriteri == "Boş Yüzdesine Göre":
            sorted_df = department_df.nlargest(gosterim_sayisi, 'Bos_Yuzde')
            x_col, x_title = 'Bos_Yuzde', '% Boş Yüzde'
            color_col, color_title = 'Toplam_Kontenjan', 'Toplam Kontenjan'
        else:  # Toplam Kontenjan Sayısına Göre
            sorted_df = department_df.nlargest(gosterim_sayisi, 'Toplam_Kontenjan')
            x_col, x_title = 'Toplam_Kontenjan', 'Toplam Kontenjan'
            color_col, color_title = 'Doluluk_Orani', '% Doluluk Oranı'
        
        if not sorted_df.empty:
            # Ana grafik
            st.subheader(f"🎯 En Boş {len(sorted_df)} Bölüm - {siralama_kriteri}")
            
            # Program adlarını kısalt
            display_df = sorted_df.copy()
            display_df['Program_Kisa'] = display_df['Program_Adi'].apply(
                lambda x: x[:50] + "..." if len(str(x)) > 50 else str(x)
            )
            
            # Ana bar chart
            fig = px.bar(
                display_df,
                y='Program_Kisa',
                x=x_col,
                color=color_col,
                hover_data={
                    'Program_Adi': True,
                    'Toplam_Kontenjan': ':,',
                    'Toplam_Yerlesen': ':,',
                    'Program_Sayisi': True,
                    'Uni_Sayisi': True,
                    'Sehir_Sayisi': True,
                    'Doluluk_Orani': ':.1f',
                    'Bos_Kontenjan': ':,',
                    'Bos_Yuzde': ':.1f',
                    'Ana_Uni_Turu': True
                },
                title=f"Türkiye Geneli En Boş {len(sorted_df)} Bölüm",
                orientation='h',
                labels={x_col: x_title, 'Program_Kisa': 'Bölüm Adı'},
                color_continuous_scale="Reds"
            )
            
            fig.update_layout(
                height=max(500, len(sorted_df) * 30),
                yaxis=dict(title="Bölüm Adı"),
                xaxis=dict(title=x_title),
                coloraxis_colorbar=dict(title=color_title)
            )
            # Y ekseni için yüzde formatı (doluluk oranı içeren grafiklerde)
            if 'Doluluk' in color_title:
                fig.update_layout(coloraxis_colorbar=dict(title=color_title, ticksuffix="%"))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Özet istatistikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Toplam Bölüm Türü", len(department_df))
            with col2:
                ortalama_doluluk = department_df['Doluluk_Orani'].mean()
                st.metric("Ortalama Doluluk", f"{ortalama_doluluk:.1f}%")
            with col3:
                toplam_bos = department_df['Bos_Kontenjan'].sum()
                st.metric("Toplam Boş Kontenjan", f"{toplam_bos:,.0f}")
            with col4:
                en_bos_oran = sorted_df.iloc[0]['Doluluk_Orani'] if len(sorted_df) > 0 else 0
                st.metric("En Boş Bölüm Doluluk", f"{en_bos_oran:.1f}%")
            
            # Detaylı tablo
            st.subheader("📋 Detaylı Bölüm İstatistikleri")
            
            # Tabloyu düzenle
            table_df = sorted_df[['Program_Adi', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 
                                'Program_Sayisi', 'Uni_Sayisi', 'Sehir_Sayisi', 
                                'Doluluk_Orani', 'Bos_Kontenjan', 'Bos_Yuzde']].copy()
            
            table_df.columns = ['Bölüm Adı', 'Toplam Kontenjan', 'Toplam Yerleşen', 
                              'Program Sayısı', 'Üniversite Sayısı', 'Şehir Sayısı',
                              '% Doluluk Oranı', 'Boş Kontenjan', '% Boş Yüzde']
            
            # Index'i 1'den başlat
            table_df.index = range(1, len(table_df) + 1)
            
            st.dataframe(
                table_df,
                use_container_width=True,
                column_config={
                    'Toplam Kontenjan': st.column_config.NumberColumn(format="%d"),
                    'Toplam Yerleşen': st.column_config.NumberColumn(format="%d"),
                    'Program Sayısı': st.column_config.NumberColumn(format="%d"),
                    'Üniversite Sayısı': st.column_config.NumberColumn(format="%d"),
                    'Şehir Sayısı': st.column_config.NumberColumn(format="%d"),
                    '% Doluluk Oranı': st.column_config.NumberColumn(format="%.1f%%"),
                    'Boş Kontenjan': st.column_config.NumberColumn(format="%d"),
                    '% Boş Yüzde': st.column_config.NumberColumn(format="%.1f%%")
                }
            )
            
        else:
            st.warning("Seçilen filtrelere uygun bölüm bulunamadı.")
    else:
        st.warning("Analiz edilecek bölüm verisi bulunamadı.")

with tab2:
    st.header("Bölüm Bazlı Doluluk Dağılımı")
    
    if not department_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Doluluk oranı histogramı
            st.subheader("Doluluk Oranı Dağılımı")
            fig_hist = px.histogram(
                department_df,
                x='Doluluk_Orani',
                nbins=25,
                title="Bölümlerin Doluluk Oranı Dağılımı",
                labels={'Doluluk_Orani': '% Doluluk Oranı', 'count': 'Bölüm Sayısı'},
                color_discrete_sequence=['#FF6B6B'],
                hover_data={
                    'Program_Adi': True,
                    'Toplam_Kontenjan': True,
                    'Toplam_Yerlesen': True,
                    'Uni_Sayisi': True
                }
            )
            fig_hist.update_traces(
                hovertemplate='<b>%Doluluk Aralığı:</b> %{x:.1f}<br>' +
                             '<b>Bu Aralıktaki Bölüm Sayısı:</b> %{y}<br>' +
                             '<extra></extra>'
            )
            fig_hist.add_vline(x=department_df['Doluluk_Orani'].mean(), 
                             line_dash="dash", line_color="red", 
                             annotation_text=f"Ortalama: {department_df['Doluluk_Orani'].mean():.1f}%")
            # X ekseni için yüzde formatı
            fig_hist.update_xaxes(title="% Doluluk Oranı", ticksuffix="%")
            st.plotly_chart(fig_hist, use_container_width=True)
            st.caption("📊 Bu grafik bölümlerin doluluk oranlarının dağılımını gösterir. X ekseni doluluk yüzdesi, Y ekseni o yüzdeye sahip bölüm sayısını gösterir. Kırmızı çizgi ortalama doluluk oranını işaret eder.")
            
            # Detaylı liste - Histogram altına ekleme
            if st.checkbox("📋 Detaylı Bölüm Listesi Göster"):
                secilen_aralik = st.selectbox(
                    "Doluluk Aralığı Seç:",
                    ["%0-10 Doluluk", "%10-20 Doluluk", "%20-30 Doluluk", "%30-40 Doluluk", "%40-50 Doluluk", "%50-60 Doluluk", 
                     "%60-70 Doluluk", "%70-80 Doluluk", "%80-90 Doluluk", "%90-100 Doluluk", "%100+ Doluluk"]
                )
                
                # Aralık filtresi uygula
                aralik_map = {
                    "%0-10 Doluluk": (0, 10), "%10-20 Doluluk": (10, 20), "%20-30 Doluluk": (20, 30),
                    "%30-40 Doluluk": (30, 40), "%40-50 Doluluk": (40, 50), "%50-60 Doluluk": (50, 60),
                    "%60-70 Doluluk": (60, 70), "%70-80 Doluluk": (70, 80), "%80-90 Doluluk": (80, 90),
                    "%90-100 Doluluk": (90, 100), "%100+ Doluluk": (100, float('inf'))
                }
                
                min_val, max_val = aralik_map[secilen_aralik]
                filtered_df = department_df[
                    (department_df['Doluluk_Orani'] >= min_val) & 
                    (department_df['Doluluk_Orani'] < max_val)
                ]
                
                if not filtered_df.empty:
                    st.write(f"**{secilen_aralik} Doluluk Aralığındaki {len(filtered_df)} Bölüm:**")
                    display_df = filtered_df[['Program_Adi', 'Doluluk_Orani', 'Toplam_Kontenjan', 'Uni_Sayisi']].copy()
                    display_df.columns = ['Bölüm Adı', '% Doluluk', 'Toplam Kontenjan', 'Üniversite Sayısı']
                    display_df = display_df.sort_values('% Doluluk')
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info(f"{secilen_aralik} aralığında bölüm bulunamadı.")
            
            # Doluluk kategorileri pasta grafiği
            st.subheader("Doluluk Kategorileri")
            doluluk_kategorileri = pd.cut(
                department_df['Doluluk_Orani'],
                bins=[0, 25, 50, 75, 90, 100, float('inf')],
                labels=['%0-25 Doluluk', '%26-50 Doluluk', '%51-75 Doluluk', '%76-90 Doluluk', '%91-100 Doluluk', '%100+ Doluluk']
            )
            kategori_dagilim = doluluk_kategorileri.value_counts()
            
            fig_pie = px.pie(
                values=kategori_dagilim.values,
                names=kategori_dagilim.index,
                title="Bölümlerin Doluluk Kategorileri",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            )
            fig_pie.update_traces(
                textposition='inside', 
                textinfo='label',  # Sadece kategori adı göster
                textfont_size=11,
                textfont_color="white",
                textfont_family="Arial Black",
                marker=dict(
                    line=dict(color='white', width=3)
                ),
                pull=[0.1 if val == kategori_dagilim.max() else 0 for val in kategori_dagilim.values],  # En büyük dilimi çek
                hovertemplate='<b>Kategori:</b> %{label}<br><b>Bölüm Sayısı:</b> %{value}<br><b>Toplam Yüzdesi:</b> %{percent}<br><extra></extra>'
            )
            fig_pie.update_layout(
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
                title_font=dict(size=16, color='white'),
                margin=dict(l=20, r=120, t=50, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.caption("🍰 Bu pasta grafiği bölümlerin doluluk oranlarına göre kategorik dağılımını gösterir. Her dilim bir doluluk aralığını temsil eder ve bu aralıktaki bölüm sayısını gösterir. En büyük kategori öne çıkarılmıştır.")
        
        with col2:
            # Kontenjan büyüklüğü vs Doluluk scatter
            st.subheader("Kontenjan vs Doluluk İlişkisi")
            fig_scatter = px.scatter(
                department_df,
                x='Toplam_Kontenjan',
                y='Doluluk_Orani',
                size='Uni_Sayisi',
                color='Ana_Uni_Turu',
                hover_data={
                    'Program_Adi': True,
                    'Toplam_Kontenjan': ':,',
                    'Toplam_Yerlesen': ':,',
                    'Program_Sayisi': True,
                    'Uni_Sayisi': True,
                    'Sehir_Sayisi': True
                },
                title="Bölümlerin Kontenjan-Doluluk İlişkisi",
                labels={
                    'Toplam_Kontenjan': 'Toplam Kontenjan', 
                    'Doluluk_Orani': '% Doluluk Oranı',
                    'Program_Adi': 'Bölüm Adı',
                    'Toplam_Yerlesen': 'Toplam Yerleşen',
                    'Program_Sayisi': 'Program Sayısı',
                    'Uni_Sayisi': 'Üniversite Sayısı',
                    'Sehir_Sayisi': 'Şehir Sayısı',
                    'Ana_Uni_Turu': 'Üniversite Türü'
                }
            )
            # X ekseni ayarları - 100'lü aralıklar, 1000+ gösterim
            max_kontenjan = department_df['Toplam_Kontenjan'].max()
            fig_scatter.update_xaxes(
                dtick=100,  # 100'lü aralıklar
                range=[0, min(1000, max_kontenjan * 1.1)],  # 1000'e kadar göster
                tickformat='d',  # Tam sayı formatı
                tickvals=list(range(0, 1001, 100)) + ([1000] if max_kontenjan > 1000 else []),
                ticktext=[str(x) for x in range(0, 1000, 100)] + (['1000+'] if max_kontenjan > 1000 else [])
            )
            # Y ekseni ayarları - yüzde formatı
            fig_scatter.update_yaxes(
                title="% Doluluk Oranı",
                ticksuffix="%"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("🎯 Bu grafik kontenjan büyüklüğü ile doluluk oranı arasındaki ilişkiyi gösterir. Her nokta bir bölümü temsil eder. Nokta büyüklüğü üniversite sayısını, renk ise üniversite türünü gösterir.")
            
            # Boş kontenjan dağılımı
            st.subheader("En Çok Boş Kontenjan")
            en_bos_kontenjanlı = department_df.nlargest(10, 'Bos_Kontenjan')
            
            fig_bar = px.bar(
                en_bos_kontenjanlı,
                x='Bos_Kontenjan',
                y='Program_Adi',
                orientation='h',
                title="En Çok Boş Kontenjanı Olan 10 Bölüm",
                labels={'Bos_Kontenjan': 'Boş Kontenjan Sayısı', 'Program_Adi': 'Bölüm Adı'},
                color='Bos_Kontenjan',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Özet istatistikler
        st.subheader("📊 Genel İstatistikler")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Toplam Bölüm Türü", len(department_df))
        with col2:
            ortalama_doluluk = department_df['Doluluk_Orani'].mean()
            st.metric("Ortalama Doluluk", f"{ortalama_doluluk:.1f}%")
        with col3:
            bos_bolum_sayisi = len(department_df[department_df['Doluluk_Orani'] < 50])
            st.metric("<%50 Dolu Bölüm", bos_bolum_sayisi)
        with col4:
            tam_dolu = len(department_df[department_df['Doluluk_Orani'] >= 100])
            st.metric("Tam Dolu Bölüm", tam_dolu)
        with col5:
            toplam_bos_kontenjan = department_df['Bos_Kontenjan'].sum()
            st.metric("Toplam Boş Kontenjan", f"{toplam_bos_kontenjan:,.0f}")
    
    else:
        st.warning("Analiz edilecek bölüm verisi bulunamadı.")

with tab3:
    st.header("Bölüm Bazlı Kontenjan Büyüklüğü Analizi")
    
    if not department_df.empty:
        # Büyük kontenjan filtreleme
        kategori_secim = st.selectbox(
            "Kontenjan Kategorisi Seç",
            ["500+ Kontenjan", "1000+ Kontenjan", "100+ Kontenjan", "50+ Kontenjan"]
        )
        
        min_vals = {"500+ Kontenjan": 500, "1000+ Kontenjan": 1000, "100+ Kontenjan": 100, "50+ Kontenjan": 50}
        min_kont = min_vals[kategori_secim]
        
        buyuk_bolumler = department_df[department_df['Toplam_Kontenjan'] >= min_kont]
        
        if not buyuk_bolumler.empty:
            st.subheader(f"{kategori_secim} Olan Bölümler ({len(buyuk_bolumler)} adet)")
            
            # En boş büyük kontenjanlı bölümler
            bos_buyuk = buyuk_bolumler.nsmallest(15, 'Doluluk_Orani')
            
            if not bos_buyuk.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Scatter plot
                    fig_scatter = px.scatter(
                        bos_buyuk,
                        x='Toplam_Kontenjan',
                        y='Doluluk_Orani',
                        size='Bos_Kontenjan',
                        color='Ana_Uni_Turu',
                        hover_data={
                            'Program_Adi': True,
                            'Toplam_Kontenjan': ':,',
                            'Toplam_Yerlesen': ':,',
                            'Uni_Sayisi': True
                        },
                        title=f"{kategori_secim} Olan En Boş 15 Bölüm",
                        labels={'Toplam_Kontenjan': 'Toplam Kontenjan', 'Doluluk_Orani': '% Doluluk Oranı'}
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                with col2:
                    # Bar chart
                    fig_bar = px.bar(
                        bos_buyuk.head(10),
                        x='Bos_Kontenjan',
                        y='Program_Adi',
                        orientation='h',
                        title=f"En Çok Boş Kontenjanı Olan 10 Bölüm",
                        labels={'Bos_Kontenjan': 'Boş Kontenjan', 'Program_Adi': 'Bölüm Adı'},
                        color='Doluluk_Orani',
                        color_continuous_scale='RdYlBu_r'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Tablo gösterimi
                st.subheader(f"{kategori_secim} En Boş Bölümler Detayı")
                display_df = bos_buyuk[['Program_Adi', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 
                                      'Doluluk_Orani', 'Bos_Kontenjan', 'Uni_Sayisi']].copy()
                display_df.columns = ['Bölüm Adı', 'Toplam Kontenjan', 'Toplam Yerleşen', 
                                    '% Doluluk Oranı', 'Boş Kontenjan', 'Üniversite Sayısı']
                display_df['% Doluluk Oranı'] = display_df['% Doluluk Oranı'].round(1)
                st.dataframe(display_df, use_container_width=True)
        else:
            st.warning(f"{kategori_secim} olan bölüm bulunamadı.")
    
    else:
        st.warning("Analiz edilecek bölüm verisi bulunamadı.")

with tab4:
    st.header("Bölüm Bazlı Tam Doluluk ve Aşım Analizleri")
    
    if not department_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Tam dolu ve üzeri bölümler
            tam_dolu_bolumler = department_df[department_df['Doluluk_Orani'] >= 100]
            asim_var_bolumler = department_df[department_df['Doluluk_Orani'] > 100]
            
            st.subheader(f"Tam Dolu Bölümler (100%+) - {len(tam_dolu_bolumler)} adet")
            
            if not tam_dolu_bolumler.empty:
                # Üniversite türüne göre dağılım
                tam_dolu_dagilim = tam_dolu_bolumler['Ana_Uni_Turu'].value_counts()
                fig_pie = px.pie(
                    values=tam_dolu_dagilim.values,
                    names=tam_dolu_dagilim.index,
                    title="Tam Dolu Bölümlerde Üniversite Türü Dağılımı",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # En yüksek doluluk oranına sahip bölümler
                en_dolu = tam_dolu_bolumler.nlargest(10, 'Doluluk_Orani')
                
                fig_bar = px.bar(
                    en_dolu,
                    x='Program_Adi',
                    y='Doluluk_Orani',
                    title="En Yüksek Doluluk Oranına Sahip 10 Bölüm",
                    labels={'Doluluk_Orani': '% Doluluk Oranı', 'Program_Adi': 'Bölüm Adı'},
                    color='Doluluk_Orani',
                    color_continuous_scale='Reds'
                )
                fig_bar.update_layout(
                    xaxis_tickangle=-45,
                    yaxis=dict(title="% Doluluk Oranı", ticksuffix="%"),
                    coloraxis_colorbar=dict(title="% Doluluk Oranı", ticksuffix="%")
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            else:
                st.info("Tam dolu bölüm bulunamadı.")
        
        with col2:
            st.subheader(f"Aşım Olan Bölümler (>100%) - {len(asim_var_bolumler)} adet")
            
            if not asim_var_bolumler.empty:
                # Aşım miktarı dağılımı
                asim_var_bolumler_copy = asim_var_bolumler.copy()
                asim_var_bolumler_copy['Asim_Miktari'] = asim_var_bolumler_copy['Doluluk_Orani'] - 100
                
                fig_hist = px.histogram(
                    asim_var_bolumler_copy,
                    x='Asim_Miktari',
                    nbins=20,
                    title="Aşım Miktarı Dağılımı",
                    labels={'Asim_Miktari': 'Aşım Miktarı (%)', 'count': 'Bölüm Sayısı'},
                    color_discrete_sequence=['#FF4444']
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # En çok aşım olan bölümler
                en_asimli = asim_var_bolumler_copy.nlargest(10, 'Asim_Miktari')
                
                fig_bar_h = px.bar(
                    en_asimli,
                    x='Asim_Miktari',
                    y='Program_Adi',
                    orientation='h',
                    title="En Fazla Aşımı Olan 10 Bölüm",
                    labels={'Asim_Miktari': 'Aşım Miktarı (%)', 'Program_Adi': 'Bölüm Adı'},
                    color='Asim_Miktari',
                    color_continuous_scale='OrRd'
                )
                st.plotly_chart(fig_bar_h, use_container_width=True)
            
            else:
                st.info("Aşım olan bölüm bulunamadı.")
        
        # Karşılaştırmalı analiz
        st.subheader("📈 Doluluk Durumu Özeti")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            bos_bolumler = len(department_df[department_df['Doluluk_Orani'] < 50])
            st.metric("<%50 Dolu", bos_bolumler)
        
        with col2:
            yarim_dolu = len(department_df[(department_df['Doluluk_Orani'] >= 50) & (department_df['Doluluk_Orani'] < 100)])
            st.metric("50-99% Dolu", yarim_dolu)
        
        with col3:
            tam_dolu_sayi = len(tam_dolu_bolumler)
            st.metric("100%+ Dolu", tam_dolu_sayi)
        
        with col4:
            asim_sayi = len(asim_var_bolumler)
            st.metric(">100% Aşım", asim_sayi)
        
        with col5:
            ortalama_doluluk = department_df['Doluluk_Orani'].mean()
            st.metric("Ortalama Doluluk", f"{ortalama_doluluk:.1f}%")
        
        # Aşım detay tablosu
        if not asim_var_bolumler.empty:
            st.subheader("🔥 Aşım Olan Bölümler Detayı")
            asim_detay = asim_var_bolumler.copy()
            asim_detay['Asim_Miktari'] = asim_detay['Doluluk_Orani'] - 100
            
            display_df = asim_detay.nlargest(20, 'Asim_Miktari')[['Program_Adi', 'Toplam_Kontenjan', 'Toplam_Yerlesen', 
                                                                'Doluluk_Orani', 'Uni_Sayisi', 'Ana_Uni_Turu', 'Asim_Miktari']].copy()
            display_df.columns = ['Bölüm Adı', 'Toplam Kontenjan', 'Toplam Yerleşen', 
                                '% Doluluk Oranı', 'Üniversite Sayısı', 'Ana Üniversite Türü', '% Aşım']
            
            for col in ['% Doluluk Oranı', '% Aşım']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(1)
            
            st.dataframe(display_df, use_container_width=True)
    
    else:
        st.warning("Analiz edilecek bölüm verisi bulunamadı.")
st.markdown("---")
st.caption("💡 Bu analizler bölüm bazlı toplu veriler üzerinden hesaplanmıştır. Filtreleri kullanarak daha spesifik analizler yapabilirsiniz.")

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
