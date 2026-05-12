import pathlib
import re
import streamlit as st

# -------------------------------------------------
# 1️⃣  Leitura e parsing de `feitos.md`
# -------------------------------------------------
FEITOS_MD_PATH = pathlib.Path(__file__).parent.parent / "feitos.md"


def _parse_feitos_md(path: pathlib.Path) -> dict[str, list[dict[str, str]]]:
    """
    Analisa o markdown `feitos.md` e devolve um dicionário:

            {
                "Planaltina - DF": [
                    {"area": "Educação", "texto": "Foram Indicados via emenda parlamentar ..."},
                    {"area": "Infraestrutura", "texto": "Indicação para melhoria da iluminação pública ..."},
                    {"area": "Saúde", "texto": "Indicação de recursos para melhorias na área da saúde ..."},
                ],
                "São Sebastião": [...],
                ...
            }

    Regras de extração:
    • Cada região começa com “!Nome da RA”.
    • O próximo cabeçalho (linha curta, sem pontuação) indica a área (ex.: Educação, Saúde).
    • Linhas que iniciam com “•”, “-” ou “*” são descrições de feitos.
    • São mantidos, por ordem de aparição, até três feitos diferentes por área.
    """
    if not path.is_file():
        st.error(f"Arquivo de fatos não encontrado: {path}")
        return {}

    raw = path.read_text(encoding="utf-8")

    # Divide o conteúdo por região (marca “!” no início da linha)
    sections = re.split(r"^!", raw, flags=re.MULTILINE)

    data: dict[str, list[dict[str, str]]] = {}

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        lines = sec.splitlines()
        ra_name = lines[0].strip()
        # Normaliza possíveis travessões
        ra_name = ra_name.replace("\u2013", "-")

        items: list[dict[str, str]] = []
        current_area: str | None = None

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Detecta cabeçalhos de área (linhas curtas e sem pontuação)
            if re.fullmatch(r"[A-Za-zÀ-ÿ ]+", line) and line.lower() not in {
                "ações realizadas",
                "resultados e impactos",
                "destaque específico da região administrativa",
                "atividade",
                "participação comunitária",
            }:
                current_area = line
                continue

            # Detecta marcadores de bullet
            if line.startswith(("•", "-", "*")):
                if current_area is None:
                    current_area = "Outros"
                texto = line.lstrip("•-* ").strip()
                # Evita ultrapassar 3 itens por mesma área
                area_items = [i for i in items if i["area"] == current_area]
                if len(area_items) < 3:
                    items.append({"area": current_area, "texto": texto})

        # Garante ao menos 3 itens (preenche com placeholder se necessário)
        if len(items) < 3:
            filler = "Informação resumida da região."
            while len(items) < 3:
                items.append({"area": "Outros", "texto": filler})

        data[ra_name] = items

    return data


# Carrega os fatos ao iniciar o módulo
FEITOS_POR_RA = _parse_feitos_md(FEITOS_MD_PATH)

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
    # Seleciona como padrão as quatro regiões citadas no pedido
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
    # 2️⃣ Renderiza os cards por região selecionada
    # -------------------------------------------------
    for ra in regioes_escolhidas:
        st.subheader(f"🗺️ {ra}")
        itens = FEITOS_POR_RA.get(ra, [])
        n_cols = 3
        cols = st.columns(n_cols)

        for idx, item in enumerate(itens[:3]):  # máximo de 3 cards por região
            col = cols[idx % n_cols]
            card_html = f"""
            <div class="card">
                <h3>{item["area"]}</h3>
                <p>{item["texto"]}</p>
            </div>
            """
            col.markdown(card_html, unsafe_allow_html=True)

    st.info(
        "Explore a aba **Detalhes** para buscar informações específicas "
        "ou a aba **Chat IA** para conversar com o assistente."
    )
