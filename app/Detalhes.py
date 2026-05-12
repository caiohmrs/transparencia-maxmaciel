import streamlit as st
import numpy as np
from rag_builder import _get_model   # modelo de embedding para gerar a query
from . import get_rag                # cache de índice e textos

def page():
    st.title("📚 Busca detalhada")
    st.write(
        "Digite um termo ou pergunta. O sistema recupera os trechos mais "
        "relevantes do nosso acervo documental."
    )

    query = st.text_input("Pergunta / termo de busca", key="search_query")
    if query:
        index, base_texto = get_rag()      # usa o cache definido em __init__.py

        # ---- Busca FAISS -------------------------------------------------
        instrucao = "Represent this query for retrieving relevant documents"
        query_input = f"Instruct: {instrucao}\nQuery: {query}"
        query_vec = _get_model().encode([query_input])

        _, idxs = index.search(np.array(query_vec).astype("float32"), k=10)
        resultados = [base_texto[i] for i in idxs[0]]

        # ---- Exibição ----------------------------------------------------
        st.subheader("Fragmentos recuperados")
        for i, frag in enumerate(resultados, start=1):
            st.markdown(f"**{i}.** {frag}")
