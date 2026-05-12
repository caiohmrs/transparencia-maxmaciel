import streamlit as st
import numpy as np
from rag_builder import _get_model   # para gerar a query
from rag_chat import client          # cliente Ollama configurado
from . import get_rag                # cache de índice e textos

def _gerar_resposta(duvida: str, index, base_texto) -> str:
    """
    Usa a mesma lógica de rag_chat.responder_pergunta, porém devolve
    a resposta completa como string.
    """
    instrucao = "Represent this query for retrieving relevant documents"
    query_input = f"Instruct: {instrucao}\nQuery: {duvida}"
    query_vec = _get_model().encode([query_input])

    _, idxs = index.search(np.array(query_vec).astype("float32"), k=15)
    contexto = "\n".join([base_texto[i] for i in idxs[0]])

    prompt = f"""
Você é o Assistente Especial de Comunicação do Mandato. Sua missão é transformar dados técnicos
em respostas claras, entusiasmadas e informativas para o cidadão.

### REGRAS DE OURO:
1. EXAUSTIVIDADE – cite tudo que o contexto mencionar.
2. ORGANIZAÇÃO – estruture em tópicos (🏥 Saúde, 🎓 Educação, 🏗️ Infraestrutura…).
3. TOM – solícito, positivo e institucional.
4. DESTAQUE FINANCEIRO – valores em **NEGRITO**.
5. FIDELIDADE – use apenas o CONTEXTO abaixo; se não houver informação, diga que não localizou.

### CONTEXTO RECUPERADO:
{contexto}

### PERGUNTA DO CIDADÃO:
{duvida}

RESPOSTA ESTRUTURADA:
"""

    messages = [{"role": "user", "content": prompt}]
    resposta = ""
    for parte in client.chat(model="gpt-oss:120b", messages=messages, stream=True):
        resposta += parte["message"]["content"]
    return resposta


def page():
    st.title("💬 Converse com a IA do Mandato")
    st.write(
        "Faça perguntas ao assistente. O contexto será recuperado do nosso "
        "repositório documental e a resposta será gerada pelo modelo Ollama."
    )

    pergunta = st.text_area("Sua pergunta", height=120, key="chat_input")
    enviar = st.button("Enviar")

    if enviar and pergunta:
        index, base_texto = get_rag()   # cacheado
        with st.spinner("Processando…"):
            resposta = _gerar_resposta(pergunta, index, base_texto)

        st.markdown("**🤖 Resposta:**")
        st.write(resposta)
