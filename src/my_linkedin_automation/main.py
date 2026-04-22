#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from my_linkedin_automation.crew import MyLinkedinAutomation

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
def run():
    """
    Run the LinkedIn Automation Crew.
    """
    inputs = {
        'job_title': 'Frontend Developer React',
        'location': 'Pune Maharashtra',
        'user_email': 'justforfunnn1901@gmail.com', 
        'resume_path': 'resume.pdf'
    }
    
    try:
        print("Starting LinkedIn Automation Crew...")
        # Running the actual kickoff with the new user_email input
        MyLinkedinAutomation().crew().kickoff(inputs=inputs)
        print("Crew execution completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        MyLinkedinAutomation().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MyLinkedinAutomation().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "job_title": "Software Engineer",
        "location": "Pune",
        "resume_path": "resume.pdf"
    }

    try:
        # Change 'openai_model_name' to 'eval_llm' to fix the TypeError
        MyLinkedinAutomation().crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = MyLinkedinAutomation().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
