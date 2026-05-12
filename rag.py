"""
Wrapper legacy para manter compatibilidade.
Executa a mesma lógica que antes, delegando ao módulo rag_chat.
"""

from rag_chat import main as iniciar_chat

if __name__ == "__main__":
    iniciar_chat()
