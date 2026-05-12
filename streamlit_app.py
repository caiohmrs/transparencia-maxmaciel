import streamlit as st
from app import Home, Detalhes, Chat   # importa as funções page()

st.set_page_config(page_title="Mandato RAG", layout="wide")

st.sidebar.title("Navegação")
opcao = st.sidebar.radio(
    "Escolha a seção",
    ("🏠 Home – Visão geral", "📚 Busca detalhada", "💬 Chat IA"),
    index=0,
)

if opcao == "🏠 Home – Visão geral":
    Home.page()
elif opcao == "📚 Busca detalhada":
    Detalhes.page()
else:
    Chat.page()
