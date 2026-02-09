import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS Customizado - Foco em Contraste e Legibilidade
st.markdown("""
    <style>
    /* 1. Título com borda fina branca (Text Stroke Effect) */
    .brand-title { 
        font-size: 42px !important; 
        font-weight: 800; 
        color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        margin-bottom: 0px; 
    }
    
    /* 2. Subtítulo maior */
    .brand-subtitle { 
        font-size: 20px !important; 
        color: #fff; 
        font-weight: 500;
        margin-top: 5px; 
        margin-bottom: 25px; 
    }
    
    /* 3. Ajuste das Caixas de Texto (Removendo fundos brancos e ajustando cores) */
    .metric-card { 
        background-color: transparent !important; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid rgba(255,255,255,0.2);
    }
    .metric-label { font-size: 22px !important; font-weight: 700; color: #fff !important; text-transform: uppercase; }
    .price-value { font-size: 52px !important; font-weight: 900; color: #fff !important; }
    .profit-value { font-size: 52px !important; font-weight: 900; color: #00E676 !important; } /* Verde vibrante para comissão */
    .sub-value { font-size: 22px !important; color: #ddd !important; font-weight: 500; }
    
    /* 4. Badges de Mercado maiores e sem fundo branco */
    .market-badge {
        background-color: rgba(255,255,255,0.1) !important;
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 20px !important;
        color: #fff !important;
        display: inline-block;
        margin-right: 15px;
        border: 1px solid rgba(255,255,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Dados e Sidebar (Mantendo a estrutura anterior)
try:
    st.sidebar.image("Alfa.png", use_container_width=True)
except:
    st.sidebar.markdown("# 🛡️ ALFA METAIS")

metais_dict = {
    "Alumínio P1020": {"ticker": "ALI=F", "premio_padrao": 350},
    "Cobre": {"ticker": "HG=F", "premio_padrao": 600},
    "Latão": {"ticker": "HG=F", "premio_padrao": 450}, 
    "Zamac 5": {"ticker": "ZN=F", "premio_padrao": 500}
}

@st.cache_data(ttl=3600)
def carregar_dados_metal(ticker):
    try:
        data = yf.Ticker(ticker).history(period="15d")
        dolar_info = yf.Ticker("USDBRL=X").history(period="1d")
        dolar = dolar_info['Close'].iloc[-1]
        return data, dolar
    except:
        return pd.DataFrame(), 5.20

# Sidebar - Controles
st.sidebar.header("📋 Parâmetros")
cliente = st.sidebar.text_input("Cliente:", "Diretoria de Compras")
produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()))
premio_base = metais_dict[produto_sel]["premio_padrao"]
premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_base), step=10.0)
pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5)
unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
volume_input = st.sidebar.number_input(f"Volume:", value=1.0 if unidade == "Toneladas" else 1000.0)
ton_calculo = volume_input if unidade == "Toneladas" else volume_input / 1000

# 6. Cálculos
df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])

if not df_hist.empty:
    preco_lme = df_hist['Close'].iloc[-1]
    preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
    venda_total = preco_kg * (ton_calculo * 1000)
    valor_comissao_total = venda_total * (pct_comissao / 100)
    comissao_por_kg = preco_kg * (pct_comissao / 100)

    # 7. Cabeçalho Principal
    st.markdown('<p class="brand-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Terminal de Inteligência Comercial | alfametaisrepresentacoes.com.br</p>', unsafe_allow_html=True)

    # Grid de Indicadores de Mercado (Fontes Aumentadas conforme solicitado)
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div class="market-badge">💵 Dólar: R$ {dolar_atual:.2f}</div>
            <div class="market-badge">🏛️ LME {produto_sel}: US$ {preco_lme:.2f}</div>
            <div class="market-badge">🏷️ Prêmio: US$ {premio_ajustado:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # 8. Grid de Resultados (Removido fundo branco, texto em destaque)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Preço de Venda</div>
            <div class="price-value">R$ {preco_kg:.2f}<span style="font-size: 24px;">/kg</span></div>
            <div class="sub-value">Total: R$ {venda_total:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟢 Sua Comissão ({pct_comissao}%)</div>
            <div class="profit-value">R$ {valor_comissao_total:,.2f}</div>
            <div class="sub-value">Ganho: R$ {comissao_por_kg:.3f} /kg</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("") 
    st.subheader(f"📊 Histórico LME: {produto_sel}")
    fig = go.Figure(go.Bar(
        x=df_hist.index.strftime('%d/%m'),
        y=df_hist['Close'].round(2),
        text=df_hist['Close'].round(2),
        textposition='outside',
        marker_color='#fff' # Gráfico em branco para contrastar com o fundo escuro
    ))
    fig.update_layout(
        height=300, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        margin=dict(l=0,r=0,t=30,b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 10. WhatsApp
    st.divider()
    vol_display = f"{volume_input} Toneladas" if unidade == "Toneladas" else f"{volume_input} KG"
    msg_zap = f"""Olá, *{cliente}*! 👋...""" # Mantendo lógica da mensagem
    st.code(msg_zap, language="text")

else:
    st.error("Erro ao sincronizar.")



