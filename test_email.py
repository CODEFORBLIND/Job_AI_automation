import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def quick_email_test():
    sender = "justforfunnn1901@gmail.com"
    # This pulls from your .env file
    password = os.getenv("GMAIL_APP_PASSWORD") 
    
    print(f"--- 📧 Testing Connection for {sender} ---")
    
    msg = MIMEText("If you are reading this, your GMAIL_APP_PASSWORD and SMTP Port 587 are working perfectly! You can now safely run your Crew.")
    msg['Subject'] = "SUCCESS: SMTP Credentials Verified"
    msg['From'] = sender
    msg['To'] = sender # Sending to yourself

    try:
        # Using Port 587 with STARTTLS (the standard we fixed earlier)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() 
            print("Connected to server. Attempting login...")
            server.login(sender, password)
            server.send_message(msg)
            print("✅ TEST SUCCESSFUL: Email sent to yourself!")
            return True
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        print("\nPossible fixes:")
        print("1. Check if GMAIL_APP_PASSWORD in .env has spaces (remove them).")
        print("2. Ensure 2-Step Verification is still ON in Google settings.")
        print("3. Check if your internet/firewall blocks Port 587.")
        return False

if __name__ == "__main__":
    quick_email_test()