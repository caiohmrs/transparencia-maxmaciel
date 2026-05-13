import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
client = genai.Client()
MODEL_NAME = "gemini-embedding-2"

texts = [
    "title: Ceilândia | text: [Ceilândia] [Educação] CED 16: Biblioteca.",
    "title: Planaltina | text: [Planaltina / Arapoanga] [Educação] CEM 01: Troca do piso da escola."
]

query = "task: search result | query: Ceilândia"

response_docs = client.models.embed_content(
    model=MODEL_NAME,
    contents=texts,
    config=types.EmbedContentConfig(output_dimensionality=768)
)

response_query = client.models.embed_content(
    model=MODEL_NAME,
    contents=[query],
    config=types.EmbedContentConfig(output_dimensionality=768)
)

vec_docs = np.array([e.values for e in response_docs.embeddings])
vec_query = np.array([e.values for e in response_query.embeddings])

sims = cosine_similarity(vec_query, vec_docs)
print(f"Similarities: {sims}")
