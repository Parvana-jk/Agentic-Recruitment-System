# Agentic AI for HR Resume Shortlisting

## Overview
This project is an end-to-end Agentic AI solution designed for HR resume shortlisting. It automates the process of:
- Parsing and processing candidate resumes.
- Matching candidates to job profiles with high accuracy and explainability.
- Selecting the best interviewers for each candidate.
- Checking interviewer schedules.
- Finding optimal interview slots.
- Generating draft email invitations for interview scheduling.

## Project Structure
The repository is well-organized, containing all necessary components for smooth execution. Below are the key folders and files:

  - `.env` - Environment variables required for execution.
  - `config/` - Contains the agents and tasks YAML files that has the base prompts 
  - `data/` - Stores input data, including:
    - `resumes/` - A folder containing candidate resumes in Word/PDF/Text format
    - `interviewers.json` - A JSON file with interviewer details.
  - `tools/` - Contains the custom tools created for this project
    - `interview_tools.py` - contains custom tools that can query the interviewers.json
    - `rag_tools.py` - custom tools that can connect and query with the vector DB and execute RAG queries
    - `resume_extract_tools.py` - contain tools that can extract key structured information from resumes
    - `email_sending_tool.py` - (unused) Tool that can trigger gmail-based emails to candidates
    
  - `agents.py` - The agent config file. Contains definitions of each agent, their tools and their execution options
  - `tasks.py` - The task config file. Contains definitions of each task, their contexts, agents and their execution options
  - `embed_resumes.py` - Contains the logic to read resumes (PDF, word, text), create chunks, generate embeddings and store them into Qdrant vector DB
  - `launch_simple.py` - The main module to launch the tool. Contains the core CrewAI definition along with fully working Streamlit demo 
  - `requirements.txt` - contains all the prerequisites for running this code
  - `Dockerfile` - contains the Dockerfile configuration for running the Streamlit demo
  - `docker-compose.yaml` - main docker-compose file to launch the complete demo (qdrant, streamlit, ollama)
    - `ollama.sh` - custom instructions for the ollama container to load the Llama3.1 model and the nomic embedding model

## Prerequisites
Ensure you have the following installed:
- `Podman` or `Docker`
- `Python 3.x`
- `pip`
- `ollama` (Get from [here](https://ollama.com/download))


## Data Setup
Place your data in the `data/` folder:
- Candidate resumes should be stored in `data/resumes/`.
- Interviewer details should be provided in `data/interviewers.json` in the following format:
  
  ```json
  [
    {
      "id": 1,
      "name": "John Doe",
      "role": "Java Developer",
      "skills": [
        "Java",
        "Spring Boot",
        "Microservices",
        "MongoDB"
      ],
      "experience": 8,
      "available_slots": [
        { "date": "2025-04-01", "time": "10:00-12:00" },
        { "date": "2025-04-02", "time": "14:00-16:00" }
      ]
    }
  ]
  ```

## Configuration
Update the `.env` file located in `Resume_shortlister/.env` with the required details:

```bash
HF_HOME=/root/.cache/huggingface

WATSONX_APIKEY=
WATSONX_PROJECT_ID=

QDRANT_API="http://qdrant:6333"
OLLAMA_API="http://ollama:11434"

embed_model_name='nomic-embed-text'
embed_dimensions=768
```

## Running the Application
You have two options to run the application:

### **Method 1: Complete Docker Setup**
Run all services (Qdrant, Streamlit, and Ollama) in Docker:


1. Make sure the .env file is updated to use the docker endpoints:
   ```
    QDRANT_API="http://qdrant:6333"
    OLLAMA_API="http://ollama:11434"
   ```

2. Run the complete docker compose 
    ```bash
    podman compose up --build -d
    ```


This will:
- Start `qdrant`, `streamlit`, and `ollama` inside containers.
- Mount necessary volumes for persistent storage.


### **Method 2: Run Streamlit and Ollama Locally, Only Qdrant in Docker**
If Ollama is slow in Docker, you can run only Qdrant inside a container and execute Streamlit and Ollama locally.

1. Start Qdrant in Docker:
   ```bash
   podman compose up --build -d qdrant
   ```

2. Install dependencies locally:
   ```bash
   python -m venv hr_agent
   source hr_agent/bin/activate
   pip install -r requirements.txt
   ```

3. Install ollama from here https://ollama.com/download

4. Pull required ollama models 
   ```bash
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ```

5. Make sure the .env file is updated to use the local endpoints:
   ```
    QDRANT_API="http://localhost:6333"
    OLLAMA_API="http://localhost:11434"
   ```

6. Run the Streamlit application locally:
   ```bash
   streamlit run launch_simple.py
   ```

This approach allows faster execution of Ollama and Streamlit without Docker overhead.

## Usage
- The system will process resumes and match them with job profiles.
- Interviewers will be selected based on expertise and availability.
- Meeting slots will be scheduled automatically.
- Draft email invitations will be generated for the selected interviewers and candidates.
- The Streamlit UI can be used to visualize and monitor the process.


## License
This project is licensed under the [Apache License 2.0](LICENSE).  
Copyright © 2025 Parvana Kuruppal. All rights reserved. 


---

For any questions or contributions, feel free to open an issue or submit a pull request!

