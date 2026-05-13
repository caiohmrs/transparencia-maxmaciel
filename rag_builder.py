import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env se existir
load_dotenv()

# ---------------------------------
# Configurações
# ---------------------------------
# Mudando para modelo local do Hugging Face para evitar quota e problemas de caracteres
MODEL_NAME = "google/embeddinggemma-300m"
INDEX_FILE = "mandato_index.faiss"
TEXTS_FILE = "mandato_textos.npy"
DOC_PATHS = ["DADOS_RA_ORGANIZADO.md", "DADOS_PDAF_CONSOLIDADO.md"]
DIMENSION = 768  # Confirmado que o embeddinggemma-300m usa 768

def _get_model():
    """
    Carrega o modelo local do Hugging Face.
    """
    token = os.getenv("HF_TOKEN")
    
    # Se não encontrar no env (local), tenta no st.secrets (Streamlit Cloud)
    if not token:
        try:
            import streamlit as st
            if "HF_TOKEN" in st.secrets:
                token = st.secrets["HF_TOKEN"]
        except:
            pass

    if not token:
        print("[AVISO] HF_TOKEN não encontrado. Se o modelo for gated, o carregamento falhará.")
    
    # Carrega o modelo via SentenceTransformers
    print(f"[INFO] Carregando modelo local {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME, use_auth_token=token)
    return model

# Cache do modelo para não recarregar toda vez
_model_cache = None

def get_encoder():
    global _model_cache
    if _model_cache is None:
        _model_cache = _get_model()
    return _model_cache

def preparar_conhecimento_ra() -> list[str]:
    textos_processados: list[str] = []

    for path in DOC_PATHS:
        if not os.path.exists(path):
            print(f"[AVISO] Arquivo {path} não encontrado. Pulando...")
            continue

        print(f"[INFO] Lendo {path}...")
        with open(path, "r", encoding="utf-8") as f:
            for linha in f:
                linha_limpa = linha.strip()
                if linha_limpa.startswith("* ["):
                    conteudo = linha_limpa.lstrip("* ").strip()
                    
                    # Extrai a RA do formato [RA] [Tema] ...
                    try:
                        ra = conteudo.split("]")[0].strip("[")
                        # Formato title/text para consistência (embora o modelo local não exija prefixos específicos da API)
                        doc_formatado = f"title: {ra} | text: {conteudo}"
                    except:
                        doc_formatado = f"title: none | text: {conteudo}"
                    
                    textos_processados.append(doc_formatado)

    print(f"[OK] {len(textos_processados)} fragmentos extraídos no total.")
    return textos_processados


def carregar_base_rag() -> tuple[faiss.Index, list[str]]:
    # Se o arquivo existe, verificamos se a dimensão bate
    if os.path.exists(INDEX_FILE) and os.path.exists(TEXTS_FILE):
        index = faiss.read_index(INDEX_FILE)
        if index.d == DIMENSION:
            base_texto = np.load(TEXTS_FILE, allow_pickle=True).tolist()
            print("[OK] Base de vetores carregada do disco.")
            return index, base_texto
        else:
            print(f"[AVISO] Dimensão do index ({index.d}) diferente da configurada ({DIMENSION}). Recriando...")

    print("[INFO] Gerando nova base RAG com modelo local (Gemma)...")
    base_texto = preparar_conhecimento_ra()
    
    model = get_encoder()

    print("[INFO] Gerando embeddings localmente (sem limite de quota)...")
    # O SentenceTransformer já lida com batching internamente, mas podemos passar tudo de uma vez
    # ou em blocos se a memória for um problema.
    embeddings_np = model.encode(
        base_texto, 
        batch_size=32, 
        show_progress_bar=True, 
        convert_to_numpy=True
    ).astype("float32")
    
    # Normalização para Inner Product (Cosine Similarity)
    faiss.normalize_L2(embeddings_np)
    
    index = faiss.IndexFlatIP(DIMENSION)
    index.add(embeddings_np)

    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)
    print("[OK] Base RAG criada e persistida com sucesso localmente.")
    return index, base_texto


if __name__ == "__main__":
    index, base_texto = carregar_base_rag()
    print(f"Total de Fragmentos: {len(base_texto)}")
    print(f"Dimensão dos Vetores: {index.d}")
