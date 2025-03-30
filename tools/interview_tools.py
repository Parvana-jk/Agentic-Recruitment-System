from crewai.tools import tool
from typing import List, Dict, Any
import json
import os

@tool('Retrieve available interviewers')
def query_interviewers() -> List[Dict[str, Any]]:
    """
    Retrieves a list of available interviewers from a JSON file.

    Each interviewer entry includes:
    - id (int): Unique identifier of the interviewer.
    - name (str): Name of the interviewer.
    - role (str): Job role of the interviewer.
    - skills (List[str]): List of technical skills.
    - experience (int): Years of experience.
    - available_slots (List[Dict[str, str]]): Available interview slots with date and time.

    Returns:
        List[Dict[str, Any]]: A list of interviewer details.
    """
    with open(os.path.join(os.getcwd(), "data/interviewers.json"), "r", encoding="utf-8") as file:
        interviewers = json.load(file)

    return interviewers