# 🎯 Intelligent User Feedback Analysis and Action System

## Capstone Project — Generative and Agentic AI Course

A fully automated multi-agent AI pipeline that reads user feedback from CSV files, classifies it using specialized AI agents, generates structured tickets, and presents everything through an interactive Streamlit dashboard.

---

## 🏆 Key Results

| Metric | Result |
|--------|--------|
| Category Classification Accuracy | 100% |
| Priority Classification Accuracy | 100% |
| Average Ticket Quality Score | 8.3 / 10 |
| Processing Time | Under 5 minutes |
| Manual Effort Required | Zero |

---

## 🤖 Multi-Agent Architecture

Six specialized AI agents collaborate in a pipeline:

| Agent | Role |
|-------|------|
| CSV Reader Agent | Reads and validates feedback from CSV files |
| Feedback Classifier Agent | Classifies into Bug / Feature Request / Praise / Complaint / Spam |
| Bug Analysis Agent | Extracts device, OS, steps to reproduce, severity |
| Feature Extractor Agent | Identifies feature requests and estimates demand |
| Ticket Creator Agent | Generates structured actionable tickets |
| Quality Critic Agent | Reviews and scores each ticket out of 10 |

---

## 🛠️ Technology Stack

- **Agent Framework:** CrewAI 1.14.4
- **LLM:** Groq llama-3.1-8b-instant (free)
- **Dashboard:** Streamlit 1.57.0
- **Data Processing:** pandas 3.0.2
- **Language:** Python 3.12

---

## 📁 Project Structure
---

## 🚀 How to Run

### 1. Install dependencies
pip install crewai openai pandas streamlit python-dotenv litellm

### 2. Set up API key
Create a .env file with your Groq API key:
GROQ_API_KEY=your-key-here
Get a free key at: console.groq.com

### 3. Run the pipeline
python main.py

### 4. Launch the dashboard
streamlit run dashboard.py
Open your browser at http://localhost:8501
---

## 📊 Dashboard Features

- Dashboard Tab — Summary metrics and category/priority charts
- Tickets Tab — Full ticket table with individual detail view
- Processing Log Tab — Complete audit trail
- Manual Override — Edit any ticket directly in the browser

---

## 👤 Author

**Kalyanaraman**
B.E. (VJTI Mumbai) | MBA (IIM Kolkata)

Capstone Project — Generative and Agentic AI Course | May 2026
