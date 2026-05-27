import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
import markdown
from xhtml2pdf import pisa

load_dotenv()

print("--- 🚀 RUNNING STRICT RESUME EDITOR TEST ---")

# 1. The File Saving Tool (with PDF conversion)
@tool("save_tailored_resume")
def save_tailored_resume(company_name: str, resume_content: str):
    """Saves the tailored resume to Markdown and PDF."""
    folder_name = "tailored_resumes"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    clean_company = "".join(x for x in company_name if x.isalnum() or x in " _-").replace(" ", "_")
    md_filename = f"{folder_name}/Chelsi_Jain_{clean_company}_Strict_Test.md"
    pdf_filename = f"{folder_name}/Chelsi_Jain_{clean_company}_Strict_Test.pdf"
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(resume_content)
    
    html_content = markdown.markdown(resume_content)
    styled_html = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4 portrait; margin: 1.5cm; }}
            body {{ font-family: "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #222; line-height: 1.4; }}
            
            /* Header Styling */
            h1 {{ font-size: 24pt; color: #000; text-align: center; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 1px; }}
            p.subtitle {{ text-align: center; font-size: 11pt; color: #555; margin-top: 0px; margin-bottom: 15px; }}
            
            /* Section Headers */
            h2 {{ font-size: 13pt; color: #000; border-bottom: 1px solid #000; padding-bottom: 4px; margin-top: 15px; margin-bottom: 10px; text-transform: uppercase; }}
            
            /* Body Elements */
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
            
    return f"SUCCESS: Saved as {pdf_filename}"

# 2. The Agent
resume_tailor = Agent(
    role='Senior Technical Recruiter & Resume Architect',
    goal='Dynamically rewrite ONLY specific resume bullet points to perfectly match job requirements while preserving 80% of core career facts.',
    backstory='You are an expert at bypassing Applicant Tracking Systems (ATS). You act as a precision editor, never deleting core history.',
    llm='gemini/gemini-2.5-flash',
    tools=[save_tailored_resume],
    verbose=True,
    max_iter=3
)

# 3. FULL LENGTH Mock Context
base_resume_data = """
# Chelsi Jain
Frontend Web Developer & MCA Student

## Education
* Master of Computer Applications (MCA) - Savitribai Phule Pune University (SPPU)
* Vice Chairperson, ACM Student Chapter

## Experience
**Cybersecurity Intern** | ASD Cybersecurity
* Conducted vulnerability assessments and penetration testing on web applications.
* Monitored network traffic for suspicious activities and drafted daily security reports.

## Projects
**Scan-to-Shelf Kitchen Manager**
* Developed a web application using React.js.
* Integrated Vision AI to scan grocery receipts.

**LinkedIn Automation Agent**
* Built an automation script using Python.
* Used CrewAI to organize data.
"""

mock_job_requirements = """
Job Title: Senior Frontend React Engineer
Company: GlobalTech
Requirements: 
Looking for heavy experience in React state management (Redux/Context API).
Must have experience building modular frontend architectures and integrating REST APIs.
"""

# 4. The Strict Task
tailoring_task = Task(
    description=f"""
    Create a highly customized, full-length Markdown resume based on the data below.
    
    BASE RESUME:
    {base_resume_data}
    
    JOB REQUIREMENTS:
    {mock_job_requirements}
    
    INSTRUCTIONS:
    1. Act as a precision editor. Keep 80% of the resume exactly the same. ONLY modify the bullet points under 'Projects'.
    
    STRICT PRESERVATION RULES:
    - DO NOT summarize or shorten the document.
    - PRESERVE EXACTLY: Name, MCA degree at SPPU, and Vice Chairperson role.
    - PRESERVE EXACTLY: The company name 'ASD Cybersecurity' and its exact bullet points. Do not change the cybersecurity experience.
    
    ATS OPTIMIZATION RULES:
    - Focus your alterations purely on the bullet points beneath the 'Scan-to-Shelf' and 'LinkedIn Automation Agent' projects.
    - Rewrite those bullet points using the XYZ Formula: Accomplished [X] as measured by [Y], by doing [Z].
    - Use strong action verbs (e.g., Engineered, Architected, Optimized).
    - NEVER use fluffy AI jargon like "leveraged advanced techniques" or "demonstrating robust skills". Keep it technical, concise, and punchy.
    - Format project headers exactly like this: **Project Name** | *Core Tech Used*
    """,
    expected_output="A success message confirming the tailored resume was saved.",
    agent=resume_tailor
)

# 5. Execute
test_crew = Crew(agents=[resume_tailor], tasks=[tailoring_task], process=Process.sequential, verbose=True)

try:
    test_crew.kickoff()
    print("\n🎉 STRICT TEST COMPLETE! Check 'tailored_resumes' folder!")
except Exception as e:
    print(f"\n❌ AI CRASHED: {e}")