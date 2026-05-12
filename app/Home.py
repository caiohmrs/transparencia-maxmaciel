import pathlib
import streamlit as st
import json
import os
from rag_chat import client

# -------------------------------------------------
# 1️⃣ Configurações de Caminho e Cache Persistente
# -------------------------------------------------
DADOS_MD_PATH = pathlib.Path(__file__).parent.parent / "DADOS_RA_ORGANIZADO.md"
CACHE_RESUMOS_PATH = pathlib.Path(__file__).parent.parent / "resumos_cache.json"

def _carregar_cache_persistente() -> dict:
    if CACHE_RESUMOS_PATH.exists():
        with open(CACHE_RESUMOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _salvar_no_cache_persistente(cache: dict):
    with open(CACHE_RESUMOS_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def _carregar_dados_ra() -> dict[str, str]:
    """
    Lê o markdown organizado e devolve um dicionário {Nome_RA: conteúdo_markdown}.
    """
    if not DADOS_MD_PATH.is_file():
        st.error(f"Arquivo de dados não encontrado: {DADOS_MD_PATH}")
        return {}

    with open(DADOS_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("\n## ")
    regioes = {}
    
    for sec in sections:
        if sec.startswith("#"):
            continue
        lines = sec.strip().split("\n")
        if not lines:
            continue
        nome_ra = lines[0].strip()
        conteudo_ra = "\n".join(lines[1:]).strip()
        if conteudo_ra.endswith("---"):
            conteudo_ra = conteudo_ra[:-3].strip()
        regioes[nome_ra] = conteudo_ra
    return regioes

# -------------------------------------------------
# 2️⃣ Lógica de Resumo e Exibição
# -------------------------------------------------

def _obter_resumo_ia(ra_nome: str, texto_completo: str) -> str:
    """
    Obtém o resumo: primeiro tenta no cache persistente (JSON),
    se não houver, gera com o LLM e salva.
    """
    cache = _carregar_cache_persistente()
    
    # Se já temos o resumo salvo para esta RA, retornamos ele
    if ra_nome in cache:
        return cache[ra_nome]
    
    # Caso contrário, geramos com o LLM
    with st.spinner(f"Gerando resumo IA para {ra_nome}..."):
        prompt = (
            "Você é um Analista de Comunicação focado em síntese executiva. "
            "Sua tarefa é ler os dados de ações parlamentares e criar um resumo "
            "EXTREMAMENTE CURTO e direto ao ponto.\n\n"
            "REGRAS:\n"
            "1. Use 5 tópicos curtos e impactantes.\n"
            "2. Use verbos de ação no presente ou pretérito (ex: 'Garantimos', 'Transformamos', 'Conquistamos').\n"
            "3. Cada tópico deve focar no benefício real para a comunidade (ex: 'X escolas reformadas', 'Mais ônibus para o IFB').\n"
            "4. Mantenha um tom entusiasmado, focado em prestação de contas e direitos sociais.\n\n"
            f"DADOS DE {ra_nome}:\n{texto_completo}"
        )
        
        try:
            resp = client.chat(model="gpt-oss:120b", messages=[{"role": "user", "content": prompt}], stream=False)
            resumo = resp["message"]["content"].strip()
            
            # Salva no cache para a próxima vez
            cache[ra_nome] = resumo
            _salvar_no_cache_persistente(cache)
            return resumo
        except Exception as e:
            return f"Resumo temporariamente indisponível. Erro: {e}"

def page():
    st.title("🏛️ Painel Geral do Mandato")
    
    st.write(
        "Bem-vindo ao portal de transparência. Aqui você encontra uma visão consolidada "
        "das ações realizadas em cada Região Administrativa."
    )

    dados_ra = _carregar_dados_ra()
    if not dados_ra:
        st.warning("Nenhum dado disponível no momento.")
        return

    ra_list = sorted(dados_ra.keys())
    
    if not ra_list:
        st.info("Nenhuma região encontrada no documento.")
        return

    # Criação das abas dinâmicas baseadas nas RAs encontradas
    tabs = st.tabs([f"📍 {ra}" for ra in ra_list])

    for i, ra in enumerate(ra_list):
        with tabs[i]:
            conteudo = dados_ra[ra]
            
            # Obtém resumo (do cache ou gera novo)
            resumo = _obter_resumo_ia(ra, conteudo)
            
            # Renderização do Card com Markdown interno para garantir os bullets
            st.markdown(f"""<div class="ra-card"><h3>✨ RESUMO EXECUTIVO</h3>

{resumo}
</div>""", unsafe_allow_html=True)
            
    st.divider()
    st.info(
        "Explore a aba **Busca detalhada** para filtrar ações por tema "
        "ou a aba **MAX.IA** para conversar com nosso assistente virtual."
    )
    st.caption("Dados atualizados com base no relatório de atividades do mandato.")
