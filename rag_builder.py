import os
import faiss
import numpy as np
import docx2txt
from ollama import Client  # Mantido para compatibilidade futura, embora não seja usado aqui
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
# Modelo de embedding – carregado uma única vez (comportamento da versão original)
# ------------------------------------------------------------------------
model_embedding = SentenceTransformer(
    MODEL_NAME, trust_remote_code=True, device="cpu"
)

# Função helper mantida apenas para compatibilidade com `rag_chat.py`
def _get_model() -> SentenceTransformer:   # pragma: no cover
    """
    Retorna o modelo de embedding já carregado.
    Mantém a assinatura original para que outros módulos possam importar.
    """
    return model_embedding


def preparar_conhecimento_ra() -> list[str]:
    """
    Processa o documento DOCX e devolve a lista de fragmentos de conhecimento
    (mesmo que a implementação original). Levanta FileNotFoundError se o
    arquivo não for encontrado.
    """
    if not os.path.exists(DOC_PATH):
        raise FileNotFoundError(f"Arquivo {DOC_PATH} não encontrado.")

    print("📖 Processando documento...")
    conteudo_docx = docx2txt.process(DOC_PATH)

    textos_processados: list[str] = []
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

    for linha in conteudo_docx.split("\n"):
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue

        # Detecta mudança de região (mesmo critério da versão original)
        if any(c.lower() in linha_limpa.lower() for c in cidades_alvo) and len(linha_limpa) < 45:
            ra_atual = linha_limpa
            continue

        # Linhas relevantes são transformadas em fragmentos
        if len(linha_limpa) > 12:
            textos_processados.append(f"Região: {ra_atual} | Detalhe: {linha_limpa}")

    return textos_processados


def carregar_base_rag() -> tuple[faiss.Index, list[str]]:
    """
    Carrega (ou cria) o índice FAISS e a lista de textos exatamente como a
    implementação original fazia, incluindo persistência em disco.
    Retorna um tuple (index, base_texto).
    """
    # -------------------------------------------------
    # 1️⃣ Verifica se já há artefatos persistidos
    # -------------------------------------------------
    if os.path.exists(INDEX_FILE) and os.path.exists(TEXTS_FILE):
        index = faiss.read_index(INDEX_FILE)
        base_texto = np.load(TEXTS_FILE, allow_pickle=True).tolist()
        print("✅ Base de vetores carregada a partir de arquivos persistidos.")
        return index, base_texto

    # -------------------------------------------------
    # 2️⃣ Caso contrário, gera tudo do zero
    # -------------------------------------------------
    print("✨ Gerando nova base otimizada...")
    base_texto = preparar_conhecimento_ra()

    # Gera os embeddings usando o modelo já carregado
    print(f"🧠 Gerando embeddings para {len(base_texto)} fragmentos...")
    embeddings = model_embedding.encode(base_texto, show_progress_bar=True)
    print("✅ Embeddings gerados. Construindo índice FAISS...")

    # Cria o índice plano L2 (mesmo tipo da versão original)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))

    # Persiste ambos para reutilização futura
    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)
    print("✅ Base RAG criada e persistida.")
    return index, base_texto
