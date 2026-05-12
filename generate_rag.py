#!/usr/bin/env python
"""
python generate_rag.py

1️⃣ Gera/atualiza mandato_index.faiss e mandato_textos.npy
2️⃣ (Opcional) faz git add + commit desses arquivos
"""

import subprocess
import sys
from pathlib import Path

# Funções principais do rag_builder
from rag_builder import carregar_base_rag, INDEX_FILE, TEXTS_FILE


def gerar():
    """Executa a criação/recuperação do índice."""
    index, base_texto = carregar_base_rag()

    # Verifica se os artefatos realmente foram gravados
    if not (Path(INDEX_FILE).exists() and Path(TEXTS_FILE).exists()):
        sys.exit("❌ Falha ao gravar os arquivos de índice.")
    print("\n✅ Artefatos gerados:")
    print(f"   • {INDEX_FILE} → {Path(INDEX_FILE).stat().st_size/1e6:.1f} MB")
    print(f"   • {TEXTS_FILE} → {Path(TEXTS_FILE).stat().st_size/1e6:.1f} MB")


def commit():
    """Adiciona e commita os arquivos gerados."""
    subprocess.run(["git", "add", INDEX_FILE, TEXTS_FILE], check=True)
    mensagem = "🗂️ Atualiza índice RAG + textos (gerado automaticamente)"
    subprocess.run(["git", "commit", "-m", mensagem], check=True)
    print("✅ Commit realizado.")


if __name__ == "__main__":
    gerar()
    resp = input("\nDeseja commitar os arquivos gerados? [y/N] ")
    if resp.lower() == "y":
        commit()
