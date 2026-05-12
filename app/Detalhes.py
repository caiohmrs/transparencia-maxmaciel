import streamlit as st
import pathlib
import re

# -------------------------------------------------
# 1️⃣ Configurações de Caminho
# -------------------------------------------------
DADOS_MD_PATH = pathlib.Path(__file__).parent.parent / "DADOS_RA_ORGANIZADO.md"

def _carregar_dados_estruturados() -> dict:
    """
    Lê o markdown e organiza em: { 'RA': { 'Tema': [lista_de_acoes] } }
    """
    if not DADOS_MD_PATH.is_file():
        return {}

    with open(DADOS_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Estrutura: RA -> Tema -> Lista de ações
    estrutura = {}
    
    # Divide por RAs
    regioes = content.split("\n## ")
    for reg_sec in regioes:
        if reg_sec.startswith("#"): continue
        
        lines = reg_sec.strip().split("\n")
        if not lines: continue
        
        ra_nome = lines[0].strip()
        estrutura[ra_nome] = {}
        
        # Conteúdo da RA (dividido por Temas)
        ra_content = "\n".join(lines[1:])
        temas_sec = ra_content.split("\n### ")
        
        for tema_sec in temas_sec:
            tema_lines = tema_sec.strip().split("\n")
            if not tema_lines: continue
            
            tema_nome = tema_lines[0].strip()
            # Filtra apenas as linhas que são itens de lista (começam com *)
            acoes = [l.strip() for l in tema_lines[1:] if l.strip().startswith("*")]
            
            if acoes:
                # Remove o prefixo [RA] [Tema] para ficar mais limpo na visualização
                acoes_limpas = []
                for acao in acoes:
                    # Regex para remover os colchetes iniciais: * [RA] [Tema] Ação -> Ação
                    limpa = re.sub(r"^\*\s*\[.*?\]\s*\[.*?\]\s*", "", acao)
                    acoes_limpas.append(limpa)
                
                estrutura[ra_nome][tema_nome] = acoes_limpas
                
    return estrutura

def page():
    st.title("📚 Busca Detalhada por Região")
    st.write(
        "Navegue pelas abas para ver todas as ações e investimentos "
        "do mandato organizados por categoria."
    )

    dados = _carregar_dados_estruturados()
    if not dados:
        st.warning("Dados não encontrados.")
        return

    ra_list = sorted(dados.keys())
    
    # Abas por RA
    tabs_ra = st.tabs([f"📍 {ra}" for ra in ra_list])

    for i, ra in enumerate(ra_list):
        with tabs_ra[i]:
            temas = dados[ra]
            if not temas:
                st.info("Nenhuma ação detalhada encontrada para esta região.")
                continue
            
            # Organiza por Temas (Expanders)
            for tema, acoes in temas.items():
                with st.expander(f"📂 {tema}", expanded=False):
                    # Criamos uma lista markdown formatada
                    lista_markdown = "\n".join([f"- {acao}" for acao in acoes])
                    
                    # Renderizamos com a mesma ID visual da Home
                    st.markdown(f"""<div class="ra-card"><h3>📌 AÇÕES EM {tema.upper()}</h3>

{lista_markdown}

</div>""", unsafe_allow_html=True)

    st.divider()
    st.caption("Filtros automáticos baseados no relatório oficial do mandato.")
