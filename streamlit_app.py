import streamlit as st
from app import Home, Detalhes, Chat, pdaf

# -------------------------------------------------
# 🎨 Identidade Visual - Max Maciel (Pop Art / Mandato)
# -------------------------------------------------
BRAND_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Outfit:wght@300;400;700&family=Inter:wght@400;700;900&display=swap');

    /* Fundo Principal */
    .stApp {
        background: linear-gradient(135deg, #FFFFFF 0%, #D1D5DB 100%);
        background-color: #E2E8F0;
    }

    /* Títulos Principais */
    h1, h2, .stTitle {
        font-family: 'Bangers', cursive !important;
        color: #B22222 !important; /* Vermelho Tijolo */
        text-transform: uppercase;
        letter-spacing: 2px;
        -webkit-text-stroke: 1px #1A1A1A;
        text-shadow: 3px 3px 0px #1A1A1A;
        font-size: 3.5rem !important;
    }

    h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 900 !important;
        color: #1A1A1A !important;
        text-transform: uppercase;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFD700 0%, #FFFDE7 100%) !important;
        border-right: 3px solid #1A1A1A;
        box-shadow: 4px 0px 15px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] h1 {
        font-family: 'Bangers', cursive !important;
        font-size: 2.2rem !important;
        color: #B22222 !important;
        -webkit-text-stroke: 0.5px #1A1A1A;
        text-align: center;
        margin-bottom: 30px !important;
    }

    /* Estilização do Menu de Rádio (Navegação) */
    [data-testid="stSidebar"] .stRadio > div {
        background-color: transparent !important;
        gap: 0px;
    }

    /* Label 'Escolha a seção' */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
        background-color: #1A1A1A !important;
        padding: 10px !important;
        margin-bottom: 15px !important;
        border: 2px solid #1A1A1A;
    }

    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] p {
        color: #FFD700 !important;
        font-family: 'Bangers', cursive !important;
        font-size: 1.2rem !important;
        text-align: center;
        margin: 0 !important;
    }

    /* Cada item do menu */
    [data-testid="stSidebar"] .stRadio label {
        background-color: #FFFFFF !important;
        border: 2px solid #1A1A1A !important;
        padding: 15px 10px !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        transform: translateX(8px);
        box-shadow: -8px 0px 0px #B22222 !important;
        background-color: #FFFDE7 !important;
    }

    /* Texto dentro da label */
    [data-testid="stSidebar"] .stRadio label p {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #1A1A1A !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }

    /* Esconde apenas o círculo do rádio */
    [data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] {
        width: 100%;
        text-align: center;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Botão Primário */
    .stButton>button {
        background-color: #B22222 !important;
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        border: 2px solid #1A1A1A !important;
        box-shadow: 4px 4px 0px #1A1A1A;
        border-radius: 0px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Estilização de Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #D1D5DB;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        background-color: transparent !important;
        border: none !important;
        color: #64748B !important; /* Cinza suave para inativos */
        font-family: 'Outfit', sans-serif !important;
        font-weight: 400;
        padding: 10px 5px !important;
    }

    .stTabs [aria-selected="true"] {
        color: #B22222 !important; /* Vermelho Mandato */
        font-weight: 700 !important;
        border-bottom: 4px solid #FFD700 !important; /* Barra Ouro */
    }

    /* Estilização de Expanders */
    [data-testid="stExpander"] {
        border: 2px solid #1A1A1A !important;
        background-color: #FFFFFF !important;
        border-radius: 0px !important;
        margin-bottom: 15px !important;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.1);
    }

    [data-testid="stExpander"] summary {
        background-color: #FFFFFF !important;
    }

    [data-testid="stExpander"] summary:hover {
        background-color: #FFFDE7 !important; /* Amarelo clarinho no hover */
    }

    [data-testid="stExpander"] summary p {
        font-family: 'Bangers', cursive !important;
        font-size: 1.4rem !important;
        color: #B22222 !important; /* Vermelho Mandato */
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #F8F9FA !important;
        padding: 10px !important;
    }

    .stButton>button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px #1A1A1A;
    }

    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border: 2px solid #1A1A1A !important;
        border-radius: 0px !important;
        background-color: #FFFFFF !important;
    }

    /* Custom Cards */
    .ra-card {
        background: #FFD700 !important;
        background-image: radial-gradient(#1A1A1A 0.5px, transparent 0.5px) !important;
        background-size: 15px 15px !important; /* Pontilhado sutil estilo Pop Art */
        border: 4px solid #1A1A1A !important;
        box-shadow: 8px 8px 0px #B22222 !important;
        border-radius: 0px !important;
        padding: 35px !important;
        margin-bottom: 45px !important;
    }

    .ra-card h3 {
        color: #B22222 !important;
        -webkit-text-stroke: 1px #1A1A1A;
        font-family: 'Bangers', cursive !important;
        font-size: 2rem !important;
        margin-top: 0px;
    }
    
    .ra-card p, .ra-card li {
        color: #1A1A1A !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 400 !important;
        font-size: 1.1rem !important;
        line-height: 1.4 !important;
    }

    .ra-card ul {
        list-style-type: none !important;
        padding-left: 0px !important;
    }

    .ra-card li {
        background: rgba(255, 255, 255, 0.45) !important;
        padding: 12px 15px !important;
        margin-bottom: 10px !important;
        border-radius: 8px !important;
        border-left: 4px solid #B22222 !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05) !important;
    }

    .ra-card li::before {
        content: "⚡" !important;
        margin-right: 10px !important;
        font-weight: bold !important;
    }

    /* Estilo das Mensagens de Chat */
    [data-testid="stChatMessage"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 20px !important;
        box-sizing: border-box !important;
        padding: 15px !important;
        overflow-x: hidden !important; /* Evita o scroll horizontal */
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        width: 100% !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        hyphens: auto !important;
    }

    /* Cores das Mensagens */
    [data-testid="stChatMessage"][aria-label="Chat message from user"] {
        background-color: #D1D5DB !important; /* Cinza Metálico */
        border-radius: 15px 15px 0px 15px !important;
        border: 2px solid #1A1A1A !important;
    }

    [data-testid="stChatMessage"][aria-label="Chat message from assistant"] {
        background-color: #FFD700 !important; /* Ouro */
        border-radius: 0px 15px 15px 15px !important;
        border: 2px solid #1A1A1A !important;
    }

    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
        color: #1A1A1A !important;
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
        word-break: break-word !important;
    }

    /* Ajuste para listas dentro do chat */
    [data-testid="stChatMessage"] ul {
        padding-left: 20px !important;
        margin: 10px 0 !important;
    }

</style>
"""

st.set_page_config(page_title="Mandato Max Maciel", layout="wide", page_icon="🏛️")
st.markdown(BRAND_CSS, unsafe_allow_html=True)

st.sidebar.title("🏛️ MENU")
opcao = st.sidebar.radio(
    "Escolha a seção",
    ("🏠 Home – Visão geral", "📚 Busca detalhada", "💰 Investimentos PDAF", "💬 MAX.IA"),
    index=0,
)

# -------------------------------------------------
# 📱 Rodapé da Sidebar (Branding)
# -------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center;'>
        <p style='font-family: "Bangers"; color: #1A1A1A; font-size: 1.5rem; margin-bottom: 0;'>MAX MACIEL</p>
        <p style='font-size: 0.8rem; font-weight: bold; color: #1A1A1A;'>DEPUTADO DISTRITAL</p>
        <p style='font-size: 0.7rem; color: #1A1A1A;'>@MAXMACIELDF</p>
        <p style='font-family: "Bangers"; color: #B22222; font-size: 1.2rem;'>☀️ PSOL</p>
    </div>
    """,
    unsafe_allow_html=True
)

if opcao == "🏠 Home – Visão geral":
    Home.page()
elif opcao == "📚 Busca detalhada":
    Detalhes.page()
elif opcao == "💰 Investimentos PDAF":
    pdaf.page()
else:
    Chat.page()
