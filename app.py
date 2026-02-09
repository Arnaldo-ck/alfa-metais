import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS para visual profissional
st.markdown("""
    <style>
    .main-title { font-size: 30px; font-weight: bold; color: #0D47A1; }
    .stCode { background-color: rgba(240, 242, 246, 0.2) !important; border: 1px solid #0D47A1; border-radius: 10px; }
    .price-card { background-color: rgba(13, 71, 161, 0.05); padding: 15px; border-radius: 10px; border-left: 6px solid #0D47A1; }
    .profit-card { background-color: rgba(27, 94, 32, 0.05); padding: 15px; border-radius: 10px; border-left: 6px solid #2E7D32; }
    .big-number { font-size: 32px; font-weight: bold; color: #0D47A1; }
    .profit-number { font-size: 32px; font-weight: bold; color: #2E7D32; }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo na Barra Lateral
try:
    st.sidebar.image("Alfa.png", use_container_width=True)
except:
    st.sidebar.warning("🛡️ ALFA METAIS")

# 4. Dados Iniciais
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

# 5. Barra Lateral - Controles de Venda
st.sidebar.header("📋 Gestão da Proposta")
cliente = st.sidebar.text_input("Nome do Cliente:", "Diretoria de Compras")
produto_sel = st.sidebar.selectbox("Metal Selecionado:", list(metais_dict.keys()))

st.sidebar.divider()
st.sidebar.subheader("💰 Parâmetros Financeiros")
premio_base = metais_dict[produto_sel]["premio_padrao"]
premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_base), step=10.0)

# CAMPO DE COMISSÃO EDITÁVEL
pct_comissao = st.sidebar.slider("Sua Comissão (%)", 0.0, 10.0, 3.0, 0.5)

unidade = st.sidebar.radio("Unidade de Medida:", ("Toneladas", "Quilos"), horizontal=True)
volume_input = st.sidebar.number_input(f"Volume em {unidade}:", value=1.0 if unidade == "Toneladas" else 1000.0, step=0.1 if unidade == "Toneladas" else 50.0)

ton_calculo = volume_input if unidade == "Toneladas" else volume_input / 1000

# 6. Lógica de Negócio
df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])

if not df_hist.empty:
    preco_lme = df_hist['Close'].iloc[-1]
    
    # Preço Final por KG
    preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
    venda_total = preco_kg * (ton_calculo * 1000)
    
    # Cálculo da Comissão
    valor_comissao_total = venda_total * (pct_comissao / 100)
    comissao_por_kg = preco_kg * (pct_comissao / 100)

    # 7. Interface Principal
    st.markdown('<p class="main-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 1.2, 2])

    with col1:
        st.markdown(f"""
        <div class="price-card">
            <span style="font-size: 14px; color: #555;">PREÇO DE VENDA</span><br>
            <span class="big-number">R$ {preco_kg:.2f}/kg</span><br>
            <small>Total: R$ {venda_total:,.2f}</small>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"💵 Dólar: R$ {dolar_atual:.2f}\n🏛️ LME: US$ {preco_lme:.2f}")

    with col2:
        # PAINEL DE COMISSÃO (Visível apenas para você no sistema)
        st.markdown(f"""
        <div class="profit-card">
            <span style="font-size: 14px; color: #1B5E20;">SUA COMISSÃO ({pct_comissao}%)</span><br>
            <span class="profit-number">R$ {valor_comissao_total:,.2f}</span><br>
            <small>Ganhando R$ {comissao_por_kg:.3f} por kg</small>
        </div>
        """, unsafe_allow_html=True)
        st.write(f"🏷️ Prêmio: US$ {premio_ajustado:.2f}")

    with col3:
        fig = go.Figure(go.Bar(
            x=df_hist.index.strftime('%d/%m'),
            y=df_hist['Close'].round(2),
            marker_color='#0D47A1'
        ))
        fig.update_layout(height=230, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # 8. Mensagem WhatsApp
    st.divider()
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

    st.subheader("📱 Mensagem para WhatsApp")
    st.code(msg_zap, language="text")

else:
    st.error("Erro na conexão com dados financeiros.")


