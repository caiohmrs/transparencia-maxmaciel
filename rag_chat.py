import streamlit as st
import numpy as np
import faiss
from ollama import Client
from typing import Generator
from dotenv import load_dotenv
import os

# Carrega .env para uso local (caso não esteja no Streamlit Cloud)
load_dotenv()

# Importamos o carregador e o helper do modelo que definimos no rag_builder
from rag_builder import carregar_base_rag, get_encoder

# ---------------------------------
# Configurações de cliente Ollama
# ---------------------------------
# Busca a chave no st.secrets (padrão Streamlit) ou no .env
OLLAMA_KEY = os.getenv("OLLAMA_API_KEY")
if not OLLAMA_KEY:
    try:
        OLLAMA_KEY = st.secrets["OLLAMA_API_KEY"]
    except:
        OLLAMA_KEY = ""

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {OLLAMA_KEY}"
    },
)

# Configurações globais
MODEL_LLM = "gemma4:31b-cloud"


def limpar_query(duvida: str) -> str:
    """
    Remove palavras-chave que podem enviesar a busca vetorial (ex: nome do deputado).
    """
    termos_para_remover = ["max", "maciel", "deputado", "mandato"]
    query_limpa = duvida.lower()
    for termo in termos_para_remover:
        query_limpa = query_limpa.replace(termo, "")
    return query_limpa.strip()


def obter_contexto(duvida: str, index: faiss.Index, base_texto: list[str], k: int = 15) -> str:
    """
    Realiza a busca semântica e retorna o contexto formatado.
    """
    # Limpamos a query para focar no assunto/localidade
    query_para_busca = limpar_query(duvida)
    
    # Adaptado para o novo GeminiEncoder no rag_builder.py
    # O prefixo 'Query:' ativa a formatação de tarefa no encoder
    query_input = f"Query: {query_para_busca}"

    model = get_encoder()
    query_vector = model.encode([query_input])

    # Busca os k fragmentos mais próximos
    _, indices = index.search(np.array(query_vector).astype("float32"), k=k)

    # Monta o contexto
    contexto_recuperado = "\n".join([base_texto[i] for i in indices[0]])
    return contexto_recuperado


def gerar_resposta_streaming(
    duvida: str, index: faiss.Index, base_texto: list[str]
) -> Generator[str, None, None]:
    """
    Gerador que encapsula a lógica de RAG e streaming do Ollama.
    """
    contexto = obter_contexto(duvida, index, base_texto)
    
    prompt = f"""
    Você é um Auditor de Dados Parlamentares. Sua prioridade absoluta é a precisão geográfica. Você prefere dizer que não sabe a dar uma resposta de uma cidade errada.

    ### CONTEXTO IMPORTANTE:
    Toda a base de dados abaixo refere-se EXCLUSIVAMENTE a ações, obras e investimentos do mandato do deputado **Max Maciel**. Se a informação está no contexto, ela é de autoria dele.

    ### REGRAS DE OURO DE VALIDAÇÃO:
    1. **FILTRO DE LOCALIDADE ESTREITO:** Analise a PERGUNTA e o CONTEXTO. Se o usuário perguntou sobre uma cidade (ex: Guará) e o contexto fala de outra (ex: Ceilândia), você NÃO deve responder com os dados da outra, mesmo que os nomes sejam parecidos.
    2. **VERIFICAÇÃO DE "MATCH":** Antes de escrever qualquer item, confirme se ele está listado abaixo do título da Região Administrativa correta no contexto.
    3. **EXAUSTIVIDADE LITERAL:** Se a cidade for a correta, liste todos os itens individualmente (escolas, praças, obras). Não agrupe nem resuma. 
    4. **DESTAQUE FINANCEIRO:** Valores (R$) e "Emendas" devem estar em **NEGRITO**.

    ### FORMATO DE RESPOSTA:
    **[NOME DA REGIÃO ADMINISTRATIVA]**
    * [CATEGORIA]
        * [Ação detalhada exatamente como no texto]
        * **Investimento:** [Valor se houver]

    ---
    ### CONTEXTO RECUPERADO PARA ANÁLISE:
    {contexto}

    ### PERGUNTA DO CIDADÃO:
    {duvida}

    RESPOSTA DO AUDITOR:
    """

    messages = [{"role": "user", "content": prompt}]

    try:
        for parte in client.chat(model=MODEL_LLM, messages=messages, stream=True):
            yield parte["message"]["content"]
    except Exception as e:
        yield f"\n❌ Erro na comunicação com a IA: {e}"


def responder_pergunta(
    duvida: str, index: faiss.Index, base_texto: list[str]
) -> None:
    """
    Versão para terminal (CLI) da resposta.
    """
    print("\n[AI] Resposta do Mandato:\n" + "-" * 30)
    for fragmento in gerar_resposta_streaming(duvida, index, base_texto):
        print(fragmento, end="", flush=True)
    print("\n" + "-" * 30)


def main() -> None:
    index, base_texto = carregar_base_rag()
    print("[INFO] Sistema RAG Mandato Ativo! (Digite 'sair' para encerrar)")

    while True:
        p = input("\nO que deseja saber sobre as ações do mandato? ").strip()
        if not p or p.lower() == "sair":
            print("Encerrando... Até logo!")
            break
        responder_pergunta(p, index, base_texto)


if __name__ == "__main__":
    main()
