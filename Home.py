import streamlit as st
import pandas as pd
import time
import sys
import os
import json
from datetime import datetime

# --- IMPORT FIX ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from resume_parser import ResumeParser
from ats_engine import ATSEngine
from skill_matcher import SkillMatcher
from ai_service import AIService

# Initialize All Engines
db = Database()
parser = ResumeParser()
engine = ATSEngine()
matcher = SkillMatcher()
ai_engine = AIService()

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "latest_candidate_data" not in st.session_state:
    st.session_state.latest_candidate_data = {}

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE CSS STYLING
# =====================================================================
st.set_page_config(
    page_title="Home | HireSense-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
    <style>
    /* 🌌 MAIN APP BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #090514 0%, #0F0B26 100%) !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    
    /* ⭐ HERO BOX */
    .hero-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #312E81 100%) !important;
        padding: 35px 25px !important;
        border-radius: 16px !important;
        border: 1px solid #4F46E5 !important;
        border-top: 2px solid #8B5CF6 !important;
        text-align: center !important;
        margin-bottom: 35px !important;
        box-shadow: 0 10px 30px -5px rgba(79, 70, 229, 0.35) !important;
    }
    .welcome-title { 
        font-size: 32px !important; 
        font-weight: 900 !important; 
        color: #FFFFFF !important; 
        margin-bottom: 8px !important;
        letter-spacing: 0.5px !important;
    }
    .welcome-subtitle { 
        font-size: 16px !important; 
        color: #E2E8F0 !important; 
        margin-bottom: 6px !important; 
        font-weight: 600 !important;
    }
    .welcome-small-text {
        font-size: 12px !important;
        color: #94A3B8 !important;
        margin-bottom: 22px !important;
        font-weight: 500 !important;
    }
    .welcome-tagline { 
        font-size: 12px !important; 
        font-weight: 800 !important; 
        color: #38BDF8 !important; 
        text-transform: uppercase !important; 
        letter-spacing: 3px !important;
        margin-bottom: 0 !important;
    }

    /* 🟣 SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #030109 !important;
        border-right: 1px solid #1E293B !important;
    }

    .stTextArea label, .stFileUploader label, .stCheckbox label, .stCheckbox span {
        color: #F8FAFC !important;
    }

    .intake-header { 
        font-size: 18px; 
        font-weight: 800; 
        color: #38BDF8 !important; 
        background: #1E293B;
        padding: 10px 16px;
        border-radius: 8px;
        border-left: 4px solid #38BDF8;
        margin-bottom: 12px; 
        display: flex; 
        align-items: center; 
        gap: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* 🚀 BUTTON */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        padding: 13px 26px !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 22px rgba(139, 92, 246, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 12px 26px rgba(139, 92, 246, 0.6) !important;
    }
    
    /* ✨ ORIGINAL WHITE FEATURE CARDS WITH HOVER EFFECT */
    .feature-card {
        background: #FFFFFF !important;
        padding: 18px 14px !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        text-align: center !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        min-height: 145px !important;
        height: 100% !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    .feature-card:hover { 
        transform: translateY(-6px) !important; 
        border-color: #4F46E5 !important; 
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.3) !important; 
    }
    .feature-icon { font-size: 26px; margin-bottom: 8px; }
    .feature-title { font-size: 13px; font-weight: 700; color: #1E293B !important; margin-bottom: 6px; }
    .feature-desc { font-size: 11px; color: #64748B !important; line-height: 1.4; }
    
    /* ⚙️ ORIGINAL WHITE WORKFLOW STEP CARDS WITH HOVER EFFECT */
    .step-card {
        background: #FFFFFF !important;
        padding: 16px 12px !important;
        border-radius: 12px !important;
        border: 1.5px dashed #CBD5E1 !important;
        text-align: center !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        min-height: 135px !important;
        height: 100% !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
    }
    .step-card:hover {
        transform: translateY(-6px) !important;
        border-color: #6366F1 !important;
        background: #F8FAFC !important;
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.3) !important;
    }
    .step-num { font-size: 10px; font-weight: 800; color: #6366F1; text-transform: uppercase; letter-spacing: 1px; }
    .step-name { font-size: 13px; font-weight: 700; color: #1E293B !important; margin: 6px 0 4px 0; }
    .step-desc { font-size: 11px; color: #64748B !important; line-height: 1.4; }

    /* ⚡ LIVE PROCESSING TIMELINE */
    .timeline-card {
        background: #0D1127;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 20px;
        margin: 20px 0;
    }
    .timeline-title {
        color: #38BDF8;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 20px;
    }
    .timeline-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
    }
    .step-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
    }
    .step-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #090514;
        border: 2px solid #334155;
        color: #64748B;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: bold;
    }
    .step-icon.active {
        border-color: #3B82F6;
        color: #3B82F6;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
    }
    .step-icon.done {
        border-color: #10B981;
        background: #10B981;
        color: #FFFFFF;
    }
    .step-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        margin-top: 6px;
    }
    .step-label.active { color: #38BDF8; }
    .step-label.done { color: #34D399; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: white; margin-bottom: 0;">🤖 HireSense-AI</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background-color: #0F172A; padding: 15px; border-radius: 12px; border: 1px solid #1E293B; margin-bottom: 20px;">
            <p style="color: #38BDF8; font-weight: bold; margin-bottom: 5px;">💡 Quick Tip</p>
            <p style="color: #94A3B8; font-size: 13px; line-height: 1.4;">Paste your target Job Description and upload candidate resumes to trigger automated evaluation.</p>
        </div>
    """, unsafe_allow_html=True)

    current_date = datetime.now().strftime("%d %b %Y")
    current_time = datetime.now().strftime("%I:%M %p")
    st.markdown(f"""
        <div style="background-color: #0F172A; padding: 15px; border-radius: 12px; border: 1px solid #1E293B;">
            <div style="margin-bottom: 5px;"><span style="color: #94A3B8; margin-right: 6px;">📅</span> <span style="color: white;">{current_date}</span></div>
            <div><span style="color: #94A3B8; margin-right: 6px;">🕒</span> <span style="color: white;">{current_time}</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
        <div style="font-size: 11px; color: #64748B; text-align: center;">
            © 2026 HireSense-AI<br>All rights reserved
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# 3. WELCOME HERO BANNER
# =====================================================================
st.markdown("""
    <div class="hero-box">
        <p class="welcome-title">Welcome to <span style="color:#38BDF8;">HireSense-AI</span></p>
        <p class="welcome-subtitle">AI Powered Recruitment Analytics Platform</p>
        <p class="welcome-small-text">Make smarter hiring decisions with AI-driven insights</p>
        <p class="welcome-tagline">SMART • FAST • EXPLAINABLE • BIAS AWARE</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 4. MIDDLE SECTION: INTAKE WORKSPACE
# =====================================================================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="intake-header"><span>📋</span> 1. Paste Job Description</div>', unsafe_allow_html=True)
    job_desc = st.text_area(
        label="Job Description Input",
        placeholder="Enter job title, required skills, experience, qualifications, responsibilities, etc...",
        height=220,
        label_visibility="collapsed"
    )
    st.markdown("<p style='color:#94A3B8; font-size:12px;'>💡 <b>Tip:</b> More details in JD gives better AI matching results.</p>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="intake-header"><span>📤</span> 2. Upload Resumes (PDF)</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        label="Resume Uploader",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown("<p style='color:#94A3B8; font-size:12px; margin-top:8px;'>⚡ Supports bulk upload • Max 200MB per file • OCR supported</p>", unsafe_allow_html=True)

# Timeline generator function for live tracking view
def render_timeline(current_step):
    steps = ["Upload", "Parsing", "Matching", "ATS Eval", "AI Insights", "DB Save", "Completed"]
    nodes = []
    for idx, name in enumerate(steps, start=1):
        if idx < current_step:
            s_class, icon = "done", "✓"
        elif idx == current_step:
            s_class, icon = "active", "⚡"
        else:
            s_class, icon = "", str(idx)
        nodes.append(f'<div class="step-node"><div class="step-icon {s_class}">{icon}</div><div class="step-label {s_class}">{name}</div></div>')
    nodes_str = "".join(nodes)
    return f'<div class="timeline-card"><div class="timeline-title">⚡ Live Processing Status</div><div class="timeline-container">{nodes_str}</div></div>'

# Action Trigger
st.write("")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
with col_btn2:
    if st.button("🚀 Start Resume Analysis", use_container_width=True, type="primary"):
        if not job_desc or not uploaded_files:
            st.warning("⚠️ Please provide both a Job Description and at least one Resume PDF to begin.")
        else:
            timeline_placeholder = st.empty()
            
            for file in uploaded_files:
                # Step 1: Upload
                timeline_placeholder.markdown(render_timeline(1), unsafe_allow_html=True)
                time.sleep(0.3)
                
                # Step 2: Parsing
                timeline_placeholder.markdown(render_timeline(2), unsafe_allow_html=True)
                parsed_data = parser.parse_resume(file)
                raw_resume_skills = parsed_data.get("skills", [])
                time.sleep(0.3)
                
                # Step 3: Skill Matching
                timeline_placeholder.markdown(render_timeline(3), unsafe_allow_html=True)
                skill_match_report = matcher.match_skills(resume_skills=raw_resume_skills, jd_text=job_desc)
                time.sleep(0.3)
                
                # Step 4: ATS Evaluation
                timeline_placeholder.markdown(render_timeline(4), unsafe_allow_html=True)
                resume_metrics = {
                    "resume_score": float(parsed_data.get("resume_score", 70.0)),
                    "experience_score": float(parsed_data.get("experience_score", 70.0)),
                    "education_score": float(parsed_data.get("education_score", 70.0))
                }
                evaluation = engine.evaluate_candidate(resume_metrics, skill_match_report)
                time.sleep(0.3)
                
                # Step 5: AI Insights
                timeline_placeholder.markdown(render_timeline(5), unsafe_allow_html=True)
                ai_payload = {
                    "name": parsed_data.get("name", "Unknown Candidate"),
                    "education": parsed_data.get("education", "Not Found"),
                    "experience": parsed_data.get("experience", "Not Found"),
                    "ats_score": evaluation["ats_score"],
                    "Matched_Skills": skill_match_report["Matched_Skills"],
                    "Missing_Skills": skill_match_report["Missing_Skills"],
                    "Additional_Skills": skill_match_report["Additional_Skills"],
                    "resume_quality": parsed_data.get("resume_quality", "Average"),
                    "forward_to_ai": evaluation["forward_to_ai"]
                }
                ai_insights = ai_engine.generate_insights(ai_payload)
                if isinstance(ai_insights, dict) and "error" in ai_insights:
                    ai_insights = {}

                # ⭐ EXTRACT ROLE DIRECTLY FROM JOB DESCRIPTION "Job Title:" FIELD
                extracted_role = "Unknown Role"
                if job_desc:
                    for line in job_desc.split("\n"):
                        if line.lower().startswith("job title"):
                            extracted_role = line.split(":", 1)[1].strip()
                            break
                if extracted_role == "Unknown Role":
                    # Fallback to first line if Job Title prefix is missing
                    extracted_role = job_desc.strip().split("\n")[0][:35] if job_desc else "Software Engineer"

                candidate_final_record = {
                    "name": parsed_data.get("name", "Unknown"),
                    "email": parsed_data.get("email", f"candidate_{int(time.time())}@ats.com") if parsed_data.get("email") == "Not Found" else parsed_data.get("email"),
                    "role": extracted_role, 
                    "experience": parsed_data.get("experience", "Fresher"),
                    "education": parsed_data.get("education", "BCA Graduate"),
                    "location": "India",
                    "ats_score": evaluation["ats_score"],
                    "jd_match": skill_match_report["Match_Percentage_Value"],
                    "status": evaluation["recommendation"], 
                    "matched_skills": skill_match_report["Matched_Skills"],
                    "ai_summary": ai_insights.get("candidate_summary", "Summary not generated."),
                    "swot": json.dumps(ai_insights.get("swot_analysis", {})),
                    "interview_questions": json.dumps(ai_insights.get("interview_questions", [])),
                    "ai_recommendation": evaluation["recommendation"]
                }
                
                # Step 6: Database Save
                timeline_placeholder.markdown(render_timeline(6), unsafe_allow_html=True)
                db.insert_candidate(candidate_final_record)
                st.session_state.latest_candidate_data = candidate_final_record
                st.session_state.current_missing_skills = skill_match_report["Missing_Skills"]
                time.sleep(0.3)

            # Step 7: Complete Status
            timeline_placeholder.markdown(render_timeline(7), unsafe_allow_html=True)
            st.session_state.analysis_done = True
            st.success(f"✅ Successfully Processed and Auto-Saved {len(uploaded_files)} Candidate(s) to Database!")
            st.info("📌 Head over to the **📄 Resume Analyzer** page from the sidebar to inspect full diagnostic metrics and detailed breakdown reports.")

# DISPLAY BEST CANDIDATE RESULTS IF DONE (COMPACT SIZED CARDS WITH COMPACT METRICS)
if st.session_state.analysis_done:
    c_data = db.get_best_candidate()

    if c_data:
        st.markdown(
            f"<h3 style='color:white; margin-top:20px;'>🏆 Best Candidate: {c_data['name']}</h3>",
            unsafe_allow_html=True
        )

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown(f"""
            <div style="
                background:#0D1127;
                border:1px solid #1E293B;
                padding:15px;
                border-radius:12px;
                border-left:5px solid #4F46E5;
            ">
                <h4 style="color:#FFFFFF; margin-bottom:5px; margin-top:0;">
                    👤 {c_data['name']}
                </h4>
                <div style="color:#38BDF8; font-weight:600; font-size:14px; margin-top:4px;">
                    🎯 Target Position: {c_data['role']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            st.markdown(f"""
            <div style="
                background:#0D1127;
                border:1px solid #1E293B;
                padding:15px;
                border-radius:12px;
                color:#E2E8F0;
                font-size:13px;
            ">
                <div style="margin-bottom:8px;">
                    <b style="color:#94A3B8;">📧 Email:</b> {c_data['email']}
                </div>
                <div>
                    <b style="color:#94A3B8;">💼 Experience:</b> {c_data['experience']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ⭐ COMPACT METRICS REPLACING STREAMLIT DEFAULT METRICS TO PREVENT TEXT CLIPPING
        status_val = c_data["status"]
        metrics_html = f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 15px;">
            <div style="background: #0D1127; border: 1px solid #1E293B; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">🎯 ATS Score</div>
                <div style="font-size: 22px; font-weight: 900; color: #38BDF8; margin-top: 4px;">{c_data['ats_score']}%</div>
            </div>
            <div style="background: #0D1127; border: 1px solid #1E293B; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">📊 JD Match</div>
                <div style="font-size: 22px; font-weight: 900; color: #34D399; margin-top: 4px;">{c_data['jd_match']}%</div>
            </div>
            <div style="background: #0D1127; border: 1px solid #1E293B; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">📄 Status</div>
                <div style="font-size: 15px; font-weight: 800; color: #FBBF24; margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{status_val}">{status_val}</div>
            </div>
            <div style="background: #0D1127; border: 1px solid #1E293B; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Database</div>
                <div style="font-size: 14px; font-weight: 800; color: #10B981; margin-top: 8px;">✅ Saved</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

# =====================================================================
# 5. CORE PLATFORM FEATURES (ORIGINAL WHITE CARDS WITH HOVER)
# =====================================================================
st.markdown("<h3 style='color: #FFFFFF; margin-top:25px;'>✨ Core Platform Features</h3>", unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

with f_col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">AI Resume Parsing</div>
            <div class="feature-desc">Extracts candidate details, skills, education and experience from PDF resumes with OCR fallback support.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Skill Matching & ATS</div>
            <div class="feature-desc">Compares resume with JD, identifies skill gaps & calculates ATS scores.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI Insights</div>
            <div class="feature-desc">Generates candidate summaries, interview questions & AI recommendations.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💼</div>
            <div class="feature-title">Candidate Management</div>
            <div class="feature-desc">Manage leaderboards, search, filter & evaluate with Blind Hiring mode.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col5:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Recruitment Dashboard</div>
            <div class="feature-desc">Visualizes hiring KPIs, candidate statistics & analytical recruitment trends.</div>
        </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# =====================================================================
# 6. WORKFLOW DIAGRAM (ORIGINAL WHITE CARDS WITH HOVER)
# =====================================================================
st.markdown('<p class="workflow-title" style="color: #FFFFFF; font-size:18px; font-weight:800; margin-bottom:15px;">⚙️ How HireSense-AI Works</p>', unsafe_allow_html=True)
w_col1, w_col2, w_col3, w_col4, w_col5 = st.columns(5)

with w_col1:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 01</div>
            <div class="step-name">📄 Parse & Extract</div>
            <div class="step-desc">Upload PDF resumes & extract candidate details automatically.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col2:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 02</div>
            <div class="step-name">🎯 Match & Evaluate</div>
            <div class="step-desc">Matches candidate skills against the Job Description and calculates ATS scores.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col3:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 03</div>
            <div class="step-name">🤖 AI Insights</div>
            <div class="step-desc">Generate AI summaries, interview Qs & hiring recommendations.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col4:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 04</div>
            <div class="step-name">💼 Workspace & Shortlist</div>
            <div class="step-desc">Rank, compare & shortlist candidates using Blind Hiring.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col5:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 05</div>
            <div class="step-name">📊 Visual Analytics</div>
            <div class="step-desc">Visualizes recruitment KPIs, candidate statistics and hiring analytics.</div>
        </div>
    """, unsafe_allow_html=True)

# Footer Prompt
st.write("")
st.markdown("<p style='text-align:center; color:#94A3B8; font-size:13px; font-weight:600;'>💜 Ready to analyze candidates? Paste your Job Description and upload PDF resumes above to begin!</p>", unsafe_allow_html=True)