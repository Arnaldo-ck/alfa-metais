import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="ALFA METAIS - Login", layout="wide", page_icon="🛡️")

# 2. CSS - CENTRALIZAÇÃO E AJUSTE DE ESCALA
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp, [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }

    /* Centralização Absoluta da Logo */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    
    /* Título com contorno e fonte ajustada */
    .brand-title-login { 
        font-size: 38px !important; 
        font-weight: 800; 
        color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }

    /* Diminuir largura e fonte dos campos de Login */
    .stTextInput, .stButton {
        max-width: 350px;
        margin: 0 auto;
    }
    
    /* Estilo das etiquetas (labels) acima dos campos */
    label {
        font-size: 14px !important;
        color: #ccc !important;
        text-align: center !important;
        display: block !important;
    }

    input {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        font-size: 14px !important;
        text-align: center !important;
    }

    /* Ajuste do botão */
    div.stButton > button {
        background-color: #0D47A1 !important;
        color: white !important;
        border: 1px solid #fff !important;
        font-weight: 700;
    }

    /* Estilo do Terminal */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 25px; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 5px solid #0D47A1; margin-bottom: 20px;
    }
    .market-badge {
        background-color: rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 10px;
        font-weight: 700; font-size: 18px !important; color: #fff !important;
        display: inline-block; margin-right: 15px; border: 1px solid rgba(255,255,255,0.1);
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
    st.write("<br><br>", unsafe_allow_html=True)
    
    # Criamos 3 colunas, mas usamos a do meio para centralizar tudo
    _, central_col, _ = st.columns([1, 1.5, 1])
    
    with central_col:
        # Logo com largura fixa para centralização
        try:
            st.image("Alfa.png", width=300)
        except:
            st.markdown("<h2 style='text-align: center;'>🛡️ ALFA METAIS</h2>", unsafe_allow_html=True)
        
        st.markdown('<p class="brand-title-login">ALFA METAIS REPRESENTAÇÕES</p>', unsafe_allow_html=True)
        
        # Campos com largura controlada via CSS (max-width: 350px)
        user_input = st.text_input("E-mail", placeholder="seu@email.com")
        pass_input = st.text_input("Senha", type="password", placeholder="********")
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("ACESSAR TERMINAL"):
            validar_login(user_input, pass_input)

# --- TERMINAL DE VENDAS ---
else:
    # 4. Dados e Funções
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
            <div class="price-value">R$ {preco_kg:.2f}<small style="font-size:18px">/kg</small></div><div class="sub-value">Total: R$ {venda_total:,.2f}</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;"><div class="metric-label">🟢 Comissão</div>
            <div class="profit-value">R$ {venda_total * (pct_comissao/100):,.2f}</div><div class="sub-value">{pct_comissao}% de margem</div></div>""", unsafe_allow_html=True)

        fig = go.Figure(data=[go.Bar(x=df_hist.index.strftime('%d/%m'), y=df_hist['Close'], marker_color='#0D47A1')])
        fig.update_layout(height=240, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)





