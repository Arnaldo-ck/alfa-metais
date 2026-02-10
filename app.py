import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração da Página (MANTIDA)
st.set_page_config(page_title="ALFA METAIS - Intelligence", layout="wide", page_icon="🛡️")

# 2. CSS - ESTILIZAÇÃO GLOBAL (Incluindo a tela de Login)
st.markdown("""
    <style>
    /* Fundo Dark Global */
    .stApp {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }

    /* Centralização do formulário de Login */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 50px;
    }

    /* Ajuste dos campos de input para ficarem menores e centralizados */
    .stTextInput div div input {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        text-align: center;
        max-width: 350px;
        margin: 0 auto;
    }

    /* Botão ACESSAR TERMINAL centralizado */
    div.stButton > button:first-child {
        display: block;
        margin: 20px auto !important;
        width: 100%;
        max-width: 350px;
        background-color: #0D47A1;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
    }

    /* Estilo do título original e cards (mantidos do seu código) */
    .brand-title { 
        font-size: 42px !important; font-weight: 800; color: #0D47A1; 
        text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
        text-align: center;
    }
    .brand-subtitle { font-size: 20px !important; color: #fff !important; text-align: center; margin-bottom: 25px; }
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        padding: 25px; border-radius: 15px; border-bottom: 5px solid #0D47A1; margin-bottom: 20px;
    }
    .market-badge {
        background-color: rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 10px;
        font-weight: 700; color: #fff !important; display: inline-block; margin-right: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE ACESSO (SESSION STATE) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PÁGINA DE LOGIN ---
if not st.session_state.autenticado:
    # Centralização manual via colunas para a logo e inputs
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("") # Espaçador
        try:
            st.image("Alfa.png", width=200) # Logo centralizada pelo tamanho e coluna
        except:
            st.markdown("<h1 style='text-align: center;'>🛡️ ALFA METAIS</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center;'>Acesso ao Terminal</h3>", unsafe_allow_html=True)
        
        user = st.text_input("Usuário", placeholder="Digite seu usuário")
        password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        
        if st.button("ACESSAR TERMINAL"):
            # Coloque aqui o seu usuário e senha de preferência
            if user == "alfa" and password == "metais2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

# --- SISTEMA ORIGINAL (SÓ CARREGA SE AUTENTICADO) ---
else:
    # 3. Dados (MANTIDO)
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

    # 4. Funções de Reset
    if 'reset_trigger' not in st.session_state:
        st.session_state.reset_trigger = 0

    def limpar_campos():
        st.session_state.reset_trigger += 1

    # 5. Barra Lateral
    st.sidebar.header("📋 Parâmetros")
    if st.sidebar.button("🧹 LIMPAR TUDO", on_click=limpar_campos):
        st.sidebar.info("Campos resetados!")
    
    if st.sidebar.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()

    # (RESTANTE DO SEU CÓDIGO ORIGINAL SEGUE ABAIXO...)
    c_key = f"cliente_{st.session_state.reset_trigger}"
    v_key = f"volume_{st.session_state.reset_trigger}"
    p_key = f"produto_{st.session_state.reset_trigger}"
    com_key = f"comissao_{st.session_state.reset_trigger}"

    cliente = st.sidebar.text_input("Cliente:", value="Diretoria de Compras", key=c_key)
    produto_sel = st.sidebar.selectbox("Produto:", list(metais_dict.keys()), key=p_key)
    premio_padrao = metais_dict[produto_sel]["premio_padrao"]
    premio_ajustado = st.sidebar.number_input("Prêmio (US$):", value=float(premio_padrao), step=10.0)
    pct_comissao = st.sidebar.slider("Comissão (%)", 0.0, 10.0, 3.0, 0.5, key=com_key)
    unidade = st.sidebar.radio("Unidade:", ("Toneladas", "Quilos"), horizontal=True)
    volume_input = st.sidebar.number_input(f"Volume:", value=1.0 if unidade == "Toneladas" else 1000.0, key=v_key)

    ton_calculo = volume_input if unidade == "Toneladas" else volume_input / 1000

    # 6. Processamento e Interface
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
            <div style="margin-bottom: 20px; text-align: center;">
                <div class="market-badge">💵 Dólar: R$ {dolar_atual:.2f}</div>
                <div class="market-badge">🏛️ LME: US$ {preco_lme:.2f}</div>
                <div class="market-badge">🏷️ Prêmio: US$ {premio_ajustado:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">💰 Preço de Venda</div>
                <div class="price-value">R$ {preco_kg:.2f}<span style="font-size: 24px;">/kg</span></div>
                <div class="sub-value">Total: R$ {venda_total:,.2f}</div>
            </div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""<div class="metric-card" style="border-bottom-color: #00E676;">
                <div class="metric-label">🟢 Sua Comissão ({pct_comissao}%)</div>
                <div class="profit-value">R$ {valor_comissao_total:,.2f}</div>
                <div class="sub-value">Ganho: R$ {comissao_por_kg:.3f}/kg</div>
            </div>""", unsafe_allow_html=True)

        # Gráfico e Mensagem WhatsApp (Mantidos conforme original)
        fig = go.Figure(go.Bar(x=df_hist.index.strftime('%d/%m'), y=df_hist['Close'].round(2), text=df_hist['Close'].round(2), textposition='outside', marker_color='#0D47A1'))
        fig.update_layout(height=280, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        msg_zap = f"""Olá, *{cliente}*! 👋\n\nAbaixo, a cotação oficializada pela *ALFA METAIS REPRESENTAÇÕES* para sua análise:\n\n📦 *MATERIAL:* {produto_sel.upper()}\n💰 *VALOR:* R$ {preco_kg:.2f}/kg\n⚖️ *VOLUME:* {f"{volume_input} {unidade}"}\n------------------------------\n💵 *TOTAL DO PEDIDO:* R$ {venda_total:,.2f}\n------------------------------\n\n🌐 *DADOS DE MERCADO*\n📈 LME: US$ {preco_lme:.2f}\n💵 Câmbio: R$ {dolar_atual:.2f}\n🏷️ Prêmio: US$ {premio_ajustado:.2f}\n\n⏳ *VALIDADE:* 24 Horas\n⚠️ _Preço sujeito a variação conforme fechamento da LME._\n\nFico à disposição para fecharmos! 🤝"""
        st.subheader("📱 Gerar Proposta WhatsApp")
        st.code(msg_zap, language="text")






