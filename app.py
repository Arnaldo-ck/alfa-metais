import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Login", layout="wide", page_icon="🛡️")

# 2. CSS - ALINHAMENTO CENTRAL TOTAL E ESTILO DARK
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp, [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }

    /* Forçar centralização de todos os blocos na tela de login */
    .login-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    /* Centralização da Logo via seletor de teste */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }

    /* Título com contorno e centralizado */
    .brand-title-login { 
        font-size: 38px !important; 
        font-weight: 800; 
        color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        text-align: center;
        margin-bottom: 25px;
    }

    /* Ajuste de largura dos campos e botão */
    .stTextInput, .stButton {
        width: 100%;
        max-width: 350px !important;
        margin: 0 auto !important;
    }
    
    /* Centralizar o texto dentro do botão e dos inputs */
    div.stButton > button {
        width: 100% !important;
        background-color: #0D47A1 !important;
        color: white !important;
        border: 1px solid #fff !important;
        font-weight: 700;
        margin-top: 10px;
    }

    input {
        text-align: center !important;
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }

    /* Esconder o label (e-mail/senha) para um visual mais clean, 
       já que usamos placeholders */
    label {
        display: none !important;
    }

    /* Estilo do Terminal */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 25px; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 5px solid #0D47A1; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Autenticação
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def validar_login(user, pwd):
    USUARIO_CORRETO = "contato@alfametaisrepresentacoes.com.br"
    SENHA_CORRETA = "alfa2026"
    if user == USUARIO_CORRETO and pwd == SENHA_CORRETA:
        st.session_state.autenticado = True
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos.")

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.write("<br><br><br>", unsafe_allow_html=True)
    
    # Usamos uma estrutura de colunas para "espremer" o conteúdo no centro
    _, center_col, _ = st.columns([1, 1, 1])
    
    with center_col:
        # Container para forçar o alinhamento de tudo dentro da coluna
        st.markdown('<div class="login-block">', unsafe_allow_html=True)
        
        try:
            st.image("Alfa.png", width=320)
        except:
            st.markdown("<h2 style='text-align: center;'>🛡️ ALFA METAIS</h2>", unsafe_allow_html=True)
        
        st.markdown('<p class="brand-title-login">ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        
        # Inputs e Botão (os estilos CSS acima cuidam da centralização interna)
        user_input = st.text_input("E-mail", placeholder="E-mail de Acesso")
        pass_input = st.text_input("Senha", type="password", placeholder="Sua Senha")
        
        if st.button("ACESSAR TERMINAL"):
            validar_login(user_input, pass_input)
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- TERMINAL DE VENDAS (MANTIDO) ---
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
        except: return pd.DataFrame(), 5.20

    if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0
    def limpar_campos(): st.session_state.reset_trigger += 1
    
    st.sidebar.button("🧹 LIMPAR TUDO", on_click=limpar_campos)
    if st.sidebar.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()

    c_key = f"c_{st.session_state.reset_trigger}"
    v_key = f"v_{st.session_state.reset_trigger}"
    
    cliente = st.sidebar.text_input("Cliente:", value="Diretoria de Compras", key=c_key)
    produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()))
    premio_padrao = metais_dict[produto_sel]["premio_padrao"]
    premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_padrao), step=10.0)
    pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5)
    unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
    volume_input = st.sidebar.number_input(f"Volume:", value=1.0 if unidade == "Toneladas" else 1000.0, key=v_key)

    df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])
    if not df_hist.empty:
        preco_lme = df_hist['Close'].iloc[-1]
        preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
        venda_total = preco_kg * (volume_input if unidade == "Toneladas" else volume_input / 1000) * 1000

        st.markdown('<p class="brand-title-login" style="font-size:32px !important; margin-bottom:10px;">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        
        # Cards e gráficos seguem aqui como na versão anterior...
        st.markdown(f"""
            <div style="margin-bottom: 20px; text-align: center;">
                <div style="background-color: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 10px; display: inline-block; margin-right: 10px;">💵 Dólar: R$ {dolar_atual:.2f}</div>
                <div style="background-color: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 10px; display: inline-block;">🏛️ LME: US$ {preco_lme:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class="metric-card"><div style="font-size: 18px; font-weight: 700; color: #fff;">💰 Venda</div>
            <div style="font-size: 40px; font-weight: 900;">R$ {preco_kg:.2f}/kg</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;"><div style="font-size: 18px; font-weight: 700; color: #fff;">🟢 Comissão</div>
            <div style="font-size: 40px; font-weight: 900; color: #00E676;">R$ {venda_total * (pct_comissao/100):,.2f}</div></div>""", unsafe_allow_html=True)




