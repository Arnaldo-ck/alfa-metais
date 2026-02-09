import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS Customizado para Máxima Visibilidade
st.markdown("""
    <style>
    /* Título Principal */
    .brand-title { font-size: 42px !important; font-weight: 800; color: #0D47A1; margin-bottom: 0px; padding-bottom: 0px; }
    .brand-subtitle { font-size: 16px; color: #666; margin-top: -10px; margin-bottom: 20px; }
    
    /* Estilização dos Cards */
    .metric-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05); 
        border: 1px solid #eee;
    }
    .metric-label { font-size: 18px !important; font-weight: 700; color: #555; text-transform: uppercase; margin-bottom: 8px; }
    .price-value { font-size: 48px !important; font-weight: 900; color: #0D47A1; line-height: 1; }
    .profit-value { font-size: 48px !important; font-weight: 900; color: #2E7D32; line-height: 1; }
    .sub-value { font-size: 20px; color: #666; font-weight: 500; margin-top: 5px; }
    
    /* Badges de Mercado */
    .market-badge {
        background-color: #f0f2f6;
        padding: 8px 15px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        display: inline-block;
        margin-right: 10px;
        border-left: 4px solid #0D47A1;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo na Barra Lateral
try:
    st.sidebar.image("Alfa.png", use_container_width=True)
except:
    st.sidebar.markdown("# 🛡️ ALFA METAIS")

# 4. Funções de Dados
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

# 5. Sidebar - Controles
st.sidebar.header("📋 Parâmetros da Venda")
cliente = st.sidebar.text_input("Cliente:", "Diretoria de Compras")
produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()))

st.sidebar.divider()
premio_base = metais_dict[produto_sel]["premio_padrao"]
premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_base), step=10.0)
pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5)

unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
volume_input = st.sidebar.number_input(f"Volume:", value=1.0 if unidade == "Toneladas" else 1000.0, step=0.1 if unidade == "Toneladas" else 50.0)

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

    # Grid de Indicadores de Mercado
    st.markdown(f"""
        <div style="margin-bottom: 25px;">
            <div class="market-badge">💵 Dólar: R$ {dolar_atual:.2f}</div>
            <div class="market-badge">🏛️ LME {produto_sel}: US$ {preco_lme:.2f}</div>
            <div class="market-badge">🏷️ Prêmio: US$ {premio_ajustado:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # 8. Grid de Resultados (Destaque Principal)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 8px solid #0D47A1;">
            <div class="metric-label">💰 Preço de Venda</div>
            <div class="price-value">R$ {preco_kg:.2f}<span style="font-size: 20px;">/kg</span></div>
            <div class="sub-value">Total: R$ {venda_total:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 8px solid #2E7D32;">
            <div class="metric-label">🟢 Sua Comissão ({pct_comissao}%)</div>
            <div class="profit-value">R$ {valor_comissao_total:,.2f}</div>
            <div class="sub-value">Ganhando R$ {comissao_por_kg:.3f} por kg</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("") # Espaçador
    
    # 9. Gráfico (Ocupando a largura total agora)
    st.subheader(f"📊 Histórico LME: {produto_sel}")
    fig = go.Figure(go.Bar(
        x=df_hist.index.strftime('%d/%m'),
        y=df_hist['Close'].round(2),
        text=df_hist['Close'].round(2),
        textposition='outside',
        marker_color='#0D47A1'
    ))
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # 10. WhatsApp
    st.divider()
    st.subheader("📱 Gerar Proposta WhatsApp")
    vol_display = f"{volume_input} Toneladas" if unidade == "Toneladas" else f"{volume_input} KG"
    
    msg_zap = f"""Olá, *{cliente}*! 👋

Abaixo, a cotação oficializada pela *ALFA METAIS* para sua análise:

📦 *MATERIAL:* {produto_sel.upper()}
💰 *VALOR:* R$ {preco_kg:.2f}/kg
⚖️ *VOLUME:* {vol_display}
------------------------------
💵 *TOTAL DO PEDIDO:* R$ {venda_total:,.2f}
------------------------------

🌐 *DADOS DE MERCADO*
📈 LME: US$ {preco_lme:.2f}
💵 Câmbio: R$ {dolar_atual:.2f}
🏷️ Prêmio: US$ {premio_ajustado:.2f}

⏳ *VALIDADE:* 24 Horas
⚠️ _Preço sujeito a variação conforme fechamento da LME._

Fico à disposição para fecharmos! 🤝"""

    st.code(msg_zap, language="text")

else:
    st.error("Erro ao sincronizar com o mercado financeiro.")



