import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS - Layout de Alta Performance
st.markdown("""
    <style>
    .brand-title { 
        font-size: 42px !important; 
        font-weight: 800; 
        color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        margin-bottom: 0px; 
    }
    .brand-subtitle { 
        font-size: 20px !important; 
        color: #fff; 
        font-weight: 500;
        margin-top: 5px; 
        margin-bottom: 25px; 
    }
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-bottom: 5px solid #0D47A1;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 20px !important; font-weight: 700; color: #fff !important; text-transform: uppercase; margin-bottom: 10px; }
    .price-value { font-size: 50px !important; font-weight: 900; color: #fff !important; line-height: 1; }
    .profit-value { font-size: 50px !important; font-weight: 900; color: #00E676 !important; line-height: 1; }
    .sub-value { font-size: 22px !important; color: #ccc !important; font-weight: 600; margin-top: 8px; }
    .market-badge {
        background-color: rgba(255,255,255,0.1);
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 22px !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.2);
        display: inline-block;
        margin-right: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo e Dados
try:
    st.sidebar.image("Alfa.png", use_container_width=True) # Nome do arquivo atualizado
except:
    st.sidebar.markdown("# 🛡️ ALFA METAIS")

metais_dict = {
    "Alumínio P1020": {"ticker": "ALI=F", "premio_padrao": 350.0},
    "Cobre": {"ticker": "HG=F", "premio_padrao": 600.0},
    "Latão": {"ticker": "HG=F", "premio_padrao": 450.0}, 
    "Zamac 5": {"ticker": "ZN=F", "premio_padrao": 500.0}
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

# 4. Lógica do Botão Limpar (Reset de Estado)
if 'reset' not in st.session_state:
    st.session_state.reset = False

def limpar_campos():
    st.session_state.cliente_input = "Diretoria de Compras"
    st.session_state.volume_input = 1.0
    st.session_state.premio_input = None # Força o padrão do dicionário
    st.session_state.comissao_input = 3.0

# 5. Barra Lateral
st.sidebar.header("📋 Parâmetros")
if st.sidebar.button("🧹 LIMPAR TUDO", on_click=limpar_campos):
    st.sidebar.success("Campos resetados!")

cliente = st.sidebar.text_input("Cliente:", key="cliente_input", value="Diretoria de Compras")
produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()))

# Ajuste automático do prêmio baseado no metal
premio_padrao = metais_dict[produto_sel]["premio_padrao"]
premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_padrao), step=10.0, key="premio_input_val" if not st.session_state.reset else None)

pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5, key="comissao_input")
unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
vol_val = 1.0 if unidade == "Toneladas" else 1000.0
volume_input = st.sidebar.number_input(f"Volume:", value=vol_val, key="volume_input")

ton_calculo = volume_input if unidade == "Toneladas" else volume_input / 1000

# 6. Cálculos e Exibição
df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])

if not df_hist.empty:
    preco_lme = df_hist['Close'].iloc[-1]
    preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
    venda_total = preco_kg * (ton_calculo * 1000)
    valor_comissao_total = venda_total * (pct_comissao / 100)
    comissao_por_kg = preco_kg * (pct_comissao / 100)

    st.markdown('<p class="brand-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Terminal de Inteligência Comercial | alfametaisrepresentacoes.com.br</p>', unsafe_allow_html=True)

    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div class="market-badge">💵 Dólar: R$ {dolar_atual:.2f}</div>
            <div class="market-badge">🏛️ LME {produto_sel}: US$ {preco_lme:.2f}</div>
            <div class="market-badge">🏷️ Prêmio: US$ {premio_ajustado:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">💰 Preço de Venda</div>
            <div class="price-value">R$ {preco_kg:.2f}<span style="font-size: 24px;">/kg</span></div>
            <div class="sub-value">Total do Pedido: R$ {venda_total:,.2f}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;">
            <div class="metric-label">🟢 Sua Comissão ({pct_comissao}%)</div>
            <div class="profit-value">R$ {valor_comissao_total:,.2f}</div>
            <div class="sub-value">Ganho: R$ {comissao_por_kg:.3f} por kg</div>
        </div>""", unsafe_allow_html=True)

    st.subheader(f"📊 Histórico LME: {produto_sel}")
    fig = go.Figure(go.Bar(x=df_hist.index.strftime('%d/%m'), y=df_hist['Close'].round(2), text=df_hist['Close'].round(2), textposition='outside', marker_color='#fff'))
    fig.update_layout(height=280, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

    # 9. WhatsApp com Nome Atualizado
    st.divider()
    vol_display = f"{volume_input} Toneladas" if unidade == "Toneladas" else f"{volume_input} KG"
    
    msg_zap = f"""Olá, *{cliente}*! 👋

Abaixo, a cotação oficializada pela *ALFA METAIS REPRESENTAÇÕES* para sua análise:

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

    st.subheader("📱 Gerar Proposta WhatsApp")
    st.code(msg_zap, language="text")

else:
    st.error("Erro na sincronização.")


