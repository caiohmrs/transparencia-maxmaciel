import os
import numpy as np
import faiss
from ollama import Client
from rag_builder import carregar_base_rag, _get_model

# -------------------------------------------------
# Configurações de cliente Ollama (mantém as mesmas)
# -------------------------------------------------
client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer "
        + os.environ.get(
            "OLLAMA_API_KEY",
            "91873b17f533488fa3b62007d2955db7.vaT1FcSBOlXolWjmrvt80SyS",
        )
    },
)


def responder_pergunta(
    duvida: str, index: faiss.Index, base_texto: list[str]
) -> None:
    """
    Busca os fragmentos mais relevantes no índice e devolve a resposta da IA.
    """
    # --------- Busca local ----------
    instrucao = "Represent this query for retrieving relevant documents"
    query_input = f"Instruct: {instrucao}\nQuery: {duvida}"
    query_vector = _get_model().encode([query_input])

    _, indices = index.search(np.array(query_vector).astype("float32"), k=10)
    contexto = "\n".join([base_texto[i] for i in indices[0]])

    # --------- Prompt para Ollama ----------
    prompt = f"""
    Use o contexto abaixo para responder à pergunta de forma completa.
    Liste todas as ações mencionadas que forem relevantes.

    CONTEXTO:
    {contexto}

    PERGUNTA:
    {duvida}
    """

    messages = [{"role": "user", "content": prompt}]

    print("\n🤖 Resposta do Mandato:\n" + "-" * 30)

    # Streaming (mesma lógica do arquivo original)
    for parte in client.chat(model="gpt-oss:120b", messages=messages, stream=True):
        print(parte["message"]["content"], end="", flush=True)

    print("\n" + "-" * 30)


def main() -> None:
    """Entrada interativa – carrega a base e entra em loop de perguntas."""
    index, base_texto = carregar_base_rag()

    while True:
        p = input("\nO que deseja saber sobre o mandato? (ou 'sair' para encerrar) ").strip()
        if not p or p.lower() == "sair":
            break
        responder_pergunta(p, index, base_texto)


if __name__ == "__main__":
    main()
