import streamlit as st
from rag_chat import gerar_resposta_streaming
from . import get_rag

def page():
    st.title("💬 MAX.IA - O Assistente do Mandato")
    st.write(
        "Eu sou a **MAX.IA**, seu assistente virtual para tudo sobre as ações do mandato. "
        "O contexto será recuperado do nosso repositório documental oficial."
    )

    # Inicializa o histórico de mensagens se não existir
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe as mensagens do histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="max.png" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

    # Input do usuário
    if prompt := st.chat_input("O que deseja saber sobre as ações do mandato?"):
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Exibe a mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)

        # Resposta do assistente
        with st.chat_message("assistant", avatar="max.png"):
            index, base_texto = get_rag()
            
            # Placeholder para o streaming
            response_placeholder = st.empty()
            full_response = ""
            
            # Gera a resposta usando a lógica unificada
            for fragmento in gerar_resposta_streaming(prompt, index, base_texto):
                full_response += fragmento
                response_placeholder.markdown(full_response + "▌")
            
            # Finaliza a exibição
            response_placeholder.markdown(full_response)
        
        # Adiciona a resposta completa ao histórico
        st.session_state.messages.append({"role": "assistant", "content": full_response})
