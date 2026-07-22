# 🚀 HireSense-AI

### Smart Recruitment Analytics System using Artificial Intelligence

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite)
![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![BCA Project](https://img.shields.io/badge/BCA-Major%20Project-purple)

---

# 📖 Overview

HireSense-AI is a Smart Recruitment Analytics System developed as a **BCA Major Project**.

The project is designed to make the resume screening process easier and more efficient. It helps recruiters upload resumes, compare them with job descriptions, calculate ATS scores, identify skill gaps, and generate AI-based hiring insights using Google Gemini AI.

The application also provides candidate management, recruitment analytics, and report generation through a simple and interactive Streamlit interface.

---

# ✨ Features

### 📄 Resume Analysis
- Parse PDF resumes
- Extract candidate details
- Detect education and experience
- Extract technical skills

### 🎯 ATS Evaluation
- Calculate ATS Score
- Match Resume with Job Description
- Skill Gap Analysis
- Explainable ATS Score
- Hiring Recommendation

### 🤖 AI Features
- AI Candidate Summary
- SWOT Analysis
- AI Hiring Recommendation
- Interview Question Generation
- Explainable AI Insights

### 👥 Candidate Management
- Bulk Resume Upload
- Duplicate Candidate Detection
- Blind Hiring Support
- Candidate Search
- Candidate Ranking

### 📊 Dashboard & Analytics
- Recruitment Dashboard
- ATS Score Analytics
- Candidate Analytics
- Skill Distribution
- Recruitment KPIs

### 📤 Export Reports
- PDF Report
- CSV Report
- TXT Report

---

# 🏗️ Workflow

```text
Resume Upload
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
Google Gemini AI
      │
      ▼
AI Summary & Hiring Insights
      │
      ▼
SQLite Database
      │
      ▼
Dashboard & Candidate Management
      │
      ▼
Report Generation
```

---

# 🛠️ Technology Used

| Category | Technology |
|----------|------------|
| Programming Language | Python |
| Frontend | Streamlit |
| Database | SQLite |
| AI | Google Gemini AI |
| Resume Parsing | pdfplumber |
| Data Processing | Pandas |
| Data Visualization | Plotly |
| PDF Generation | FPDF2 |
| Environment Variables | python-dotenv |

---

# 📁 Project Structure

```text
HireSense-AI
│
├── Home.py
├── ai_service.py
├── ats_engine.py
├── database.py
├── resume_parser.py
├── skill_matcher.py
├── requirements.txt
│
├── database/
├── pages/
│   ├── _Resume_Analyzer.py
│   ├── _Dashboard.py
│   ├── _Candidate_Management.py
│   └── _AI_Insights.py
│
├── screenshots/
└── README.md
```

---

# 🚀 How to Run

### Clone the Repository

```bash
git clone https://github.com/shraddhasinha7777/HireSense-AI.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create Environment File

Create a `.env` file and add your Gemini API key.

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Run the Project

```bash
streamlit run Home.py
```

---

# 📌 Project Modules

- 🏠 Home
- 📄 Resume Analyzer
- 📊 Dashboard
- 👥 Candidate Management
- 🤖 AI Insights

---

# 📷 Application Screenshots

## 🏠 Home

![Home](screenshots/Home1.png)

![Home](screenshots/Home2.png)

---

## 📄 Resume Analyzer

![Resume Analyzer](screenshots/ResumeAnalyser.png)

---

## 📊 Dashboard

![Dashboard](screenshots/Dashboard.png)

---

## 👥 Candidate Management

![Candidate Management](screenshots/Candidate%20manage.png)

---

## 🤖 AI Insights

![AI Insights](screenshots/AI%20insight1.png)

![AI Insights](screenshots/AI%20insight2.png)

---

# 🎯 Main Functionalities

- Resume Parsing
- ATS Score Calculation
- Resume and Job Description Matching
- Skill Gap Analysis
- AI Candidate Summary
- SWOT Analysis
- AI Hiring Recommendation
- Interview Question Generator
- Candidate Management
- Blind Hiring
- Dashboard & Analytics
- PDF, CSV and TXT Report Export

---

# 👩‍💻 Developed By

**Shraddha**

Bachelor of Computer Applications (BCA)

Amrita AHEAD

Amrita Vishwa Vidyapeetham

Academic Major Project • 2026

---

## 📌 About this Project

This project was developed as part of the BCA curriculum to understand how Artificial Intelligence can be applied in the recruitment process. It combines resume analysis, ATS evaluation, candidate management, and AI-based insights into a single application.

---
