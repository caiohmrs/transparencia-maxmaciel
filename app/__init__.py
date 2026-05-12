import streamlit as st
from rag_builder import carregar_base_rag

@st.cache_resource(show_spinner=False)
def get_rag():
    """Carrega (ou cria) o índice FAISS + textos e devolve (index, base_texto)."""
    index, base_texto = carregar_base_rag()
    return index, base_texto
