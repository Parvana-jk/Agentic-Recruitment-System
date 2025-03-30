##### This file implements the class based method of defining custom Crew tools
#### This is required because certain fields of the tools are supported by the class based method only
#### specifically the feature  of `result_as_answer = True` option was required for these tools
#### this option ensures that the complete output of the tool is passed on as the agent output
#### this is useful in cases when LLM hallucinations might change critical data that shouldn't be changed
#### for example : sensitive DB query results etc

from crewai.tools import BaseTool
import os

import json

from typing import List, Dict, Any, Type
from pydantic import BaseModel, Field
from ollama import  Client

from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), ".env"))

client = Client(
  host=os.environ.get("OLLAMA_API"),
)



########### TOOL to extract the candidate contact details from the resume #############
class ResumeContactExtractorInput(BaseModel):
    """Input schema for ResumeContactExtractor."""
    folder_name: str = Field(..., description="Folder name containing resumes.")

class ResumeContactExtractor(BaseTool):
    name: str = "resume_contact_extractor"
    description: str = (
        "Extracts candidate's contact info like name, email, phone number, and LinkedIn ID from resumes in a JSON"
    )
    args_schema: Type[BaseModel] = ResumeContactExtractorInput
    result_as_answer:bool = True

    def _run(self, folder_name: str) -> List[Dict[str, Any]]:
        candidate_info_list = []
        folder_path = os.path.join(os.getcwd(), folder_name)

        if not os.path.exists(folder_path):
            return []

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    resume_text = file.read()

                response = client.chat(model="llama3.1" , messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract the candidate's name, email, and phone number from the resume "
                            "and return it in a structured JSON format. NEVER Return any thing extra apart from the json."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Resume: {resume_text}\n\nReturn the output in JSON format:\n"
                            "{\n  \"name\": \"<Candidate Name or null>\",\n"
                            "  \"email\": \"<Candidate Email or null>\",\n"
                            "  \"phone\": \"<Candidate Phone or null>\"\n}"
                        ),
                    }
                ])

                try:
                    candidate_info_list.append(response.message.content.strip())
                except json.JSONDecodeError:
                    continue

        return json.dumps(candidate_info_list)

Get_candidate_information = ResumeContactExtractor()
   

########### TOOL to extract the candidate skill details from the resume #############
class ResumeSkillExtractorInput(BaseModel):
    folder_name: str = Field("top_resumes", description="Folder containing resume files.")

class ResumeSkillExtractor(BaseTool):
    name: str = "Resume_Skill_Extractor"
    description: str = (
        "Analyse the candidate resumes and extracts their skills and expertise in different technologies in a JSON"
    )
    args_schema: Type[BaseModel] = ResumeSkillExtractorInput
    result_as_answer:bool = True



    def _run(self, folder_name: str) -> List[str]:
        folder_path = os.path.join(os.getcwd(), folder_name)
        skill_data_list = []

        if not os.path.exists(folder_path):
            print(f"Folder '{folder_name}' not found in CWD.")
            return []

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    resume_text = file.read()

                response = client.chat(model="llama3.1",  messages=[
                    {"role": "system", "content": "Extract the candidate's skills and structure them into high-level expertise areas and the outermost key being candidate email. NEVER Return anything extra apart from the JSON."},
                    {"role": "user", "content": f"Resume: {resume_text}\n\nReturn the output in JSON format. here is an example :\n{{\n  \"frontend\": \"<Technologies>\",\n  \"backend\": \"<Technologies>\",\n  \"devops\": \"<Technologies>\",\n  \"project management\": \"<Technologies>\"\n}}"}
                ])

                try:
                    skill_data_list.append(response.message.content.strip())
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON response for {file_name}, skipping.")

        return json.dumps(skill_data_list)
    






########### TOOL to extract the candidate experience details from the resume #############
class ResumeExperienceExtractorInput(BaseModel):
    folder_name: str = Field("top_resumes", description="Folder containing resume files.")

class ResumeExperienceExtractor(BaseTool):
    name: str = "Resume_Experience_Extractor"
    description: str = (
        "Analyse the given resume text and extract the candidate's experience details across different roles."
    )
    args_schema: Type[BaseModel] = ResumeExperienceExtractorInput
    result_as_answer:bool = True



    def _run(self, folder_name: str) -> List[str]:
        folder_path = os.path.join(os.getcwd(), folder_name)
        experience_data_list = []

        if not os.path.exists(folder_path):
            print(f"Folder '{folder_name}' not found in CWD.")
            return []

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    resume_text = file.read()

                response = client.chat(model="llama3.1",   messages=[
                    {"role": "system", "content": "Extract the candidate's total experience and experiences per role in years. The outermost key should be candidate email. NEVER Return anything extra apart from the JSON."},
                    {"role": "user", "content": f"Resume: {resume_text}\n\nReturn the output in JSON format. here is an example:\n{{\n  \"experience\": \"<Total years>\",\n  \"roles\": [\n    {{ \"Tech lead\": \"3\" }},\n    {{ \"Frontend developer\": \"3\" }},\n    {{ \"Engineering manager\": \"4\" }}\n  ]\n}}"}
                ])

                try:
                    experience_data_list.append(response.message.content.strip())
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON response for {file_name}, skipping.")

        return json.dumps(experience_data_list)


Get_candidate_information = ResumeContactExtractor()
Get_candidate_skills = ResumeSkillExtractor()
Get_candidate_experience = ResumeExperienceExtractor()


