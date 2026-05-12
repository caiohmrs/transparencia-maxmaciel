import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------
# Configurações
# ---------------------------------
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
INDEX_FILE = "mandato_index.faiss"
TEXTS_FILE = "mandato_textos.npy"

# Usar o arquivo Markdown que já está formatado para RAG
DOC_PATH = "DADOS_RA_ORGANIZADO.md"

# Modelo de embedding
model_embedding = SentenceTransformer(
    MODEL_NAME, trust_remote_code=True, device="cpu"
)

# Adicione isso no rag_builder.py
def _get_model() -> SentenceTransformer:
    """
    Retorna o modelo de embedding já carregado para ser usado no chat.
    """
    return model_embedding


def preparar_conhecimento_ra() -> list[str]:
    if not os.path.exists(DOC_PATH):
        raise FileNotFoundError(f"Arquivo {DOC_PATH} não encontrado.")

    print("[INFO] Lendo Markdown otimizado...")

    textos_processados: list[str] = []

    with open(DOC_PATH, "r", encoding="utf-8") as f:
        for linha in f:
            linha_limpa = linha.strip()

            # Captura apenas as linhas de conteúdo (que começam com o marcador de lista do Markdown)
            if linha_limpa.startswith("* ["):
                # Remove o '*' inicial e limpa espaços
                conteudo = linha_limpa.lstrip("* ").strip()
                # O formato já é "[RA] [Tema] Detalhe", perfeito para o Embedder
                textos_processados.append(conteudo)

    print(f"[OK] {len(textos_processados)} fragmentos extraídos com sucesso.")
    return textos_processados


def carregar_base_rag() -> tuple[faiss.Index, list[str]]:
    if os.path.exists(INDEX_FILE) and os.path.exists(TEXTS_FILE):
        index = faiss.read_index(INDEX_FILE)
        base_texto = np.load(TEXTS_FILE, allow_pickle=True).tolist()
        print("[OK] Base de vetores carregada do disco.")
        return index, base_texto

    print("[INFO] Gerando nova base RAG...")
    base_texto = preparar_conhecimento_ra()

    print("[INFO] Gerando embeddings...")
    embeddings = model_embedding.encode(base_texto, show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))

    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)
    print("[OK] Base RAG criada e persistida.")
    return index, base_texto


if __name__ == "__main__":
    index, base_texto = carregar_base_rag()
    print(f"Total de Fragmentos: {len(base_texto)}")
