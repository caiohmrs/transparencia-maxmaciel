import os
import faiss
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env se existir
load_dotenv()

# ---------------------------------
# Configurações
# ---------------------------------
MODEL_NAME = "gemini-embedding-2"
INDEX_FILE = "mandato_index.faiss"
TEXTS_FILE = "mandato_textos.npy"
DOC_PATH = "DADOS_RA_ORGANIZADO.md"
DIMENSION = 768  # Usando 768 para eficiência (Matryoshka)

# Inicialização do Cliente Gemini
def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada no .env ou st.secrets")
    
    return genai.Client(api_key=api_key)

client_genai = _get_client()

def _get_model():
    """
    Mantido para compatibilidade com rag_chat.py.
    Retorna um objeto com método encode para simular o comportamento do SentenceTransformer.
    """
    class GeminiEncoder:
        def encode(self, texts: list[str]) -> np.ndarray:
            # Para consultas (queries), usamos o formato de query
            formatted_texts = []
            for t in texts:
                if "Query:" in t:
                    query_content = t.split("Query:")[1].strip()
                    formatted_texts.append(f"task: search result | query: {query_content}")
                else:
                    formatted_texts.append(t)

            # Para garantir embeddings separados para cada item na lista (se houver mais de um)
            # usamos a estrutura de Content objects
            contents = [types.Content(parts=[types.Part.from_text(text=t)]) for t in formatted_texts]

            response = client_genai.models.embed_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.EmbedContentConfig(output_dimensionality=DIMENSION)
            )
            return np.array([e.values for e in response.embeddings]).astype("float32")

    return GeminiEncoder()


def preparar_conhecimento_ra() -> list[str]:
    if not os.path.exists(DOC_PATH):
        raise FileNotFoundError(f"Arquivo {DOC_PATH} não encontrado.")

    print("[INFO] Lendo Markdown otimizado...")
    textos_processados: list[str] = []

    with open(DOC_PATH, "r", encoding="utf-8") as f:
        for linha in f:
            linha_limpa = linha.strip()
            if linha_limpa.startswith("* ["):
                conteudo = linha_limpa.lstrip("* ").strip()
                
                # Extrai a RA do formato [RA] [Tema] ...
                try:
                    ra = conteudo.split("]")[0].strip("[")
                    doc_formatado = f"title: {ra} | text: {conteudo}"
                except:
                    doc_formatado = f"title: none | text: {conteudo}"
                
                textos_processados.append(doc_formatado)

    print(f"[OK] {len(textos_processados)} fragmentos extraídos com sucesso.")
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

    print("[INFO] Gerando nova base RAG com Gemini...")
    base_texto = preparar_conhecimento_ra()

    print("[INFO] Gerando embeddings (isso pode levar alguns segundos)...")
    all_embeddings = []
    batch_size = 50
    for i in range(0, len(base_texto), batch_size):
        batch = base_texto[i:i + batch_size]
        
        # IMPORTANTE: No gemini-embedding-2, passar uma lista de strings resulta em AGREGAÇÃO.
        # Para obter embeddings separados, devemos passar Content objects.
        contents = [types.Content(parts=[types.Part.from_text(text=t)]) for t in batch]
        
        response = client_genai.models.embed_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.EmbedContentConfig(output_dimensionality=DIMENSION)
        )
        all_embeddings.extend([e.values for e in response.embeddings])

    embeddings_np = np.array(all_embeddings).astype("float32")
    
    # Normalização para Inner Product
    faiss.normalize_L2(embeddings_np)
    
    index = faiss.IndexFlatIP(DIMENSION)
    index.add(embeddings_np)

    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)
    print("[OK] Base RAG criada e persistida com sucesso.")
    return index, base_texto


if __name__ == "__main__":
    index, base_texto = carregar_base_rag()
    print(f"Total de Fragmentos: {len(base_texto)}")
    print(f"Dimensão dos Vetores: {index.d}")
