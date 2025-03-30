from crewai import Agent, LLM
from tools.custom_tool import *
import yaml
import os
from dotenv import load_dotenv
load_dotenv()


### the watsonx model that will be the agent's "brain"
llama_llm = LLM(
    model="watsonx/meta-llama/llama-3-3-70b-instruct",
    base_url="https://us-south.ml.cloud.ibm.com",
	api_key=os.environ.get("WATSONX_APIKEY"),
	project_id = os.environ.get("WATSONX_PROJECT_ID"),
)


## load the base prompts for each agent from the YAML
agents_config = 'config/agents.yaml'
with open('config/agents.yaml', 'r') as file:
    agents_config = yaml.safe_load(file)
    


## create the agents programmatically
## Agents can also be loaded directly from the YAML files, but then it lacks certain flexibility
## for example, specifying tools etc in YAML is not supported for agents
HR_agent = Agent(
			config = agents_config['HR_agent'],
			verbose=True,
			tools = [query_candidate_resumes],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
resume_contact_extractor = Agent(
			config = agents_config['resume_contact_extractor'],
			verbose=True,
			tools = [Get_candidate_information],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
resume_skill_extractor = Agent(
			config = agents_config['resume_skill_extractor'],
			verbose=True,
			tools = [Get_candidate_skills],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
resume_experience_extractor = Agent(
			config = agents_config['resume_experience_extractor'],
			verbose=True,
			tools = [Get_candidate_experience],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
interview_candidate_matching = Agent(
			config = agents_config['interview_candidate_matching'],
			verbose=True,
			tools = [query_interviewers],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
interview_scheduler = Agent(
			config = agents_config['interview_scheduler'],
			verbose=True,
			tools = [],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
invitation_generator = Agent(
			config = agents_config['invitation_generator'],
			verbose=True,
            tools = [],
			llm = llama_llm,
			max_iter = 10,
			memory=True,
			allow_delegation=False,
			max_rpm=50
)
