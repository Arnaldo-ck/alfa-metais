import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS DEFINITIVO - FOCO EM CENTRALIZAÇÃO E TAMANHO FIXO
st.markdown("""
    <style>
    /* Fundo Dark */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* CONTAINER CENTRAL DE LOGIN */
    /* Criamos uma div para limitar o tamanho de tudo no centro */
    .main-login-container {
        max-width: 350px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* AJUSTE DA LOGO */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    [data-testid="stImage"] img {
        max-width: 250px !important; /* Controla o tamanho da logo para não ficar gigante */
    }

    /* CAMPOS DE INPUT */
    .stTextInput div div input {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 5px !important;
        height: 45px;
    }

    /* BOTÃO ACESSAR TERMINAL - CENTRALIZAÇÃO REAL */
    div.stButton {
        text-align: center;
        display: flex;
        justify-content: center;
        width: 100%;
    }
    div.stButton > button {
        width: 100% !important; /* Ocupa a largura do container de 350px */
        max-width: 350px !important;
        background-color: #0D47A1 !important;
        color: white !important;
        font-weight: bold !important;
        height: 50px;
        border-radius: 8px;
        margin-top: 15px;
        border: none;
    }

    /* ESTILIZAÇÃO DO SISTEMA (PÓS-LOGIN) */
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

# 3. LÓGICA DE ACESSO
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    
    # Criamos o container centralizado usando colunas de preenchimento
    _, col_central, _ = st.columns([1.2, 1, 1.2])
    
    with col_central:
        st.write("##")
        st.write("##")
        
        # Logo com tamanho controlado
        try:
            st.image("Alfa.png", width=250)
        except:
            st.markdown("<h1 style='text-align: center; color: white;'>🛡️ ALFA METAIS</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: white;'>Acesso Restrito</h3>", unsafe_allow_html=True)
        
        # Inputs com nomes FORA dos campos
        user = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        # Botão centralizado
        if st.button("ACESSAR TERMINAL"):
            if user == "alfa" and password == "metais2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")

# --- SISTEMA ORIGINAL ---
else:
    # 4. Dados e Funções (Tudo mantido conforme seu original)
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
        st.sidebar.info("Resetado!")
    
    if st.sidebar.button("🚪 SAIR"):
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

    # Interface Principal
    df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])

    if not df_hist.empty:
        preco_lme = df_hist['Close'].iloc[-1]
        preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
        venda_total = preco_kg * (ton_calculo * 1000)
        valor_comissao_total = venda_total * (pct_comissao / 100)
        comissao_por_kg = preco_kg * (pct_comissao / 100)

        st.markdown('<p class="brand-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: white;">Terminal de Inteligência Comercial</p>', unsafe_allow_html=True)

        st.write("##")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("💵 Dólar", f"R$ {dolar_atual:.2f}")
        col_m2.metric("🏛️ LME", f"US$ {preco_lme:.2f}")
        col_m3.metric("🏷️ Prêmio", f"US$ {premio_ajustado:.2f}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div style="color: #bbb;">💰 Preço de Venda</div>
                <div style="font-size: 45px; font-weight: 900;">R$ {preco_kg:.2f}/kg</div>
                <div style="color: #0D47A1;">Total: R$ {venda_total:,.2f}</div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;">
                <div style="color: #bbb;">🟢 Sua Comissão ({pct_comissao}%)</div>
                <div style="font-size: 45px; font-weight: 900; color: #00E676;">R$ {valor_comissao_total:,.2f}</div>
                <div style="color: #bbb;">Ganho: R$ {comissao_por_kg:.3f}/kg</div>
            </div>""", unsafe_allow_html=True)

        fig = go.Figure(go.Bar(x=df_hist.index.strftime('%d/%m'), y=df_hist['Close'].round(2), text=df_hist['Close'].round(2), textposition='outside', marker_color='#0D47A1'))
        fig.update_layout(height=280, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)




