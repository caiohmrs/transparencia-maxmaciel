import pathlib
import re
import streamlit as st

# -------------------------------------------------
# 1️⃣  Leitura completa de `feitos.md`
# -------------------------------------------------
FEITOS_MD_PATH = pathlib.Path(__file__).parent.parent / "feitos.md"


def _carregar_feitos_bruto(path: pathlib.Path) -> dict[str, str]:
    """
    Lê o markdown ``feitos.md`` e devolve um dicionário:

        {
            "Planaltina - DF": "<texto completo da região>",
            "São Sebastião": "<texto completo da região>",
            "Gama": "<texto completo da região>",
            "Ceilândia": "<texto completo da região>",
            ...
        }

    O arquivo está estruturado com marcadores “!Nome da RA”.
    Tudo que vem depois do marcador até o próximo marcador
    (ou fim‑de‑arquivo) é considerado o **conteúdo bruto** da região.
    """
    if not path.is_file():
        st.error(f"Arquivo de fatos não encontrado: {path}")
        return {}

    raw = path.read_text(encoding="utf-8")
    # Separa por linhas que começam com “!” (início de cada região)
    sections = re.split(r"^!", raw, flags=re.MULTILINE)

    regioes: dict[str, str] = {}
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        lines = sec.splitlines()
        nome_ra = lines[0].strip().replace("\u2013", "-")
        # Junta todo o restante da seção como texto bruto
        conteudo = "\n".join(lines[1:]).strip()
        regioes[nome_ra] = conteudo
    return regioes


# Carrega todo o conteúdo já no momento da importação – é apenas leitura de texto
FEITOS_POR_RA = _carregar_feitos_bruto(FEITOS_MD_PATH)

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

    # -------------------------------------------------
    # 1️⃣ Seletor de Regiões Administrativas
    # -------------------------------------------------
    todas_regioes = sorted(FEITOS_POR_RA.keys())
    # Mantemos como padrão as quatro regiões pedidas
    default_sel = [
        ra
        for ra in todas_regioes
        if ra.lower().startswith(
            ("planaltina", "são sebastião", "são sebastiao", "gama", "ceilândia", "ceilanda")
        )
    ]
    regioes_escolhidas = st.multiselect(
        "Selecione as Regiões Administrativas que deseja visualizar",
        options=todas_regioes,
        default=default_sel,
    )

    if not regioes_escolhidas:
        st.warning("Selecione ao menos uma Região Administrativa.")
        return

    # -------------------------------------------------
    # 2️⃣ Exibe o conteúdo **bruto** de cada região escolhida
    # -------------------------------------------------
    for ra in regioes_escolhidas:
        st.subheader(f"🗺️ {ra}")
        # O markdown já vem formatado (bullets, negritos, etc.)
        conteudo = FEITOS_POR_RA.get(ra, "")
        if conteudo:
            st.markdown(conteudo)
        else:
            st.info("Nenhum conteúdo encontrado para esta região.")

    st.info(
        "Explore a aba **Detalhes** para buscar informações específicas "
        "ou a aba **Chat IA** para conversar com o assistente."
    )
