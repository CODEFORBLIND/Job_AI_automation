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
    

@tool("save_cover_letter")
def save_cover_letter(company_name: str, job_title: str, letter_content: str):
    """Saves the generated cover letter to a local markdown file."""
    import os
    
    # 1. Create a dedicated folder for cover letters if it doesn't exist
    folder_name = "cover_letters"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # 2. Clean the company name so it's safe to use as a file name
    clean_company = "".join(x for x in company_name if x.isalnum() or x in " _-").replace(" ", "_")
    clean_title = "".join(x for x in job_title if x.isalnum() or x in " _-").replace(" ", "_")
    filename = f"{folder_name}/{clean_company}_{clean_title}_CoverLetter.md"
    
    # 3. Save the actual text to the file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(letter_content)
    
    print(f"📄 SUCCESS: Custom Cover Letter saved as {filename}")
    return f"SUCCESS: Cover letter saved locally as {filename}"


@tool("save_tailored_resume")
def save_tailored_resume(company_name: str, resume_content: str):
    """Saves the tailored resume to a local markdown file AND converts it to a professional PDF."""
    import os
    import markdown
    from xhtml2pdf import pisa
    
    # 1. Create a dedicated folder for tailored resumes
    folder_name = "tailored_resumes"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # 2. Clean the company name for the file path
    clean_company = "".join(x for x in company_name if x.isalnum() or x in " _-").replace(" ", "_")
    md_filename = f"{folder_name}/Chelsi_Jain_{clean_company}_Resume.md"
    pdf_filename = f"{folder_name}/Chelsi_Jain_{clean_company}_Resume.pdf"
    
    # 3. Save the Markdown file (as a backup)
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(resume_content)
    
    # 4. Convert Markdown to HTML
    # We add basic CSS styling to make the PDF look like a real resume
    html_content = markdown.markdown(resume_content)
    styled_html = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4 portrait; margin: 2cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12pt; color: #333; }}
            h1 {{ font-size: 24pt; color: #2c3e50; text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 5px; }}
            h2 {{ font-size: 16pt; color: #34495e; margin-top: 20px; border-bottom: 1px solid #ccc; }}
            ul {{ margin-bottom: 15px; }}
            li {{ margin-bottom: 5px; line-height: 1.4; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # 5. Convert HTML to PDF using xhtml2pdf
    try:
        with open(pdf_filename, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)
            
        if pisa_status.err:
            print(f"⚠️ Warning: PDF generated with some errors for {clean_company}")
        else:
            print(f"📄 SUCCESS: Markdown AND PDF Resume saved for {clean_company}!")
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return f"Saved MD, but failed to generate PDF: {e}"
        
    return f"SUCCESS: Resume saved locally as {pdf_filename}"

@tool("save_tailored_resume")
def save_tailored_resume(company_name: str, resume_content: str):
    """Saves the tailored resume to Markdown and PDF."""
    import os
    import markdown
    from xhtml2pdf import pisa

    folder_name = "tailored_resumes"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    clean_company = "".join(x for x in company_name if x.isalnum() or x in " _-").replace(" ", "_")
    md_filename = f"{folder_name}/Chelsi_Jain_{clean_company}_Resume.md"
    pdf_filename = f"{folder_name}/Chelsi_Jain_{clean_company}_Resume.pdf"
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(resume_content)
    
    html_content = markdown.markdown(resume_content)
    styled_html = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4 portrait; margin: 1.5cm; }}
            body {{ font-family: "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #222; line-height: 1.4; }}
            h1 {{ font-size: 24pt; color: #000; text-align: center; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 1px; }}
            p.subtitle {{ text-align: center; font-size: 11pt; color: #555; margin-top: 0px; margin-bottom: 15px; }}
            h2 {{ font-size: 13pt; color: #000; border-bottom: 1px solid #000; padding-bottom: 4px; margin-top: 15px; margin-bottom: 10px; text-transform: uppercase; }}
            ul {{ margin-top: 5px; margin-bottom: 15px; padding-left: 20px; }}
            li {{ margin-bottom: 5px; text-align: justify; }}
            strong {{ color: #000; font-weight: bold; }}
            em {{ color: #444; font-style: italic; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    with open(pdf_filename, "w+b") as pdf_file:
        pisa.CreatePDF(styled_html, dest=pdf_file)
            
    print(f"📄 SUCCESS: Tailored Resume saved for {clean_company}")
    return f"SUCCESS: Saved as {pdf_filename}"

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
    
    @agent
    def cover_letter_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['cover_letter_writer'],
            tools=[save_cover_letter], # Give it the new tool!
            verbose=True,
            allow_delegation=False,
            step_callback=lambda step: time.sleep(5)
        )
    
    @agent
    def resume_tailor(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_tailor'],
            tools=[save_tailored_resume], 
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def tailor_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['tailor_resume_task'],
            context=[self.research_job_task()] # Gives it the job requirements
        )
    
    @task
    def tailor_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['tailor_resume_task'],
            context=[self.user_checkup_task(), self.research_job_task(), self.analyze_resume_task()]
        )
    
    @task
    def write_cover_letter_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_cover_letter_task'],
            context=[self.user_checkup_task(), self.research_job_task(), self.analyze_resume_task()]
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
            tasks=[
                self.research_job_task(),
                self.analyze_resume_task(),
                self.outreach_task(),
                self.user_checkup_task(),
                self.simulate_application_task(),
                self.write_cover_letter_task(),
                self.tailor_resume_task()
            ], 
            process=Process.sequential,
            verbose=True,
            max_rpm=1,
            cache=True
        )