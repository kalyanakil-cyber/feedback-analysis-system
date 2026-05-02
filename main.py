
import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, LLM

llm = LLM(model="groq/llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

classifier_agent = Agent(
    role="Feedback Classifier",
    goal="Classify feedback into exactly one category: Bug, Feature Request, Praise, Complaint, or Spam",
    backstory="You are an expert NLP specialist who classifies user feedback accurately and consistently.",
    llm=llm,
    verbose=True
)

ticket_creator_agent = Agent(
    role="Ticket Creator",
    goal="Generate well structured actionable tickets from analyzed feedback",
    backstory="You are an experienced project manager who writes clear actionable tickets.",
    llm=llm,
    verbose=True
)

quality_critic_agent = Agent(
    role="Quality Critic",
    goal="Review generated tickets for completeness and accuracy",
    backstory="You are a meticulous QA specialist who ensures every ticket meets high standards.",
    llm=llm,
    verbose=True
)

def read_csv(filepath):
    rows = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def process_feedback(feedback_text, source_id, source_type):
    classify_task = Task(
        description=f"""
        Analyze this user feedback and return a JSON object with these exact fields:
        - category: one of Bug, Feature Request, Praise, Complaint, Spam
        - priority: one of Critical, High, Medium, Low
        - technical_details: key technical info extracted from the feedback
        - suggested_title: a clear actionable ticket title

        Feedback ID: {source_id}
        Source Type: {source_type}
        Feedback Text: {feedback_text}

        Return ONLY a valid JSON object. No extra text.
        """,
        agent=classifier_agent,
        expected_output="A JSON object with category, priority, technical_details, and suggested_title"
    )

    ticket_task = Task(
        description=f"""
        Based on the classification of this feedback, create a detailed ticket description.
        Include: what the issue is, who reported it, what action is needed.
        
        Feedback: {feedback_text}
        Source ID: {source_id}
        
        Return ONLY a JSON object with field: ticket_description
        """,
        agent=ticket_creator_agent,
        expected_output="A JSON object with ticket_description field"
    )

    quality_task = Task(
        description=f"""
        Review the ticket created for feedback {source_id}.
        Check if it has clear title, correct priority, and actionable description.
        Return ONLY a JSON object with fields:
        - quality_score: number from 1 to 10
        - quality_notes: brief comment on ticket quality
        """,
        agent=quality_critic_agent,
        expected_output="A JSON object with quality_score and quality_notes"
    )

    crew = Crew(
        agents=[classifier_agent, ticket_creator_agent, quality_critic_agent],
        tasks=[classify_task, ticket_task, quality_task],
        verbose=True
    )

    result = crew.kickoff()
    return str(result)

def save_ticket(ticket_data, output_file):
    file_exists = os.path.exists(output_file)
    with open(output_file, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["ticket_id","source_id","source_type","category","priority","suggested_title","technical_details","ticket_description","quality_score","processed_at"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(ticket_data)

def save_log(log_data, log_file):
    file_exists = os.path.exists(log_file)
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["timestamp","source_id","source_type","status","message"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_data)

def run_pipeline():
    print("=" * 60)
    print("FEEDBACK ANALYSIS PIPELINE STARTING")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    output_file = "output/generated_tickets.csv"
    log_file = "output/processing_log.csv"
    ticket_counter = 1

    reviews = read_csv("data/app_store_reviews.csv")
    emails = read_csv("data/support_emails.csv")
    print(f"Loaded {len(reviews)} reviews and {len(emails)} emails")
    print("Processing first 3 items as demo...")

    all_feedback = []
    for r in reviews[:2]:
        all_feedback.append({"id": r["review_id"], "type": "review", "text": r["review_text"]})
    for e in emails[:1]:
        all_feedback.append({"id": e["email_id"], "type": "email", "text": e["subject"] + " " + e["body"]})

    for item in all_feedback:
        print(f"\nProcessing {item['id']}...")
        try:
            result = process_feedback(item["text"], item["id"], item["type"])
            import json, re
            raw = str(result)
            cat = "Unknown"; pri = "Medium"; title = "Untitled"; details = ""; desc = ""; score = "N/A"
            try:
                match = re.search(r'\{[^{}]*"category"[^{}]*\}', raw, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    cat = parsed.get("category", "Unknown")
                    pri = parsed.get("priority", "Medium")
                    title = parsed.get("suggested_title", "Untitled")
                    details = parsed.get("technical_details", "")
            except: pass
            try:
                match2 = re.search(r'"ticket_description"\s*:\s*"([^"]*)"', raw)
                if match2: desc = match2.group(1)
            except: pass
            try:
                match3 = re.search(r'"quality_score"\s*:\s*(\d+)', raw)
                if match3: score = match3.group(1)
            except: pass
            ticket = {
                "ticket_id": f"TKT-{ticket_counter:03d}",
                "source_id": item["id"],
                "source_type": item["type"],
                "category": cat,
                "priority": pri,
                "suggested_title": title,
                "technical_details": details[:200],
                "ticket_description": desc[:300],
                "quality_score": score,
                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_ticket(ticket, output_file)
            save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "source_id": item["id"], "source_type": item["type"], "status": "SUCCESS", "message": "Ticket created successfully"}, log_file)
            ticket_counter += 1
            print(f"Ticket TKT-{ticket_counter-1:03d} created for {item['id']}")
        except Exception as ex:
            print(f"Error processing {item['id']}: {ex}")
            save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "source_id": item["id"], "source_type": item["type"], "status": "ERROR", "message": str(ex)}, log_file)

    print("\n" + "=" * 60)
    print(f"PIPELINE COMPLETE! {ticket_counter-1} tickets created.")
    print(f"Output saved to: {output_file}")
    print(f"Log saved to: {log_file}")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
