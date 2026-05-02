import os
import csv
import json
import re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, LLM

llm = LLM(model='groq/llama-3.1-8b-instant', api_key=os.getenv('GROQ_API_KEY'))

classifier_agent = Agent(
    role='Feedback Classifier',
    goal='Classify feedback into exactly one category: Bug, Feature Request, Praise, Complaint, or Spam',
    backstory='You are an expert NLP specialist who classifies user feedback accurately.',
    llm=llm, verbose=True
)

ticket_creator_agent = Agent(
    role='Ticket Creator',
    goal='Generate well structured actionable tickets from analyzed feedback',
    backstory='You are an experienced project manager who writes clear actionable tickets.',
    llm=llm, verbose=True
)

quality_critic_agent = Agent(
    role='Quality Critic',
    goal='Review generated tickets for completeness and accuracy',
    backstory='You are a meticulous QA specialist who ensures every ticket meets high standards.',
    llm=llm, verbose=True
)

classifier_agent = Agent(
    role='Feedback Classifier',
    goal='Classify feedback into exactly one category: Bug, Feature Request, Praise, Complaint, or Spam',
    backstory='You are an expert NLP specialist who classifies user feedback accurately.',
    llm=llm, verbose=True
)

ticket_creator_agent = Agent(
    role='Ticket Creator',
    goal='Generate well structured actionable tickets from analyzed feedback',
    backstory='You are an experienced project manager who writes clear actionable tickets.',
    llm=llm, verbose=True
)

quality_critic_agent = Agent(
    role='Quality Critic',
    goal='Review generated tickets for completeness and accuracy',
    backstory='You are a meticulous QA specialist who ensures every ticket meets high standards.',
    llm=llm, verbose=True
)

def read_csv(filepath):
    rows = []
    with open(filepath, encoding='utf-8') as f2:
        reader = csv.DictReader(f2)
        for row in reader:
            rows.append(row)
    return rows

def parse_result(raw, feedback_text):
    cat = 'Unknown'; pri = 'Medium'; title = 'Untitled'
    details = ''; desc = ''; score = 'N/A'
    clean = re.sub(r'```json|```', '', raw).strip()
    all_jsons = re.findall(r'\{[^{}]+\}', clean, re.DOTALL)
    for j in all_jsons:
        try:
            parsed = json.loads(j)
            if 'category' in parsed and parsed['category'] in ['Bug','Feature Request','Praise','Complaint','Spam']:
                cat = parsed['category']
                pri = parsed.get('priority', 'Medium')
                title = str(parsed.get('suggested_title', 'Untitled'))
                raw_d = parsed.get('technical_details', '')
                details = str(raw_d) if not isinstance(raw_d, list) else ', '.join(raw_d)
            if 'ticket_description' in parsed:
                val = parsed['ticket_description']
                desc = ' '.join(str(v) for v in val.values()) if isinstance(val, dict) else str(val)
            if 'quality_score' in parsed:
                score = str(parsed['quality_score'])
        except: pass
    if cat == 'Unknown':
        m = re.search(r'"category"\s*:\s*"([^"]+)"', clean)
        if m and m.group(1) in ['Bug','Feature Request','Praise','Complaint','Spam']: cat = m.group(1)
    if pri == 'Medium':
        m = re.search(r'"priority"\s*:\s*"([^"]+)"', clean)
        if m and m.group(1) in ['Critical','High','Medium','Low']: pri = m.group(1)
    if title == 'Untitled':
        m = re.search(r'"suggested_title"\s*:\s*"([^"]+)"', clean)
        if m: title = m.group(1)
    if not desc:
        m = re.search(r'"ticket_description"\s*:\s*"([^"]+)"', clean)
        desc = m.group(1) if m else feedback_text[:200]
    if score == 'N/A':
        m = re.search(r'"quality_score"\s*:\s*(\d+)', clean)
        if m: score = m.group(1)
    return cat, pri, title, details, desc, score

def process_feedback(feedback_text, source_id, source_type):
    classify_task = Task(
        description='Analyze this feedback and return ONLY a JSON object with NO extra text.\n'
            'Example: {"category": "Bug", "priority": "Critical", "technical_details": "details", "suggested_title": "title"}\n'
            'category must be one of: Bug, Feature Request, Praise, Complaint, Spam\n'
            'priority must be one of: Critical, High, Medium, Low\n'
            f'Feedback ID: {source_id}\nFeedback: {feedback_text}',
        agent=classifier_agent,
        expected_output='A JSON object with category, priority, technical_details, suggested_title'
    )
    ticket_task = Task(
        description='Create a ticket description. Return ONLY this JSON:\n'
            '{"ticket_description": "your description here"}\n'
            f'Feedback: {feedback_text}\nSource ID: {source_id}',
        agent=ticket_creator_agent,
        expected_output='A JSON object with ticket_description field'
    )
    quality_task = Task(
        description='Review this ticket and return ONLY this JSON:\n'
            '{"quality_score": 8, "quality_notes": "notes here"}\n'
            f'quality_score must be a number 1-10. Ticket ID: {source_id}',
        agent=quality_critic_agent,
        expected_output='A JSON object with quality_score and quality_notes'
    )
    crew = Crew(
        agents=[classifier_agent, ticket_creator_agent, quality_critic_agent],
        tasks=[classify_task, ticket_task, quality_task],
        verbose=True
    )
    crew_result = crew.kickoff()
    all_outputs = [str(t.output.raw) for t in crew.tasks if t.output]
    return '|||'.join(all_outputs)

def save_ticket(ticket_data, output_file):
    file_exists = os.path.exists(output_file)
    with open(output_file, 'a', newline='', encoding='utf-8') as f2:
        fieldnames = ['ticket_id','source_id','source_type','category','priority',
                      'suggested_title','technical_details','ticket_description',
                      'quality_score','processed_at']
        writer = csv.DictWriter(f2, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(ticket_data)

def save_log(log_data, log_file):
    file_exists = os.path.exists(log_file)
    with open(log_file, 'a', newline='', encoding='utf-8') as f2:
        fieldnames = ['timestamp','source_id','source_type','status','message']
        writer = csv.DictWriter(f2, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_data)

def run_pipeline():
    print('=' * 60)
    print('FEEDBACK ANALYSIS PIPELINE STARTING')
    print('=' * 60)
    os.makedirs('output', exist_ok=True)
    output_file = 'output/generated_tickets.csv'
    log_file = 'output/processing_log.csv'
    if os.path.exists(output_file): os.remove(output_file)
    if os.path.exists(log_file): os.remove(log_file)
    ticket_counter = 1
    reviews = read_csv('data/app_store_reviews.csv')
    emails = read_csv('data/support_emails.csv')
    print(f'Loaded {len(reviews)} reviews and {len(emails)} emails')
    print(f'Processing ALL {len(reviews) + len(emails)} items...')
    all_feedback = []
    for r in reviews:
        all_feedback.append({'id': r['review_id'], 'type': 'review', 'text': r['review_text']})
    for e in emails:
        all_feedback.append({'id': e['email_id'], 'type': 'email', 'text': e['subject'] + ' ' + e['body']})
    for item in all_feedback:
        print('Processing ' + item['id'] + ' (' + str(ticket_counter) + '/' + str(len(all_feedback)) + ')...')
        try:
            import time
            time.sleep(20)
            result = process_feedback(item['text'], item['id'], item['type'])
            cat, pri, title, details, desc, score = parse_result(result, item['text'])
            ticket = {
                'ticket_id': f'TKT-{ticket_counter:03d}',
                'source_id': item['id'],
                'source_type': item['type'],
                'category': cat,
                'priority': pri,
                'suggested_title': title[:150],
                'technical_details': details[:200],
                'ticket_description': desc[:300],
                'quality_score': score,
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            save_ticket(ticket, output_file)
            save_log({'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'source_id': item['id'], 'source_type': item['type'], 'status': 'SUCCESS', 'message': 'Ticket created - ' + cat + ' / ' + pri}, log_file)
            ticket_counter += 1
            print('TKT-' + str(ticket_counter-1).zfill(3) + ' created: ' + cat + ' / ' + pri)
        except Exception as ex:
            print('Error: ' + str(ex))
            save_log({'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'source_id': item['id'], 'source_type': item['type'], 'status': 'ERROR', 'message': str(ex)[:200]}, log_file)

if __name__ == '__main__':
    run_pipeline()
