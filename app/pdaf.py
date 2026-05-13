import streamlit as st
import pandas as pd
import pathlib
import os

# -------------------------------------------------
# 1️⃣ Configurações de Caminho e Carregamento
# -------------------------------------------------
ROOT_PATH = pathlib.Path(__file__).parent.parent
CSV_FILES = {
    "2023": {"path": ROOT_PATH / "PDAF2023.csv", "sep": ";"},
    "2024": {"path": ROOT_PATH / "PDAF2024.csv", "sep": ";"},
    "2025": {"path": ROOT_PATH / "PDAF2025.csv", "sep": ","}
}

def _normalizar_ra(cre_text):
    if pd.isna(cre_text): return "DESCONHECIDO"
    ra = str(cre_text).replace("CRE ", "").replace("CRE'NDIA", "CEILÂNDIA").strip().title()
    ra = ra.replace("Ceilndia", "Ceilândia").replace("Ceil'Ndia", "Ceilândia")
    return ra

@st.cache_data
def _carregar_todos_dados():
    dfs = []
    for ano, config in CSV_FILES.items():
        if os.path.exists(config["path"]):
            df = pd.read_csv(config["path"], sep=config["sep"], encoding="utf-8")
            df["Ano"] = ano
            # Padronização básica
            if "Total" in df.columns: df = df.rename(columns={"Total": "Valor"})
            if "CRE" in df.columns: df["RA"] = df["CRE"].apply(_normalizar_ra)
            else: df["RA"] = "DESCONHECIDO"
            
            # Limpeza de valor (R$ 100.000,00 -> 100000.0)
            def limpar_valor(v):
                if pd.isna(v): return 0.0
                v = str(v).replace("R$", "").replace(".", "").replace(",", ".").strip()
                try: return float(v)
                except: return 0.0
            
            df["Valor_Num"] = df["Valor"].apply(limpar_valor)
            dfs.append(df)
    
    if not dfs: return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

def page():
    st.title("💰 Painel Financeiro – PDAF")
    st.write(
        "Acompanhe o detalhamento das emendas e recursos do **PDAF** destinados "
        "às unidades escolares pelo mandato."
    )

    df_full = _carregar_todos_dados()
    if df_full.empty:
        st.warning("Dados financeiros não encontrados.")
        return

    # --- Filtros no topo ---
    col1, col2 = st.columns([1, 2])
    with col1:
        ano_sel = st.selectbox("📅 Selecione o Ano", ["Todos"] + sorted(list(CSV_FILES.keys()), reverse=True))
    with col2:
        busca = st.text_input("🔍 Buscar Escola", placeholder="Digite o nome da escola...")

    # Aplica filtros
    df = df_full.copy()
    if ano_sel != "Todos":
        df = df[df["Ano"] == ano_sel]
    if busca:
        df = df[df["Unidade Escolar"].str.contains(busca, case=False, na=False)]

    # --- Métricas Gerais ---
    total_investido = df["Valor_Num"].sum()
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 25px; border-radius: 8px; border-left: 8px solid #FFD700; margin-bottom: 30px; box-shadow: 5px 5px 15px rgba(0,0,0,0.2);">
            <p style="color: #FFD700; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; margin: 0; letter-spacing: 1px;">💰 TOTAL INVESTIDO NO PERÍODO</p>
            <h2 style="color: #FFFFFF !important; margin: 0; font-family: 'Inter', sans-serif; font-weight: 900; font-size: 2.8rem !important; -webkit-text-stroke: 0px; text-shadow: none;">R$ {total_investido:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    # --- Organização por RA e Escola ---
    ra_list = sorted(df["RA"].unique())
    if not ra_list:
        st.info("Nenhum dado corresponde aos filtros selecionados.")
        return

    tabs_ra = st.tabs([f"📍 {ra}" for ra in ra_list])

    for i, ra in enumerate(ra_list):
        with tabs_ra[i]:
            df_ra = df[df["RA"] == ra]
            escolas = sorted(df_ra["Unidade Escolar"].unique())
            
            st.subheader(f"Total em {ra}: R$ {df_ra['Valor_Num'].sum():,.2f}")
            
            for escola in escolas:
                df_esc = df_ra[df_ra["Unidade Escolar"] == escola]
                total_esc = df_esc["Valor_Num"].sum()
                
                with st.expander(f"🏫 {escola} — R$ {total_esc:,.2f}", expanded=False):
                    for _, row in df_esc.iterrows():
                        # Layout de cada registro
                        st.markdown(f"""
                            <div style="border-bottom: 1px solid #D1D5DB; padding: 10px 0;">
                                <span style="font-weight: bold; color: #B22222;">[{row['Ano']}]</span> {row.get('Destinação', 'PDAF GERAL')} <br>
                                <span style="font-size: 1.1rem; font-weight: bold;">{row['Valor']}</span><br>
                                <small style="color: #666;">{row.get('Portaria', '')} | {row.get('Data pagamento', '')}</small>
                            </div>
                        """, unsafe_allow_html=True)

    st.divider()
    st.caption("Dados extraídos dos relatórios de execução orçamentária do PDAF.")
