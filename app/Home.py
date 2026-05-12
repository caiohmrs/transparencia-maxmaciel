import streamlit as st

def page():
    st.title("🏛️ Mandato – Visão geral")
    
    # ---- Cards (métricas) ----
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="📚 Projetos aprovados", value="128")
        st.caption("Desde o início do mandato")

    with col2:
        st.metric(label="💰 Investimento total", value="R$ 1,2 bi")
        st.caption("Saúde, Educação, Infraestrutura…")

    with col3:
        st.metric(label="🗺️ Regiões atendidas", value="9")
        st.caption("Planaltina, Gama, Ceilândia…")

    st.info(
        "Use a aba **Detalhes** para buscar informações específicas "
        "ou a aba **Chat IA** para conversar com o assistente."
    )
