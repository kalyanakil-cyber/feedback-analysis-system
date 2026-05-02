
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, LLM

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

csv_reader_agent = Agent(
    role="CSV Data Reader",
    goal="Read and validate feedback data from CSV files accurately",
    backstory="You are an expert data engineer who reads CSV files and ensures all data is clean and properly structured before processing.",
    llm=llm,
    verbose=True
)

classifier_agent = Agent(
    role="Feedback Classifier",
    goal="Classify each piece of feedback into exactly one category: Bug, Feature Request, Praise, Complaint, or Spam",
    backstory="You are an expert NLP specialist who has classified millions of user feedback items. You are highly accurate and consistent in your classifications.",
    llm=llm,
    verbose=True
)

bug_analysis_agent = Agent(
    role="Bug Analysis Expert",
    goal="Extract technical details from bug reports including device info, OS version, app version, steps to reproduce, and severity",
    backstory="You are a senior QA engineer who specializes in analyzing bug reports. You know exactly what technical details are needed to reproduce and fix bugs.",
    llm=llm,
    verbose=True
)

feature_extractor_agent = Agent(
    role="Feature Request Analyst",
    goal="Identify and analyze feature requests, estimate user demand and business impact",
    backstory="You are a product manager who specializes in analyzing user feature requests and prioritizing them based on demand and business value.",
    llm=llm,
    verbose=True
)

ticket_creator_agent = Agent(
    role="Ticket Creator",
    goal="Generate well structured actionable tickets from analyzed feedback with proper titles, descriptions, and priority levels",
    backstory="You are an experienced project manager who writes clear and actionable tickets that engineers and product teams can immediately act upon.",
    llm=llm,
    verbose=True
)

quality_critic_agent = Agent(
    role="Quality Critic",
    goal="Review generated tickets for completeness, accuracy, and consistency. Flag any tickets that are incomplete or incorrectly classified.",
    backstory="You are a meticulous quality assurance specialist who ensures every ticket meets the highest standards before it reaches the engineering team.",
    llm=llm,
    verbose=True
)

print("All 6 agents created successfully!")
print("Agents ready: CSV Reader, Classifier, Bug Analyst, Feature Extractor, Ticket Creator, Quality Critic")
