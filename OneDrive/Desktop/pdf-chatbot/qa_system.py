from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

chunks = []
index = None

def process_text(text):
    global chunks, index

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(text)

    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))


def get_answer(query):
    global index, chunks

    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), k=3)

    context = " ".join([chunks[i] for i in indices[0]])

    return context