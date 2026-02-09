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
    .price-card { background-color: rgba(13, 71, 161, 0.05); padding: 20px; border-radius: 10px; border-left: 6px solid #0D47A1; }
    .big-number { font-size: 40px; font-weight: bold; color: #1B5E20; }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo na Barra Lateral
try:
    st.sidebar.image("Alfa.png", use_container_width=True)
except:
    st.sidebar.warning("🛡️ ALFA METAIS")

# 4. Dados e Configurações
metais_dict = {
    "Alumínio P1020": {"ticker": "ALI=F", "spread": 350},
    "Cobre": {"ticker": "HG=F", "spread": 600},
    "Latão": {"ticker": "HG=F", "spread": 450}, 
    "Zamac 5": {"ticker": "ZN=F", "spread": 500}
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

# 5. Interface da Barra Lateral (Gestão da Proposta)
st.sidebar.header("📋 Gestão da Proposta")
cliente = st.sidebar.text_input("Nome do Cliente:", "Diretoria de Compras")
produto_sel = st.sidebar.selectbox("Metal Selecionado:", list(metais_dict.keys()))

# --- NOVO SELETOR DE UNIDADE ---
unidade = st.sidebar.radio("Unidade de Medida:", ("Toneladas", "Quilos"), horizontal=True)
passo = 0.1 if unidade == "Toneladas" else 50.0
valor_padrao = 1.0 if unidade == "Toneladas" else 1000.0

volume_input = st.sidebar.number_input(f"Volume em {unidade}:", value=valor_padrao, step=passo)

# Lógica de conversão interna para cálculo (Sempre baseada em Toneladas para a LME)
ton_calculo = volume_input if unidade == "Toneladas" else volume_input / 1000

# 6. Processamento de Dados
df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])

if not df_hist.empty:
    preco_lme = df_hist['Close'].iloc[-1]
    spread = metais_dict[produto_sel]["spread"]
    
    # Preço por KG: ((LME + Spread) * Dólar) / 1000
    preco_kg = ((preco_lme + spread) * dolar_atual) / 1000
    
    # Valor Total: Preço por KG * Volume total em KG
    venda_total = preco_kg * (ton_calculo * 1000)

    # 7. Exibição Principal
    st.markdown('<p class="main-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
    st.caption("Acesse: alfametaisrepresentacoes.com.br")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("💰 Cotação do Dia")
        st.markdown(f"""
        <div class="price-card">
            <span style="font-size: 18px; color: #555;">Preço Sugerido {produto_sel}</span><br>
            <span class="big-number">R$ {preco_kg:.2f}/kg</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.info(f"💵 **Dólar:** R$ {dolar_atual:.2f} | 🏛️ **LME:** US$ {preco_lme:.2f}")
        st.success(f"**Total do Pedido:** R$ {venda_total:,.2f}")

    with col2:
        st.subheader(f"📊 Histórico LME: {produto_sel}")
        fig = go.Figure(go.Bar(
            x=df_hist.index.strftime('%d/%m'),
            y=df_hist['Close'].round(2),
            text=df_hist['Close'].round(2),
            textposition='outside',
            marker_color='#0D47A1'
        ))
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0), dragmode=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 8. Mensagem para WhatsApp (Adaptável KG/Ton)
    st.divider()
    st.subheader("📱 Mensagem para WhatsApp")
    
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

⏳ *VALIDADE:* 24 Horas
⚠️ _Preço sujeito a variação conforme fechamento da LME._

Fico à disposição para fecharmos! 🤝"""

    st.code(msg_zap, language="text")
    st.caption("Passe o mouse sobre o campo acima e clique no ícone de cópia à direita.")

else:
    st.error("Erro ao sincronizar com o mercado financeiro.")


