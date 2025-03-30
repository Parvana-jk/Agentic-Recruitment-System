
import os
import numpy as np
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
from ollama import  Client
import pdfplumber



from dotenv import load_dotenv
load_dotenv()




############# PROCESSING RESUMES ################
# Initialize Qdrant client
qdrant_client = QdrantClient(url=os.environ.get("QDRANT_API"))
collection_name = "resumes"


client = Client(
  host=os.environ.get("OLLAMA_API"),
)

embed_model_name=os.environ.get('embed_model_name')
embed_dimensions=os.environ.get('embed_dimensions')



# Ensure the collection exists in Qdrant
def create_qdrant_collection():

    # Check if the collection exists
    if qdrant_client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' exists. Deleting and recreating it...")
        qdrant_client.delete_collection(collection_name)

    # Create the collection
    print(f"Creating collection '{collection_name}'...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embed_dimensions, distance="Cosine")
    )
    print(f"Collection '{collection_name}' created successfully!")

def normalize_vector(vec):
    return vec / np.linalg.norm(vec)


def read_docx(file_path):
    document = Document(file_path)
    text = "\n".join([para.text for para in document.paragraphs])
    print(f"Read {len(text)} characters from {file_path}")
    return text

def chunk_resume(resume_text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=0)
    chunks = text_splitter.split_text(resume_text)
    print(f"Chunked resume into {len(chunks)} parts")
    return chunks


def embed_chunks(chunks):
    embeddings = {}
    for chunk in chunks:
        if chunk.strip():  # Skip empty chunks
            response = client.embed(model=embed_model_name, input=chunk)  # Call Ollama API
            embedding = response['embeddings']  # Extract embedding vector
            embeddings[chunk] = embedding[0]  # Store embedding
        
    print(f"Generated {len(embeddings)} embeddings")
    return embeddings


def store_embeddings(embeddings, user_id, resume_text):
    points = []
    for chunk, embedding in embeddings.items():
        norm_embedding = normalize_vector(embedding).tolist()  # Convert to list for Qdrant
        points.append(
            PointStruct(
                id=user_id,
                vector=norm_embedding,
                payload={"resume_text": resume_text}  # Store resume as metadata
            )
        )
    
    # Insert into Qdrant
    qdrant_client.upsert(collection_name=collection_name, points=points)
    print(f"Stored {len(embeddings)} embeddings for user {user_id}")


def read_pdf(file_path):
    """Extract text from a PDF file using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n" if page.extract_text() else ""
    return text.strip()

def process_resumes(folder_path):
    create_qdrant_collection()  # Ensure Qdrant collection is ready
    failed_files = []

    

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(('.txt', '.docx', '.pdf')):  # Added .pdf support
            try:
                if filename.endswith('.docx'):
                    resume_text = read_docx(file_path)
                elif filename.endswith('.pdf'):
                    print("heree")
                    resume_text = read_pdf(file_path)  # Added PDF handling
                else:
                    resume_text = open(file_path, encoding='utf-8').read()
                    
                user_id = int(hashlib.sha256(filename.encode()).hexdigest(), 16) % (10**8)

                # Chunk and embed
                chunks = chunk_resume(resume_text)
                embeddings = embed_chunks(chunks)

                # Store embeddings in Qdrant
                store_embeddings(embeddings, user_id, resume_text)
                
            except Exception as e:
                print("Something failed" + str(e))
                failed_files.append(f"{filename} failed: {e}")
                raise e

    print("All resumes processed successfully.")