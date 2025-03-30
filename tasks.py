
from crewai import Task
import yaml
from agents import * 


## load the base prompts for each task from the YAML
with open('config/tasks.yaml', 'r') as file:
    tasks_config = yaml.safe_load(file)


## create the tasks programmatically
## Tasks can also be loaded directly from the YAML files, but then it lacks certain flexibility
## for example, specifying multiple context as dependency is not supported in the YAML syntax
analyse_job_description = Task(
    description=tasks_config['analyse_job_description']['description'],
    expected_output=tasks_config['analyse_job_description']['expected_output'],
    agent=HR_agent
)

extract_resume_contacts = Task(
    description=tasks_config['extract_resume_contacts']['description'],
    expected_output=tasks_config['extract_resume_contacts']['expected_output'],
    agent=resume_contact_extractor,
    context=[analyse_job_description]
)

extract_resume_skills = Task(
    description=tasks_config['extract_resume_skills']['description'],
    expected_output=tasks_config['extract_resume_skills']['expected_output'],
    agent=resume_skill_extractor,
    context=[analyse_job_description]
)

extract_resume_experience = Task(
    description=tasks_config['extract_resume_experience']['description'],
    expected_output=tasks_config['extract_resume_experience']['expected_output'],
    agent=resume_experience_extractor,
    context=[analyse_job_description]
)

match_candidate_with_interviewer = Task(
    description=tasks_config['match_candidate_with_interviewer']['description'],
    expected_output=tasks_config['match_candidate_with_interviewer']['expected_output'],
    agent=interview_candidate_matching,
    context=[extract_resume_contacts,extract_resume_skills,extract_resume_experience]
)

schedule_interviews = Task(
    description=tasks_config['schedule_interviews']['description'],
    expected_output=tasks_config['schedule_interviews']['expected_output'],
    agent=interview_scheduler,
    context=[match_candidate_with_interviewer, extract_resume_contacts]
)

send_invitation_emails = Task(
    description=tasks_config['send_invitation_emails']['description'],
    expected_output=tasks_config['send_invitation_emails']['expected_output'],
    agent=invitation_generator,
    context=[schedule_interviews,extract_resume_contacts ]
)


