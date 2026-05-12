import pathlib
import re
import streamlit as st
# O cliente já está configurado em rag_chat.py; reutilizamos aqui.
from rag_chat import client

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
# 2️⃣ Função que chama o modelo Ollama para resumir um texto
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def _resumir_texto_ollama(texto: str) -> str:
    """
    Envia *texto* ao modelo Ollama (gpt‑oss:120b) e devolve um resumo
    conciso. O cache evita chamadas repetidas para o mesmo fragmento.
    """
    if not texto:
        return ""

    # Prompt que orienta o modelo a criar um resumo objetivo,
    # mantendo as áreas de interesse (Educação, Saúde, Infraestrutura,
    # Cultura, Mobilidade e Participação Comunitária).
    prompt = (
        "Resuma o texto a seguir, mantendo os principais pontos de "
        "Educação, Saúde, Infraestrutura, Cultura, Mobilidade e "
        "Participação Comunitária. Use linguagem clara e objetiva, em "
        "até três frases curtas.\n\n"
        f"{texto}"
    )

    messages = [{"role": "user", "content": prompt}]

    # -----------------------------------------------------------------
    # O cliente Ollama devolve um dicionário (ou uma tupla contendo o
    # dicionário) quando stream=False.  Não devemos iterar sobre ele.
    # -----------------------------------------------------------------
    resp = client.chat(model="gpt-oss:120b", messages=messages, stream=False)

    # Se a resposta vier embrulhada numa tupla/lista, pegue o primeiro item
    if isinstance(resp, (list, tuple)):
        resp = resp[0] if resp else {}

    # Caso a resposta já seja um dicionário, extraímos o conteúdo da mensagem
    try:
        resumo = resp["message"]["content"]
    except (KeyError, TypeError):
        # Falha graciosa – devolve o texto original (ou uma string vazia)
        resumo = texto

    return resumo.strip()


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
    # 2️⃣ Exibe **resumo** (card) + texto completo opcional
    # -------------------------------------------------
    for ra in regioes_escolhidas:
        st.subheader(f"🗺️ {ra}")
        conteudo = FEITOS_POR_RA.get(ra, "")

        if not conteudo:
            st.info("Nenhum conteúdo encontrado para esta região.")
            continue

        # ---- Resumo (card) -------------------------------------------------
        resumo = _resumir_texto_ollama(conteudo)
        col = st.columns(1)[0]   # usar coluna única para ocupar a largura total
        card_html = f"""
        <div class="card">
            <h3>Resumo da região</h3>
            <p>{resumo}</p>
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

        # ---- Texto completo (expander opcional) -------------------------------
        with st.expander("Ver detalhes completos"):
            st.markdown(conteudo)

    st.info(
        "Explore a aba **Detalhes** para buscar informações específicas "
        "ou a aba **Chat IA** para conversar com o assistente."
    )
