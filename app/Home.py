import json
import pathlib
import streamlit as st

# -------------------------------------------------
# Onde os dados dos feitos são armazenados
# -------------------------------------------------
# Se existir um arquivo JSON na raiz do projeto (ao lado da pasta "app"),
# ele será carregado. Caso contrário, será usada a lista hard‑coded.
FEITOS_PATH = pathlib.Path(__file__).parent.parent / "feitos.json"

if FEITOS_PATH.is_file():
    # Exemplo de estrutura esperada no JSON:
    # [
    #   {"titulo": "Projetos concluídos", "texto": "128 obras finalizadas em saúde, educação e infraestrutura."},
    #   {"titulo": "Investimento total", "texto": "R$ 1,2 bilhão aplicados em obras públicas."},
    #   {"titulo": "Regiões atendidas", "texto": "9 regiões atendidas, de Planaltina a Gama, beneficiando mais de 1,5 milhão de habitantes."}
    # ]
    with FEITOS_PATH.open(encoding="utf-8") as f:
        FEITOS = json.load(f)
else:
    # Lista padrão – substitua pelos textos reais do seu mandato
    FEITOS = [
        {
            "titulo": "Projetos concluídos",
            "texto": "128 obras finalizadas em saúde, educação e infraestrutura."
        },
        {
            "titulo": "Investimento total",
            "texto": "R$ 1,2 bilhão aplicados em obras públicas."
        },
        {
            "titulo": "Regiões atendidas",
            "texto": "9 regiões atendidas, de Planaltina a Gama, beneficiando mais de 1,5 milhão de habitantes."
        },
        # Adicione mais dicionários aqui caso queira mais cards
    ]

# -------------------------------------------------
# CSS para estilizar os cards
# -------------------------------------------------
CARD_STYLE = """
<style>
.card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: transform 0.1s ease;
}
.card:hover {
    transform: translateY(-2px);
}
.card h3 {
    margin-top: 0;
    margin-bottom: 0.4rem;
    color: #0e1117;
}
.card p {
    margin: 0;
    color: #333333;
    line-height: 1.4;
}
</style>
"""

# -------------------------------------------------
# Página principal
# -------------------------------------------------
def page():
    st.title("🏛️ Mandato – Principais feitos")
    st.markdown(CARD_STYLE, unsafe_allow_html=True)

    # Definir número de colunas (até 3 cards por linha)
    n_cols = 3
    cols = st.columns(n_cols)

    for idx, feito in enumerate(FEITOS):
        col = cols[idx % n_cols]
        card_html = f"""
        <div class="card">
            <h3>{feito["titulo"]}</h3>
            <p>{feito["texto"]}</p>
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

    st.info(
        "Explore a aba **Detalhes** para buscar informações específicas "
        "ou a aba **Chat IA** para conversar com o assistente."
    )
