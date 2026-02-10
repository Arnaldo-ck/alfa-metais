import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS DEFINITIVO PARA CENTRALIZAÇÃO TOTAL
st.markdown("""
    <style>
    /* Fundo Dark Global */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* Forçar centralização da Logo */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-left: auto;
        margin-right: auto;
    }

    /* Centralizar Títulos */
    h1, h2, h3, p {
        text-align: center !important;
        color: white !important;
    }

    /* Ajuste dos Inputs */
    .stTextInput div div input {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        text-align: center;
    }

    /* CENTRALIZAÇÃO DO BOTÃO - O ponto mais difícil no Streamlit */
    div.stButton {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    div.stButton > button {
        width: 100% !important;
        max-width: 300px !important;
        background-color: #0D47A1 !important;
        color: white !important;
        font-weight: bold !important;
        height: 50px;
        border-radius: 8px;
        border: 1px solid #1E88E5;
        margin: 20px auto !important; /* Margem automática nas laterais */
    }

    /* Estilo do Terminal (Pós-Login) */
    .brand-title { 
        font-size: 38px !important; font-weight: 800; color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        text-align: center; 
    }
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 20px; border-radius: 15px; border-bottom: 5px solid #0D47A1; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONTROLE DE SESSÃO
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    
    # Criamos colunas para criar um "corredor" central estreito
    col_esq, col_central, col_dir = st.columns([1.5, 1, 1.5])
    
    with col_central:
        st.write("##")
        # Logo centralizada com largura fixa
        try:
            st.image("Alfa.png", width=250)
        except:
            st.markdown("<h1 style='font-size: 30px;'>🛡️ ALFA METAIS</h1>", unsafe_allow_html=True)
        
        st.markdown("### Terminal de Vendas")
        
        # Inputs
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        
        # Botão
        if st.button("ACESSAR TERMINAL"):
            if usuario_input == "alfa" and senha_input == "metais2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais incorretas!")

# --- SISTEMA ORIGINAL (APÓS LOGIN) ---
else:
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

    if 'reset_trigger' not in st.session_state:
        st.session_state.reset_trigger = 0

    def limpar_campos():
        st.session_state.reset_trigger += 1

    # Sidebar
    st.sidebar.header("📋 Parâmetros")
    if st.sidebar.button("🧹 LIMPAR TUDO", on_click=limpar_campos):
        st.sidebar.info("Dados resetados!")
    
    if st.sidebar.button("🚪 LOGOUT / SAIR"):
        st.session_state.autenticado = False
        st.rerun()

    c_key = f"cliente_{st.session_state.reset_trigger}"
    v_key = f"volume_{st.session_state.reset_trigger}"
    p_key = f"produto_{st.session_state.reset_trigger}"
    com_key = f"comissao_{st.session_state.reset_trigger}"

    cliente = st.sidebar.text_input("Cliente:", value="Diretoria de Compras", key=c_key)
    produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()), key=p_key)
    premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(metais_dict[produto_sel]["premio_padrao"]), step=10.0)
    pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5, key=com_key)
    unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
    volume_input = st.sidebar.number_input(f"Volume:", value=1.0 if unidade == "Toneladas" else 1000.0, key=v_key)

    ton_calculo = volume_input if unidade == "Toneladas" else volume_input / 1000

    # Processamento
    df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])

    if not df_hist.empty:
        preco_lme = df_hist['Close'].iloc[-1]
        preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
        venda_total = preco_kg * (ton_calculo * 1000)
        valor_comissao_total = venda_total * (pct_comissao / 100)
        comissao_por_kg = preco_kg * (pct_comissao / 100)

        st.markdown('<p class="brand-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: white; margin-bottom: 20px;">Terminal Comercial | alfametaisrepresentacoes.com.br</p>', unsafe_allow_html=True)

        # Badges de mercado centralizados
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 25px;">
                <span style="background:#1A1C24; padding:10px 20px; border-radius:10px; border:1px solid #30363d; margin:5px; display:inline-block;">💵 Dólar: R$ {dolar_atual:.2f}</span>
                <span style="background:#1A1C24; padding:10px 20px; border-radius:10px; border:1px solid #30363d; margin:5px; display:inline-block;">🏛️ LME: US$ {preco_lme:.2f}</span>
                <span style="background:#1A1C24; padding:10px 20px; border-radius:10px; border:1px solid #30363d; margin:5px; display:inline-block;">🏷️ Prêmio: US$ {premio_ajustado:.2f}</span>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div style="color: #bbb; font-weight: bold;">💰 Preço de Venda</div>
                <div style="font-size: 45px; font-weight: 900; color: white;">R$ {preco_kg:.2f}/kg</div>
                <div style="color: #0D47A1; font-weight: 700;">Total: R$ {venda_total:,.2f}</div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;">
                <div style="color: #bbb; font-weight: bold;">🟢 Sua Comissão ({pct_comissao}%)</div>
                <div style="font-size: 45px; font-weight: 900; color: #00E676;">R$ {valor_comissao_total:,.2f}</div>
                <div style="color: #bbb; font-weight: 700;">Ganho: R$ {comissao_por_kg:.3f}/kg</div>
            </div>""", unsafe_allow_html=True)

        # Gráfico
        fig = go.Figure(go.Bar(x=df_hist.index.strftime('%d/%m'), y=df_hist['Close'].round(2), text=df_hist['Close'].round(2), textposition='outside', marker_color='#0D47A1'))
        fig.update_layout(height=280, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

        # Proposta WhatsApp
        st.divider()
        msg_zap = f"""Olá, *{cliente}*! 👋\n\nAbaixo, a cotação oficializada pela *ALFA METAIS REPRESENTAÇÕES* para sua análise:\n\n📦 *MATERIAL:* {produto_sel.upper()}\n💰 *VALOR:* R$ {preco_kg:.2f}/kg\n⚖️ *VOLUME:* {f"{volume_input} {unidade}"}\n------------------------------\n💵 *TOTAL DO PEDIDO:* R$ {venda_total:,.2f}\n------------------------------\n\n🌐 *DADOS DE MERCADO*\n📈 LME: US$ {preco_lme:.2f}\n💵 Câmbio: R$ {dolar_atual:.2f}\n🏷️ Prêmio: US$ {premio_ajustado:.2f}\n\n⏳ *VALIDADE:* 24 Horas\n⚠️ _Preço sujeito a variação conforme fechamento da LME._\n\nFico à disposição para fecharmos! 🤝"""
        st.subheader("📱 Gerar Proposta WhatsApp")
        st.code(msg_zap, language="text")


