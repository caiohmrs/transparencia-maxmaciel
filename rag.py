import os
import faiss
import numpy as np
import docx2txt
from ollama import Client
from sentence_transformers import SentenceTransformer

# --- CONFIGURAÇÕES ---
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
INDEX_FILE = "mandato_index.faiss"
TEXTS_FILE = "mandato_textos.npy"
DOC_PATH = "DADOS R.A - COMUNICAÇÃO.docx"

# Configuração do Cliente Ollama Cloud
client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY', '91873b17f533488fa3b62007d2955db7.vaT1FcSBOlXolWjmrvt80SyS')}
)

print("--- Sistema Híbrido: Qwen3 (Local) + Ollama Streaming (Cloud) ---")

# 1. CARREGAR MODELO DE EMBEDDING LOCAL
model_embedding = SentenceTransformer(MODEL_NAME, trust_remote_code=True)


def preparar_conhecimento_ra():
    if not os.path.exists(DOC_PATH):
        print(f"❌ Erro: Arquivo {DOC_PATH} não encontrado!")
        return []

    print(f"📖 Processando documento...")
    conteudo_docx = docx2txt.process(DOC_PATH)
    textos_processados = []
    ra_atual = "Distrito Federal"
    cidades_alvo = ["Planaltina", "São Sebastião", "Sol Nascente", "Gama", "Ceilândia", "Arapoanga", "Pôr do Sol",
                    "Estrutural", "Brazlândia"]

    for linha in conteudo_docx.split('\n'):
        linha_limpa = linha.strip()
        if not linha_limpa: continue
        if any(cidade.lower() in linha_limpa.lower() for cidade in cidades_alvo) and len(linha_limpa) < 45:
            ra_atual = linha_limpa
            continue
        if len(linha_limpa) > 12:
            textos_processados.append(f"Região: {ra_atual} | Detalhe: {linha_limpa}")
    return textos_processados


# LÓGICA DE PERSISTÊNCIA
if os.path.exists(INDEX_FILE) and os.path.exists(TEXTS_FILE):
    index = faiss.read_index(INDEX_FILE)
    base_texto = np.load(TEXTS_FILE, allow_pickle=True).tolist()
    print("✅ Base de vetores carregada.")
else:
    print("✨ Gerando nova base otimizada...")
    base_texto = preparar_conhecimento_ra()
    embeddings = model_embedding.encode(base_texto, show_progress_bar=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype('float32'))
    faiss.write_index(index, INDEX_FILE)
    np.save(TEXTS_FILE, base_texto)


# 2. MOTOR DE RESPOSTA (AJUSTADO COM O SEU PROMPT)
def responder_pergunta(duvida):
    # 1. Busca Local com Qwen3 (Usando os 10 fragmentos mais relevantes como você pediu)
    instrucao = "Represent this query for retrieving relevant documents"
    query_input = f"Instruct: {instrucao}\nQuery: {duvida}"
    query_vector = model_embedding.encode([query_input])

    _, indices = index.search(np.array(query_vector).astype('float32'), k=10)
    contexto = "\n".join([base_texto[idx] for idx in indices[0]])

    # 2. Monta o prompt completo seguindo exatamente o seu formato
    prompt_completo = f"""
    Use o contexto abaixo para responder à pergunta de forma completa.
    Liste todas as ações mencionadas que forem relevantes.

    CONTEXTO:
    {contexto}

    PERGUNTA:
    {duvida}
    """

    messages = [
        {
            'role': 'user',
            'content': prompt_completo,
        },
    ]

    print("\n🤖 Resposta do Mandato:\n" + "-" * 30)

    # Chamada com Stream no modelo gpt-oss:120b
    for part in client.chat(model='gpt-oss:120b', messages=messages, stream=True):
        print(part['message']['content'], end='', flush=True)
    print("\n" + "-" * 30)


if __name__ == "__main__":
    p = input("\nO que deseja saber sobre o mandato? ")
    responder_pergunta(p)