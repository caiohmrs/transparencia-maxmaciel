import pandas as pd
import os

# ---------------------------------
# Configurações
# ---------------------------------
CSV_FILES = {
    "2023": {"path": "PDAF2023.csv", "sep": ";"},
    "2024": {"path": "PDAF2024.csv", "sep": ";"},
    "2025": {"path": "PDAF2025.csv", "sep": ","}
}

OUTPUT_MD = "DADOS_PDAF_CONSOLIDADO.md"

def normalizar_ra(cre_text):
    """
    Limpa o texto da CRE para deixar apenas o nome da RA.
    Ex: "CRE CEILÂNDIA" -> "Ceilândia"
    """
    if pd.isna(cre_text):
        return "Desconhecido"
    
    ra = str(cre_text).replace("CRE ", "").replace("CRE'NDIA", "CEILÂNDIA").strip().title()
    # Correções específicas de encoding ou erros comuns nos CSVs
    ra = ra.replace("Ceilndia", "Ceilândia").replace("Ceil'Ndia", "Ceilândia")
    return ra

def processar_csvs():
    consolidado = []
    
    print("[INFO] Iniciando processamento dos CSVs de PDAF...")
    
    for ano, config in CSV_FILES.items():
        if not os.path.exists(config["path"]):
            print(f"[AVISO] Arquivo {config['path']} não encontrado. Pulando...")
            continue
            
        print(f"[INFO] Lendo {config['path']}...")
        df = pd.read_csv(config["path"], sep=config["sep"], encoding="utf-8")
        
        # Padronização de colunas
        if ano == "2023":
            # Ofício;Destinação;Programa de Trabalho;CRE;Unidade Escolar;Total;Portaria;DODF;Processo de Pagamento;Data pagamento
            df = df.rename(columns={"Total": "Valor"})
        elif ano == "2024":
            # Ofício;Destinação;Programa de Trabalho;CRE;Unidade Escolar;Valor;Portaria;DODF;Processo de Pagamento;Data pagamento
            pass
        elif ano == "2025":
            # Unidade Escolar,CRE,Valor,Destinação,Data pagamento
            pass
            
        for _, row in df.iterrows():
            ra = normalizar_ra(row.get("CRE", "Desconhecido"))
            escola = str(row.get("Unidade Escolar", "Unidade Geral")).strip().upper()
            valor = str(row.get("Valor", "Não informado")).strip()
            destinacao = str(row.get("Destinação", "Não informado")).strip()
            data = str(row.get("Data pagamento", "Pendente")).strip()
            
            # Detalhes extras se houver (Portaria, DODF)
            extra = ""
            if "Portaria" in df.columns and pd.notna(row["Portaria"]):
                extra += f" via {row['Portaria']}"
            if "DODF" in df.columns and pd.notna(row["DODF"]):
                extra += f" ({row['DODF']})"
            
            # Criar a linha formatada para o RAG
            # Formato: * [RA] [Educação/PDAF] [Ano] Descrição
            linha = f"* [{ra}] [Educação/PDAF] [{ano}] {escola}: Investimento de **{valor}** para {destinacao}. Pagamento: {data}.{extra}"
            consolidado.append(linha)

    print(f"[OK] {len(consolidado)} registros processados.")
    
    # Salvar o Markdown
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# Consolidado de Investimentos PDAF (2023-2025)\n\n")
        # Agrupar por RA para ficar organizado visualmente
        # Mas o RAG lerá cada linha individualmente
        f.write("\n".join(consolidado))
        
    print(f"[SUCESSO] Arquivo {OUTPUT_MD} gerado.")

if __name__ == "__main__":
    processar_csvs()
