import os
import pytest

# Garante que a variável de ambiente esteja definida para evitar falhas ao importar rag.py
os.environ["OLLAMA_API_KEY"] = "test_key"

from rag import preparar_conhecimento_ra, DOC_PATH

def test_preparar_conhecimento_ra_existe_arquivo(monkeypatch):
    # Simula a existência do DOC_PATH e o conteúdo retornado por docx2txt.process
    dummy_content = "Planaltina\nDetalhe da região A\nDetalhe da região B\n"
    monkeypatch.setattr("os.path.exists", lambda path: True if path == DOC_PATH else False)
    monkeypatch.setattr("docx2txt.process", lambda _: dummy_content)

    textos = preparar_conhecimento_ra()
    assert isinstance(textos, list)
    # Deve conter ao menos duas linhas processadas (excluindo a linha de cabeçalho)
    assert len(textos) >= 2
    assert all("Região:" in t and "Detalhe:" in t for t in textos)
