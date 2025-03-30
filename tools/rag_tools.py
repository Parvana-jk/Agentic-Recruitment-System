from crewai.tools import tool
import os
import shutil
import numpy as np
from ollama import  Client
from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams
from typing import List
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), ".env"))

client = Client(
  host=os.environ.get("OLLAMA_API"),
)

# Initialize Qdrant client
qdrant_client = QdrantClient(url=os.environ.get("QDRANT_API"))
embed_model_name=os.environ.get('embed_model_name')

def normalize_vector(vec):
    return vec / np.linalg.norm(vec)

def check_role_match(resume_text, role):
    """
    Uses LLM to check if a resume mentions the given role.
    Returns 'Yes' or 'No'.
    """
    try:
        print("Checking role match for:", role)
        # ## Experiments with different Prompts
        # response = client.chat(model="llama3.1", messages=[
        #     {"role": "system", "content": "Does this resume mention the role or similar roles? Reply 'Yes' or 'No'. DON'T GIVE ANY EXTRA TEXT OTHER THAN 'Yes' or 'No'"},
        #     {"role": "user", "content": f"Resume: {resume_text}\nRole: {role}"}
        # ])
        # response = client.chat(model="llama3.1", messages=[
        #     {"role": "system", "content": "You are a technical recruiter . You know the difference between developers in different fields like Front end developer is not same as backend developer , or Java backend developer is not same as python backend developer , look for entire role matches  .Classify the given resume into the following categories : \n '1' : if the candidate has required number of years of  experience and  the role required is his most recent role (if you don't know don't assume role is match). \n '2':only if the candidate has required number of years of experience in relevant role, but the role required is not the last role he worked in \n '3': if the candidate works and has worked in a different role. Return only '1' ,'2' or '3' and no other extra text."},
        #     {"role": "user", "content": f"Resume: {resume_text}\nRole: {role}"}
        # ])

        ## Best prompt
        response = client.chat(model="llama3.1", messages=[
            {"role": "system", "content": "You are a technical recruiter . You know the difference between developers in different fields like Front end developer is not same as backend developer , or Java backend developer is not same as python backend developer , look for entire role matches  .Based on the resume's role and job description's role judge if the candidate is a perfect fit by telling 'yes' :only if the candidate most recent role is the role required and has enough number of years of experience. Role is important.  (if you don't know don't assume role is match). Choose this category only for strong perfect matches. Doubtful or transitionable are not strong match. Don't make blunders like classifying candidate of a different role as fit for required role based on doubts. \n Other wise respond with 'no' , Remember you are a strict evaluator of correctness and will be given heavy penalty if you give Resume's of candidates with different roles as strong match. Response should be like : Fit:'yes/no' Explanation:"},
            {"role": "user", "content": f"Resume: {resume_text}\nRole: {role}"}
        ])

        match = response.message.content.strip()
        print("LLM Response:", match)
        return match  # Will be "Yes" or "No"
    except Exception as e:
        print("Error in check_role_match:", e)
        return "4"  # Default to "No" if error occurs


def get_query_embedding(query):
    """Generate embedding for the query using Ollama."""
    response = client.embed(model=embed_model_name, input=query)  # Generate embedding
    return np.array(response['embeddings'][0], dtype=np.float32)  # Convert to NumPy array

def rag_search(query, job_role, top_n=5):
    # Collection name in Qdrant
    collection_name = "resumes"

    query_embedding = normalize_vector(get_query_embedding(query))

    # Perform a vector search in Qdrant
    search_results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=50,  # Number of results to fetch
        search_params=SearchParams(
            hnsw_ef=256,  # Optional: Control the search precision (tune based on your dataset size)
        )
    )

    user_scores = {}
    user_chunk_counts = {}

    # Process search results
    for result in search_results:
        user_id = result.id
        score = result.score

        user_scores[user_id] = user_scores.get(user_id, 0) + score
        user_chunk_counts[user_id] = user_chunk_counts.get(user_id, 0) + 1

    for user_id in user_scores:
        # Fetch resume text from Qdrant metadata
        resume_text = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[user_id]
        )[0].payload.get("resume_text", "")

        if not resume_text:
            print(f"Warning: Resume not found for user_id {user_id}")
            continue

        # Check role relevance
        role_match = check_role_match(resume_text, job_role)

        # Normalize score by chunk count
        user_scores[user_id] /= user_chunk_counts[user_id]

        # Boost score if role matches
        ## experiments with differnt rewards
        # if "yes" in role_match:
        #      user_scores[user_id] += 0.1

        ## Best reward setup
        if "yes" in role_match:
             user_scores[user_id] += 0.15
        elif "no" in role_match:
            user_scores[user_id] -= 0.1

    # Rank candidates by score
    ranked_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    # Fetch top N resumes
    top_resumes = []
    for user_id, _ in ranked_users[:top_n]:
        resume_text = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[user_id]
        )[0].payload.get("resume_text", "")
        if resume_text:
            top_resumes.append(resume_text)

    print(len(top_resumes))


    # Define the folder name
    folder_name = "top_resumes"
    cwd = os.getcwd()  # Get the current working directory
    folder_path = os.path.join(cwd, folder_name)

    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    if os.listdir(folder_path):
        print(f"Folder '{folder_name}' already exists. Clearing old files...")
        # Remove all files in the folder
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or symbolic link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directory
        print(f"Folder '{folder_name}' has been cleared.")
    
    
    # Save the resumes
    for user_id, resume_text in zip([user_id for user_id, _ in ranked_users[:top_n]], top_resumes):
        file_path = os.path.join(folder_path, f"resume_{user_id}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(resume_text)

    print(f"Top {top_n} resumes saved in {folder_path}")

    # print("Top RAG search results:", '\n\n'.join(top_resumes))
    # return top_resumes  # Returns the resume contents
    return folder_name


@tool('Find top candidates matching job profile')
def query_candidate_resumes(job_role:str, job_profile:str, top_n:int = 5) -> List[str]:
    """Gets the top matching candidates that match highly with the required job profile
       Needs the job_role name and the full job_profile 
       top_n parameter controls the number of candidates retrieved

       Return : the folder name where the resumes are stored
    """
    job_role = rag_search(job_profile, job_role, top_n)
    return job_role