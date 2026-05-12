import os
import faiss
import numpy as np
import docx2txt
from sentence_transformers import SentenceTransformer

# ---------------------------------
# Configurações (mesmas do rag.py)
# ---------------------------------
# Modelo de embedding – pode ser trocado por uma versão menor se desejar.
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"   # <- deixar assim ou substituir por modelo mais leve

# Arquivos de persistência
INDEX_FILE = "mandato_index.faiss"
TEXTS_FILE = "mandato_textos.npy"
DOC_PATH = "DADOS R.A - COMUNICAÇÃO.docx"


# ------------------------------------------------------------------------
# Função de lazy‑loading do modelo (evita download na importação)
# ------------------------------------------------------------------------
def _get_model() -> SentenceTransformer:
    """
    Retorna um objeto SentenceTransformer cacheado.
    Na primeira chamada o modelo é baixado e carregado; nas chamadas subsequentes
    o mesmo objeto já está em memória.
    """
    if not hasattr(_get_model, "model"):
        # Força uso de CPU (ou GPU se preferir mudar para "cuda")
        _get_model.model = SentenceTransformer(
            MODEL_NAME, trust_remote_code=True, device="cpu"
        )
    return _get_model.model


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

    print(f"🧠 Gerando embeddings para {len(base_texto)} fragmentos...")
    embeddings = _get_model().encode(base_texto, show_progress_bar=True)
    print("✅ Embeddings gerados. Construindo índice FAISS...")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))

    # Persiste para reutilização futura
    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)

    print("✅ Base RAG criada e persistida.")
    return index, base_texto
