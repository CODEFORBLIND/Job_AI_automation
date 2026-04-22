import time
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai.tools import tool 
# Optimized Tavily Tool
from crewai_tools import TavilySearchTool 

import csv
from datetime import datetime
import os
from PyPDF2 import PdfReader

import smtplib
from email.mime.text import MIMEText


import os
APP_PASSWORD = os.environ.get("rzhd mwgk rkiv mejf")

# --- Custom Tools ---

@tool("read_resume")
def read_resume(path: str):
    """Reads the content of the resume PDF file."""
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Create a dedicated file for raw links at the start of the script
with open("RAW_TOOL_LINKS.txt", "w") as f:
    f.write("--- Raw Tool Output Log ---\n")

@tool("untruncated_job_search")
def untruncated_job_search(query: str):
    """Search for exactly one direct Indeed viewjob link and log it."""
    from tavily import TavilyClient
    import os
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    
    # Force direct links using 'viewjob' pattern
    optimized_query = f"{query} site:in.indeed.com/viewjob"
    
    search_result = client.search(
        query=optimized_query,
        search_depth="advanced",
        max_results=1 
    )

    # --- FIX: Move the Logging BEFORE the return statement ---
    try:
        with open("RAW_TOOL_LINKS.txt", "a", encoding='utf-8') as f:
            # Tavily returns results in a 'results' list
            for res in search_result.get('results', []):
                f.write(f"{res['url']}\n")
        print("✅ Success: Job link logged to RAW_TOOL_LINKS.txt")
    except Exception as e:
        print(f"❌ Warning: Could not log to file: {e}")

    # Now we return the result so the agent can see it
    return search_result




@tool("send_automation_email")
def send_automation_email(to_email: str, subject: str, body: str):
    """Sends a professional automation update email to the user."""
    import smtplib
    from email.mime.text import MIMEText

    SENDER_EMAIL = "justforfunnn1901@gmail.com" 
    APP_PASSWORD = "rwttmkkrpokpruso" 

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
        # Switching to Port 587 with STARTTLS (Better for Windows/Firewalls)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1) # This will show us exactly where it hangs in the terminal
        server.starttls() 
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return f"SUCCESS: Email sent to {to_email}"
    except Exception as e:
        return f"FAILED to send email: {str(e)}"

# --- Crew Definition ---

@CrewBase
class MyLinkedinAutomation():
    """MyLinkedinAutomation crew optimized for efficiency"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def job_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['job_researcher'],
            tools=[untruncated_job_search], 
            max_rpm=1, 
            verbose=True,
            allow_delegation=False,
            backstory="You are an expert at finding accessible job postings on Indeed and Naukri. "
                    "You avoid LinkedIn because its links are often blocked for users.",
            step_callback=lambda step: print("--- Rate Limit Cooling (10s) ---") or time.sleep(10)
        )

    @agent
    def resume_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyst'],
            tools=[read_resume], 
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: print("--- Rate Limit Cooling (10s) ---") or time.sleep(10)
        )

    @agent
    def outreach_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['outreach_specialist'],
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def automation_manager(self) -> Agent:
        return Agent(
            role="Career Automation Manager",
            goal="Coordinate user checkups and job application confirmations.",
            backstory="You bridge the gap between AI job discovery and real-world application execution.",
            tools=[send_automation_email],
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: print("--- Rate Limit Cooling (10s) ---") or time.sleep(10)
        )
    
    @agent
    def automation_manager(self) -> Agent:
        return Agent(
        config=self.agents_config['automation_manager'],
        # Make sure the manager has the new simulation tool
        tools=[send_automation_email, execute_job_application], 
        verbose=True,
        allow_delegation=False
        )

    @task
    def research_job_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_job_task'],
        )

    @task
    def analyze_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_resume_task'],
            context=[self.research_job_task()] 
        )

    @task
    def outreach_task(self) -> Task:
        return Task(
            config=self.tasks_config['outreach_task'],
            context=[self.analyze_resume_task()],
            output_file='final_outreach_report.md'
        )

    @task
    def user_checkup_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_checkup_task'],
            context=[self.analyze_resume_task()],
            human_input=True # This is the magic line for your demo!
        )

    @task
    def simulate_application_task(self) -> Task:
        return Task(
            config=self.tasks_config['simulate_application_task'],
            context=[self.user_checkup_task()]
        )

    @task
    def final_acknowledgement_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_acknowledgement_task'],
            context=[self.simulate_application_task()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MyLinkedinAutomation crew"""
        return Crew(
            agents=self.agents, 
            tasks=[
                self.research_job_task(),
                self.analyze_resume_task(),
                self.outreach_task(),
                self.user_checkup_task(),
                self.simulate_application_task(),
                self.final_acknowledgement_task()
            ], 
            process=Process.sequential,
            verbose=True,
            max_rpm=1,
            cache=True # Enable caching so if it retries a tool, it doesn't use a credit
        )
    
    
    

@tool("execute_job_application")
def execute_job_application(job_title: str, company: str, job_url: str):
    """
    SIMULATION TOOL: Records the application in the tracker database.
    Does not perform a real web submission to protect user privacy.
    """
    import csv
    from datetime import datetime
    
    print(f"--- 🛡️ SIMULATING APPLICATION: {job_title} at {company} ---")
    
    date_applied = datetime.now().strftime("%Y-%m-%d %H:%M")
    tracker_file = 'applied_jobs_tracker.csv'
    file_exists = os.path.isfile(tracker_file)
    
    # Writing to our 'Database' so we have proof for the project report
    with open(tracker_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Job Title', 'Company', 'URL', 'Status'])
        writer.writerow([date_applied, job_title, company, job_url, "SIMULATED_SUCCESS"])
    
    return f"VIRTUAL SUCCESS: Application for {job_title} logged in tracker. No real data sent to {company}."