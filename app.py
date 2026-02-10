import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Login", layout="wide", page_icon="🛡️")

# 2. CSS - ESTILO DARK E CENTRALIZAÇÃO REFORÇADA
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp, [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }

    /* Forçar centralização de todos os elementos na coluna */
    [data-testid="stVerticalBlock"] > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* Ajuste específico da Logo */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center !important;
        width: 100%;
        margin-bottom: 5px;
    }

    /* Título Centralizado e Corrigido */
    .brand-title-login { 
        font-size: 32px !important; 
        font-weight: 800; 
        color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        text-align: center;
        margin-bottom: 20px;
        width: 100%;
    }

    /* Campos de Login e Botão - Largura Estrita */
    .stTextInput, .stButton {
        width: 280px !important; /* Diminuído para dar aspecto mais elegante */
        margin: 0 auto !important;
    }
    
    input {
        text-align: center !important;
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }

    /* Botão Acessar */
    div.stButton > button {
        width: 100% !important;
        background-color: #0D47A1 !important;
        color: white !important;
        border: 1px solid #fff !important;
        font-weight: 700;
        margin-top: 15px;
    }

    /* Esconder Labels */
    label { display: none !important; }

    /* Estilo do Terminal */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 20px; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 5px solid #0D47A1; margin-bottom: 15px;
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
        st.error("Dados incorretos.")

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.write("<br><br><br>", unsafe_allow_html=True)
    
    # Colunas mais estreitas no centro para forçar o agrupamento
    _, center_col, _ = st.columns([1.2, 1, 1.2])
    
    with center_col:
        # Logo reduzida para 220px para facilitar a centralização
        try:
            st.image("Alfa.png", width=220)
        except:
            st.markdown("<h3 style='text-align: center;'>🛡️ ALFA METAIS</h3>", unsafe_allow_html=True)
        
        st.markdown('<p class="brand-title-login">ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        
        user_input = st.text_input("E-mail", placeholder="E-mail de Acesso")
        pass_input = st.text_input("Senha", type="password", placeholder="Sua Senha")
        
        if st.button("ACESSAR TERMINAL"):
            validar_login(user_input, pass_input)

# --- TERMINAL DE VENDAS ---
else:
    # (O restante do código do terminal permanece igual à versão anterior)
    st.sidebar.title("🛡️ ALFA METAIS")
    if st.sidebar.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()
    
    # Conteúdo do Terminal...
    st.markdown('<p class="brand-title-login" style="font-size:28px !important;">ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
    st.info("Terminal de Vendas Ativo - Utilize a barra lateral para operar.")





