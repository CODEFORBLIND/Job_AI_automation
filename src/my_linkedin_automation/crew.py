import time
import os
import csv
from datetime import datetime
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from tavily import TavilyClient

# Force load the .env file so passwords work
load_dotenv()

with open("RAW_TOOL_LINKS.txt", "w", encoding='utf-8') as f:
    f.write("--- Raw Tool Output Log ---\n")

@tool("read_resume")
def read_resume(path: str):
    """Reads the content of the resume PDF file."""
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

@tool("untruncated_job_search")
def untruncated_job_search(query: str):
    """Search for exactly one direct Indeed viewjob link and log it."""
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    optimized_query = f"{query} site:in.indeed.com/viewjob"
    
    search_result = client.search(
        query=optimized_query,
        search_depth="advanced",
        max_results=1
    )

    try:
        with open("RAW_TOOL_LINKS.txt", "a", encoding='utf-8') as f:
            for res in search_result.get('results', []):
                f.write(f"{res['url']}\n")
        print("✅ Success: Job link logged to RAW_TOOL_LINKS.txt")
    except Exception as e:
        print(f"❌ Warning: Could not log to file: {e}")

    return search_result

@tool("send_automation_email")
def send_automation_email(to_email: str, subject: str, body: str):
    """Sends a professional automation update email to the user."""
    SENDER_EMAIL = "justforfunnn1901@gmail.com" 
    APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD") 

    if not APP_PASSWORD:
        return "FAILED: GMAIL_APP_PASSWORD is not set in the .env file."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return f"SUCCESS: Email sent to {to_email}"
    except Exception as e:
        return f"FAILED to send email: {str(e)}"

@tool("execute_job_application")
def execute_job_application(job_title: str, company: str, job_url: str, location: str = "N/A", ats_score: str = "N/A"):
    """SIMULATION TOOL: Records an individual job application into the tracker database, checking for duplicates."""
    import csv
    import os
    from datetime import datetime
    
    print(f"\n--- 🛡️ SIMULATING APPLICATION: {job_title} at {company} ({location}) ---")
    date_applied = datetime.now().strftime("%Y-%m-%d %H:%M")
    tracker_file = 'applied_jobs_tracker.csv'
    
    is_new_file = not os.path.exists(tracker_file)
    
    # 1. SMART DUPLICATE CHECK: Verify the unique URL hasn't been saved yet
    if not is_new_file:
        try:
            with open(tracker_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    # Check column index 3 (URL) to avoid copying existing entries
                    if len(row) > 3 and row[3] == job_url:
                        print(f"⚠️ SKIP: Entry already exists for {job_url}")
                        return f"SKIPPED: {job_title} at {company} is already in the database."
        except Exception as e:
            print(f"Error reading tracker: {e}")

    # 2. APPEND ENTRY: Write the row with your new customized columns
    try:
        with open(tracker_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Define your custom column layout here
            if is_new_file:
                writer.writerow(['Date', 'Job Title', 'Company', 'URL', 'Location', 'ATS Score', 'Status'])
            
            # Log the corresponding data fields
            writer.writerow([date_applied, job_title, company, job_url, location, ats_score, "SIMULATED_SUCCESS"])
            
        with open(tracker_file, mode='r', encoding='utf-8') as file:
            total_rows = sum(1 for row in file) - 1
            
        print(f"✅ SUCCESS: Appended safely. Total unique records in tracker: {total_rows}")
        return f"SUCCESS: Logged {job_title} at {company}. Total tracker rows: {total_rows}"
    except Exception as e:
        return f"FAILED to write entry: {str(e)}"
    

@CrewBase
class MyLinkedinAutomation():
    """MyLinkedinAutomation crew optimized for efficiency"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def job_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['job_researcher'],
            tools=[untruncated_job_search], 
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: time.sleep(5)
        )

    @agent
    def resume_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyst'],
            tools=[read_resume], 
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: time.sleep(5)
        )

    @agent
    def outreach_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['outreach_specialist'],
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: time.sleep(5)
        )
    
    @agent
    def automation_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['automation_manager'],
            tools=[send_automation_email, execute_job_application], 
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: time.sleep(5)
        )

    @task
    def research_job_task(self) -> Task:
        return Task(config=self.tasks_config['research_job_task'])

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
            human_input=True
        )

    @task
    def simulate_application_task(self) -> Task:
        return Task(
            config=self.tasks_config['simulate_application_task'],
            context=[self.user_checkup_task(), self.research_job_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            max_rpm=1,
            cache=True
        )