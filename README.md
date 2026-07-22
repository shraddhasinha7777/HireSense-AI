# 🚀 HireSense-AI

### Smart Recruitment Analytics System

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)

---

## 📖 Overview

HireSense-AI is a Smart Recruitment Analytics System developed as a **Bachelor of Computer Applications (BCA) Major Project**.

The project helps recruiters analyze resumes more efficiently by combining resume parsing, ATS evaluation, skill matching, and AI-generated insights in a single application.

Recruiters can upload one or multiple PDF resumes together with a job description. The system extracts candidate information, compares technical skills with the job requirements, calculates an ATS score, and generates AI-powered recommendations to support the shortlisting process.

The application also provides candidate management, recruitment analytics, and report generation through a simple Streamlit interface.

---

## ✨ Features

### 📄 Resume Analysis

- Upload one or multiple PDF resumes
- Extract candidate details
- Education & Experience Detection
- Technical Skill Extraction

### 🎯 ATS Evaluation

- ATS Score Calculation
- Job Description Matching
- Skill Gap Analysis
- Hiring Recommendation

### 🤖 AI Features

- Candidate Summary
- SWOT Analysis
- Hiring Recommendation
- Interview Question Generator

### 👥 Candidate Management

- Candidate Records
- Candidate Search
- Bulk Resume Processing
- Duplicate Candidate Detection
- Blind Hiring Support

### 📊 Dashboard

- Recruitment KPIs
- ATS Analytics
- Candidate Analytics
- Skill Distribution

### 📤 Export

- PDF Report
- CSV Export
- TXT Export

---

## 🔄 Workflow

```text
Upload Resume(s) + Job Description
                │
                ▼
         Resume Parsing
                │
                ▼
 Candidate Information Extraction
                │
                ▼
          Skill Matching
                │
                ▼
      ATS Score Calculation
                │
                ▼
      Google Gemini AI Analysis
                │
                ▼
 Store Results in SQLite Database
                │
                ▼
 Dashboard • Resume Analyzer
 Candidate Management • AI Insights
```

---

## 🛠 Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python |
| Framework | Streamlit |
| Database | SQLite |
| AI | Google Gemini AI |
| Resume Parsing | pdfplumber |
| Data Processing | Pandas |
| Visualization | Plotly |
| PDF Reports | FPDF2 |
| Environment | python-dotenv |

---

## 📁 Project Structure

```text
HireSense-AI
│
├── Home.py
├── resume_parser.py
├── skill_matcher.py
├── ats_engine.py
├── ai_service.py
├── database.py
├── requirements.txt
│
├── database/
├── pages/
├── screenshots/
└── README.md
```

---

## 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/shraddhasinha7777/HireSense-AI.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Run the application

```bash
streamlit run Home.py
```

---

## 📸 Application Preview

### 🏠 Home

![Home](screenshots/Home1.png)

![Home](screenshots/Home2.png)

---

### 📄 Resume Analyzer

![Resume Analyzer](screenshots/ResumeAnalyser.png)

---

### 📊 Dashboard

![Dashboard](screenshots/Dashboard.png)

---

### 👥 Candidate Management

![Candidate Management](screenshots/Candidate%20manage.png)

---

### 🤖 AI Insights

![AI Insights](screenshots/AI%20insight1.png)

![AI Insights](screenshots/AI%20insight2.png)

---

## 👩‍💻 Developed By

**Shraddha**

Bachelor of Computer Applications (BCA)

Amrita AHEAD

Amrita Vishwa Vidyapeetham

Academic Major Project • 2026
