import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Login", layout="wide", page_icon="🛡️")

# Função para converter imagem local para base64 (necessário para o HTML injetado)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. CSS Global
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    [data-testid="stSidebar"] { background-color: #0E1117 !important; }
    
    /* Esconder elementos desnecessários na tela de login */
    .stDeployButton, footer, header {visibility: hidden;}
    
    /* Estilo dos campos de entrada que o Streamlit ainda controla */
    .stTextInput input {
        text-align: center !important;
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }
    
    /* Botão de Acesso */
    div.stButton > button {
        width: 100% !important;
        max-width: 300px;
        background-color: #0D47A1 !important;
        color: white !important;
        border: 1px solid #fff !important;
        font-weight: 700;
        display: block;
        margin: 0 auto;
    }

    /* Centralização dos placeholders e labels */
    label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Autenticação
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    # 3.1 Construção do Cabeçalho Centralizado em HTML Puro
    try:
        img_base64 = get_base64_of_bin_file("Alfa.png")
        header_html = f"""
            <div style="text-align: center; width: 100%;">
                <img src="data:image/png;base64,{img_base64}" width="200" style="margin-bottom: 10px;">
                <h1 style="
                    font-size: 36px; 
                    font-weight: 800; 
                    color: #0D47A1; 
                    text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
                    margin-top: 0px;
                    margin-bottom: 20px;
                    font-family: sans-serif;
                ">ALFA METAIS REPRESENTAÇÕES</h1>
            </div>
        """
    except:
        header_html = """
            <div style="text-align: center; width: 100%;">
                <h1 style="color: #0D47A1; text-shadow: 1px 1px #fff;">🛡️ ALFA METAIS REPRESENTAÇÕES</h1>
            </div>
        """

    # Exibe o cabeçalho centralizado
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown(header_html, unsafe_allow_html=True)

    # 3.2 Campos de Login (Usando colunas apenas para limitar a largura)
    _, center_col, _ = st.columns([1.5, 1, 1.5])
    
    with center_col:
        user_input = st.text_input("E-mail", placeholder="E-mail de Acesso")
        pass_input = st.text_input("Senha", type="password", placeholder="Sua Senha")
        
        st.write("") # Espaçador
        
        if st.button("ACESSAR TERMINAL"):
            if user_input == "contato@alfametaisrepresentacoes.com.br" and pass_input == "alfa2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Dados incorretos.")

# --- TERMINAL DE VENDAS ---
else:
    # (Código do Terminal permanece o mesmo das versões estáveis anteriores)
    st.sidebar.image("Alfa.png", use_container_width=True)
    if st.sidebar.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()
    
    st.markdown(f'<h1 style="text-align: center; color: #0D47A1; text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;">🛡️ ALFA METAIS REPRESENTAÇÕES</h1>', unsafe_allow_html=True)
    st.success("Painel de Vendas Liberado")





