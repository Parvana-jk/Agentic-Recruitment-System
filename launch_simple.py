import os
import sys
import re
import threading
from time import sleep
import queue
from ansi2html import Ansi2HTMLConverter
import streamlit as st
from io import StringIO


from crewai import Crew
from agents import HR_agent, resume_contact_extractor, resume_skill_extractor, resume_experience_extractor, interview_candidate_matching, interview_scheduler, invitation_generator
from tasks import analyse_job_description, extract_resume_contacts, extract_resume_skills, extract_resume_experience, match_candidate_with_interviewer, schedule_interviews, send_invitation_emails

from embed_resumes import process_resumes

from dotenv import load_dotenv
load_dotenv()




##### wrapper function to define and launch the Agentic HR recruiter Crew
def run_crew(inputs, output_queue):

    crew = Crew(
        agents=[
            HR_agent, resume_contact_extractor, resume_skill_extractor, 
            resume_experience_extractor, interview_candidate_matching, 
            interview_scheduler, invitation_generator
        ],
        tasks=[
            analyse_job_description, extract_resume_contacts, 
            extract_resume_skills, extract_resume_experience, 
            match_candidate_with_interviewer, schedule_interviews, 
            send_invitation_emails
        ], 
        max_rpm=40,
        full_output=True, 
        output_log_file=True, 
        share_crew=False
        )

    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = StreamCapture()
    
    try:
        output = crew.kickoff(inputs=inputs)

    except Exception as e:
        output_queue.put(f"\nError: {str(e)}\n")
    
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        output_queue.put("DONE")
        output_queue.put(None)
    
    



#### custom style for the logs to be printed in the terminal style
output_queue = queue.Queue()
ansi_converter = Ansi2HTMLConverter(inline=True)


class StreamCapture(StringIO):
    def write(self, msg):
        super().write(msg)
        output_queue.put(msg)

def clean_ansi_codes(text):
    return ansi_converter.convert(text, full=False)


# Inject custom CSS for styling
st.markdown(
    """
    <style>
        .stTextInput, .stButton { width: 100%; }
        .css-18e3th9 { max-width: 90% !important; }
        .icon-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .icon {
            width: 30px;  /* Adjust size as needed */
            height: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True
)



###################################
# Streamlit UI
st.title("Resume Processing System")
job_role = st.text_input("Enter Job Role:")
job_profile = st.text_area("Enter Job Profile:")
resume_folder_path = "data/resumes/"
num_files = len(os.listdir(resume_folder_path))  # Count files in the folder

print(f"Number of files in '{resume_folder_path}': {num_files}")
output_area = st.empty()
output_text = ""




if st.button("Run CrewAI Processing"):
    with st.spinner("Processing resumes..."):
        sleep(2)
        failed_files = process_resumes(resume_folder_path)
        print("Processing the index finished")
    

        
    if failed_files:
        st.error(f"Some files failed: {failed_files}")
    else:
        st.success("All resumes processed successfully.")

    with st.spinner("Running CrewAI Agents..."):
        thread = threading.Thread(target=run_crew, args=({"job_role" : job_role, "job_profile" : job_profile}, output_queue), daemon=True)
        thread.start()

        while True:
            try:
                msg = output_queue.get(timeout=0.1)
                if msg == "DONE":
                    break
                else:
                    output_text += clean_ansi_codes(msg)
                    formatted_output = output_text.replace("\n", "<br>")
                    formatted_output = re.sub(r'<b>(.*?)</b>', r'\1', formatted_output)
                    html_content = f"""
                    <div id="output_container" style="background-color:black; color:white; padding:15px; border-radius:5px;
                        overflow-y:auto; height:500px; width:100%; font-family:monospace; font-size:12px; white-space:pre-wrap;">
                        {formatted_output}
                    </div>
                    <script>
                        var out = document.getElementById("output_container");
                        out.scrollTop = out.scrollHeight;
                    </script>
                    """
                    output_area.markdown(html_content, unsafe_allow_html=True)
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Something went wrong : {e}")
            if not thread.is_alive() and output_queue.empty():
                break

    st.success("Processing Completed.")
    # st.json(output)