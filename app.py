import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Login", layout="wide", page_icon="🛡️")

# 2. CSS - ESTILO DARK TOTAL E LOGIN CENTRALIZADO
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp, [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }

    /* Centralização da tela de Login */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 50px;
    }

    /* Estilização dos Inputs */
    input {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 5px;
    }

    /* Título com contorno */
    .brand-title { 
        font-size: 42px !important; 
        font-weight: 800; 
        color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        text-align: center;
    }

    /* Cards e Badges do Terminal */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 25px; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 5px solid #0D47A1; margin-bottom: 20px;
    }
    .market-badge {
        background-color: rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 10px;
        font-weight: 700; font-size: 20px !important; color: #fff !important;
        display: inline-block; margin-right: 15px; border: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Autenticação
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def validar_login(user, pwd):
    # Substitua pelo seu e-mail e senha de preferência
    USUARIO_CORRETO = "contato@alfametaisrepresentacoes.com.br"
    SENHA_CORRETA = "alfa2026"
    
    if user == USUARIO_CORRETO and pwd == SENHA_CORRETA:
        st.session_state.autenticado = True
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos.")

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    
    with col_l2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        try:
            st.image("Alfa.png", width=250)
        except:
            st.markdown("### 🛡️ ALFA METAIS")
        
        st.markdown('<p class="brand-title">REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        st.write("")
        
        user_input = st.text_input("E-mail de Acesso")
        pass_input = st.text_input("Senha", type="password")
        
        if st.button("ACESSAR TERMINAL", use_container_width=True):
            validar_login(user_input, pass_input)
        st.markdown('</div>', unsafe_allow_html=True)

# --- TERMINAL DE VENDAS (SÓ ABRE SE AUTENTICADO) ---
else:
    # 4. Dados e Funções (Mesma lógica anterior)
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

    # 5. Barra Lateral e Botão Limpar
    if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0
    def limpar_campos(): st.session_state.reset_trigger += 1
    
    st.sidebar.button("🧹 LIMPAR TUDO", on_click=limpar_campos)
    if st.sidebar.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()

    c_key = f"c_{st.session_state.reset_trigger}"
    v_key = f"v_{st.session_state.reset_trigger}"
    p_key = f"p_{st.session_state.reset_trigger}"
    
    cliente = st.sidebar.text_input("Cliente:", value="Diretoria de Compras", key=c_key)
    produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()), key=p_key)
    premio_padrao = metais_dict[produto_sel]["premio_padrao"]
    premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_padrao), step=10.0)
    pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5)
    unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
    volume_input = st.sidebar.number_input(f"Volume:", value=1.0 if unidade == "Toneladas" else 1000.0, key=v_key)

    # 6. Processamento e Visualização
    df_hist, dolar_atual = carregar_dados_metal(metais_dict[produto_sel]["ticker"])
    if not df_hist.empty:
        preco_lme = df_hist['Close'].iloc[-1]
        preco_kg = ((preco_lme + premio_ajustado) * dolar_atual) / 1000
        venda_total = preco_kg * (volume_input if unidade == "Toneladas" else volume_input / 1000) * 1000

        st.markdown('<p class="brand-title">🛡️ ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="margin-bottom: 20px; text-align: center;">
                <div class="market-badge">💵 Dólar: R$ {dolar_atual:.2f}</div>
                <div class="market-badge">🏛️ LME: US$ {preco_lme:.2f}</div>
                <div class="market-badge">🏷️ Prêmio: US$ {premio_ajustado:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">💰 Preço de Venda</div>
            <div class="price-value">R$ {preco_kg:.2f}/kg</div><div class="sub-value">Total: R$ {venda_total:,.2f}</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;"><div class="metric-label">🟢 Comissão</div>
            <div class="profit-value">R$ {venda_total * (pct_comissao/100):,.2f}</div><div class="sub-value">{pct_comissao}% do pedido</div></div>""", unsafe_allow_html=True)

        st.plotly_chart(go.Figure(data=[go.Bar(x=df_hist.index, y=df_hist['Close'], marker_color='#0D47A1')], layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=250)), use_container_width=True)



