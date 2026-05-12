import os
import faiss
import numpy as np
import docx2txt
from sentence_transformers import SentenceTransformer

# ---------------------------------
# Configurações (mesmas do rag.py)
# ---------------------------------
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
INDEX_FILE = "mandato_index.faiss"
TEXTS_FILE = "mandato_textos.npy"
DOC_PATH = "DADOS R.A - COMUNICAÇÃO.docx"

# Modelo de embedding – carregado uma única vez
model_embedding = SentenceTransformer(MODEL_NAME, trust_remote_code=True)


def _processar_documento() -> list[str]:
    """Lê o DOCX e devolve a lista de fragmentos já processados."""
    if not os.path.exists(DOC_PATH):
        raise FileNotFoundError(f"Arquivo {DOC_PATH} não encontrado.")

    conteudo = docx2txt.process(DOC_PATH)
    textos = []
    ra_atual = "Distrito Federal"
    cidades_alvo = [
        "Planaltina",
        "São Sebastião",
        "Sol Nascente",
        "Gama",
        "Ceilândia",
        "Arapoanga",
        "Pôr do Sol",
        "Estrutural",
        "Brazlândia",
    ]

    for linha in conteudo.split("\n"):
        linha = linha.strip()
        if not linha:
            continue

        # Detecta mudança de região
        if any(c.lower() in linha.lower() for c in cidades_alvo) and len(linha) < 45:
            ra_atual = linha
            continue

        # Apenas linhas relevantes entram como fragmento
        if len(linha) > 12:
            textos.append(f"Região: {ra_atual} | Detalhe: {linha}")

    return textos


def carregar_base_rag() -> tuple[faiss.Index, list[str]]:
    """
    Carrega (ou cria) o índice FAISS e a lista de textos.
    Retorna (index, base_texto).
    """
    # 1️⃣ Caso já exista no disco, carrega
    if os.path.exists(INDEX_FILE) and os.path.exists(TEXTS_FILE):
        index = faiss.read_index(INDEX_FILE)
        base_texto = np.load(TEXTS_FILE, allow_pickle=True).tolist()
        print("✅ Base RAG carregada a partir de arquivos persistidos.")
        return index, base_texto

    # 2️⃣ Caso contrário, gera a base a partir do DOCX
    print("✨ Gerando nova base RAG...")
    base_texto = _processar_documento()
    embeddings = model_embedding.encode(base_texto, show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))

    # Persiste para reutilização futura
    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)

    print("✅ Base RAG criada e persistida.")
    return index, base_texto
