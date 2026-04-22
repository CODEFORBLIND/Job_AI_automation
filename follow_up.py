import csv
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def send_follow_up_email(job_title, company, recipient_email):
    """Sends a professional follow-up email using the existing SMTP logic."""
    sender_email = "justforfunnn1901@gmail.com"
    password = os.environ.get("GMAIL_APP_PASSWORD") 

    if not password:
        print("❌ Error: GMAIL_APP_PASSWORD not found in environment. Check your .env file.")
        return

    subject = f"Follow-up: Application for {job_title} role - Aditya Sharma"
    
    body = f"""
Dear Hiring Team at {company},

I hope this email finds you well.

I am writing to briefly follow up on my application for the {job_title} position, which I submitted recently. As a Master of Computer Applications (MCA) student at Savitribai Phule Pune University (SPPU) with a focus on modern Frontend development (React, TypeScript), I am very enthusiastic about the possibility of contributing to your team.

I am particularly interested in how {company} approaches scalable web architecture, and I am confident that my experience with performance optimization and component-driven design would be an asset to your current projects.

Please let me know if there are any additional materials I can provide. I look forward to hearing from you.

Best regards,

Aditya Sharma
Pune, Maharashtra
MCA Student, SPPU
"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email 

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"✅ Follow-up email sent for {job_title} at {company}")
    except Exception as e:
        print(f"❌ Failed to send follow-up: {e}")

def check_for_follow_ups():
    tracker_file = 'applied_jobs_tracker.csv'
    
    if not os.path.exists(tracker_file):
        print("❌ No application tracker found. Run the Crew first to apply to jobs!")
        return

    print("🔍 Scanning tracker for follow-up opportunities...")
    
    # We read the file to find matches
    rows = []
    with open(tracker_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # We track if we made any changes to update the CSV later
    updated = False
    for row in rows:
        app_date = datetime.strptime(row['Date'], "%Y-%m-%d %H:%M")
        
        # LOGIC: Current time >= application date + X days
        # Set to days=0 for immediate demo results
        if datetime.now() >= app_date + timedelta(days=0) and row['Status'] == "Applied/Pending": 
            print(f"Match found! Drafting follow-up for {row['Company']}...")
            send_follow_up_email(row['Job Title'], row['Company'], "justforfunnn1901@gmail.com")
            
            # Optional: Update status to avoid double-emailing
            # row['Status'] = "Followed Up"
            # updated = True

    print("--- Follow-up check completed. ---")

if __name__ == "__main__":
    check_for_follow_ups()