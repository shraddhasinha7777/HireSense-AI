import streamlit as st
import pandas as pd
import time
import sys
import os
import json
import re
from datetime import datetime
from fpdf import FPDF  # Added FPDF for PDF generation

# --- 1. PATH SETUP & MODULE IMPORTS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from resume_parser import ResumeParser
from ats_engine import ATSEngine
from skill_matcher import SkillMatcher
from ai_service import AIService

# --- 2. ENGINE INITIALIZATION ---
db = Database()
parser = ResumeParser()
engine = ATSEngine()
matcher = SkillMatcher()
ai_engine = AIService()

# --- 3. SESSION STATE MANAGEMENT ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "latest_candidate_data" not in st.session_state:
    st.session_state.latest_candidate_data = {}

# --- 4. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Resume Analyzer | HireSense-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 5. PREMIUM DARK CUSTOM STYLING ---
st.markdown("""
<style>
/* Main Dark Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #090514 0%, #0F0B26 100%) !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
.block-container { 
    max-width: 1380px !important; 
    padding-top: 1.5rem; 
    padding-bottom: 3rem; 
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #030108 !important;
    border-right: 1px solid #1E293B !important;
}
.stTextArea label, .stFileUploader label {
    color: #F8FAFC !important;
}

/* Page Headers */
.top-title {
    font-size: 30px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 5px;
}
.top-subtitle {
    font-size: 14px;
    color: #94A3B8;
    margin-bottom: 25px;
}

/* Result Cards - Uniform Height & Spacing */
.result-card {
    background: #0D1127;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 18px;
    height: 100% !important;
    min-height: 255px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

/* Gauge Rings */
.ring-box {
    position: relative;
    width: 76px;
    height: 76px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 10px auto;
}
.ring-core {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #0D1127;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 17px;
    color: #FFF;
}

/* Skill Badges */
.pill-match {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
    color: #34D399;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 4px;
}
.pill-missing {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid #EF4444;
    color: #F87171;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 4px;
}
.pill-add {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3B82F6;
    color: #60A5FA;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 4px;
}

/* Primary Button */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    border-radius: 10px !important;
    box-shadow: 0 6px 18px rgba(139, 92, 246, 0.4) !important;
}

/* Live Processing Stepper */
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

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🤖 HireSense-AI")
    st.caption("AI Powered Recruitment Analytics Platform")
    st.divider()
    
    st.markdown("#### 👤 User Profile")
    st.write("**Role:** Recruitment Manager")
    st.write(f"📅 **Date:** {datetime.now().strftime('%d %b %Y')}")
    st.divider()
    
    st.info("💡 **Quick Tip:** Paste JD & upload resumes to generate ATS Breakdown & AI Insights.")
    st.caption("© 2026 HireSense-AI | Enterprise Architecture")

# --- 7. MAIN HEADER SECTION ---
st.markdown('<div class="top-title">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="top-subtitle">AI Powered Resume Screening & ATS Evaluation System</div>', unsafe_allow_html=True)

# --- 8. INTAKE WORKSPACE ---
col_jd, col_up = st.columns(2, gap="large")

with col_jd:
    st.markdown("### 📋 1. Job Description")
    jd_text = st.text_area(
        label="JD Input",
        placeholder="Paste candidate target Job Description (skills, experience, responsibilities)...",
        height=210,
        label_visibility="collapsed"
    )
    st.caption("💡 Tip: Providing detailed requirements improves AI matching accuracy.")

with col_up:
    st.markdown("### 📤 2. Upload Resume(s)")
    uploaded_files = st.file_uploader(
        label="Uploader",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.caption("⚡ Supports bulk upload • Max 200MB per PDF file • OCR supported")

st.write("")

# Dynamic Timeline Generator
def render_timeline(current_step):
    steps = ["Upload", "Parsing", "Matching", "ATS Eval", "AI Processing", "DB Save", "Completed"]
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

# Helper Function: Smart Name Extraction Algorithm
def resolve_smart_candidate_name(parsed_name, raw_resume_text, file_name, extracted_email):
    if parsed_name and parsed_name not in ["Unknown Candidate", "Unknown", "Not Found", "None"] and not str(parsed_name).isdigit():
        return str(parsed_name).title()
    
    if raw_resume_text:
        lines = [line.strip() for line in raw_resume_text.split('\n') if line.strip()]
        ignored_words = ["RESUME", "CURRICULUM", "VITAE", "CAREER", "CENTER", "OHIO", "STATE", "UNIVERSITY", "EDUCATION", "SUMMARY", "EXPERIENCE", "PROFILE"]
        
        for line in lines[:10]:
            clean_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            words = clean_line.split()
            if 2 <= len(words) <= 3 and all(w.isupper() or w.istitle() for w in words):
                if not any(ign in clean_line.upper() for ign in ignored_words):
                    return clean_line.title()

    if extracted_email and extracted_email != "Not Found" and "@" in str(extracted_email):
        prefix = str(extracted_email).split("@")[0]
        clean_prefix = re.sub(r'[^a-zA-Z]', ' ', prefix).strip()
        if len(clean_prefix.split()) >= 1 and not clean_prefix.isdigit():
            return clean_prefix.title()

    base_file = os.path.splitext(file_name)[0]
    clean_filename = re.sub(r'[^a-zA-Z]', ' ', base_file).strip()
    if len(clean_filename) > 2 and not clean_filename.isdigit():
        return clean_filename.title()

    return "Candidate Applicant"

# Helper Function: Generate PDF Report
def generate_pdf_report(c):
    def clean_text(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="HIRESENSE-AI EVALUATION REPORT", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Candidate Name: {clean_text(c.get('name', 'N/A'))}", ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=f"Target Role: {clean_text(c.get('role', 'N/A'))}", ln=True)
    pdf.cell(200, 8, txt=f"Experience: {clean_text(c.get('experience', 'N/A'))}", ln=True)
    pdf.cell(200, 8, txt=f"Education: {clean_text(c.get('education', 'N/A'))}", ln=True)
    pdf.cell(200, 8, txt=f"ATS Score: {c.get('ats_score', 0)}%", ln=True)
    pdf.cell(200, 8, txt=f"JD Match: {c.get('jd_match', 0)}%", ln=True)
    pdf.cell(200, 8, txt=f"Status: {clean_text(c.get('status', 'N/A'))}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Skills Analysis", ln=True)
    pdf.set_font("Arial", '', 11)
    
    matched = c.get('matched_skills', [])
    if isinstance(matched, str): matched = matched.split(',')
    matched_str = clean_text(", ".join(matched) if matched else "None")
    
    missing = c.get('missing_skills', [])
    if isinstance(missing, str): missing = missing.split(',')
    missing_str = clean_text(", ".join(missing) if missing else "None")

    pdf.multi_cell(0, 8, txt=f"Matched Skills: {matched_str}")
    pdf.multi_cell(0, 8, txt=f"Missing Skills: {missing_str}")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="AI Summary", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=clean_text(c.get('ai_summary', 'N/A')))

    try:
        return bytes(pdf.output(dest='S').encode('latin-1'))
    except Exception:
        return pdf.output(dest='S')

# --- 9. ANALYSIS TRIGGER LOGIC ---
col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
with col_btn2:
    button_label = f"🚀 Analyze {len(uploaded_files)} Resume(s)" if uploaded_files else "🚀 Start Resume Analysis"
    analyze_click = st.button(button_label, type="primary", use_container_width=True)

if analyze_click:
    if not jd_text or not uploaded_files:
        st.toast("⚠️ Please provide both a Job Description and at least one Resume PDF!", icon="🚨")
    else:
        timeline_placeholder = st.empty()
        
        for file in uploaded_files:
            # Step 1: Upload
            timeline_placeholder.markdown(render_timeline(1), unsafe_allow_html=True)
            time.sleep(0.4)
            
            # Step 2: Parsing
            timeline_placeholder.markdown(render_timeline(2), unsafe_allow_html=True)
            parsed_data = parser.parse_resume(file)
            raw_skills = parsed_data.get("skills", [])
            raw_text = parsed_data.get("raw_text", "")
            time.sleep(0.4)
            
            extracted_email = parsed_data.get("email", "Not Found")
            extracted_name = resolve_smart_candidate_name(
                parsed_name=parsed_data.get("name"),
                raw_resume_text=raw_text,
                file_name=file.name,
                extracted_email=extracted_email
            )

            # Step 3: Skill Matching
            timeline_placeholder.markdown(render_timeline(3), unsafe_allow_html=True)
            skill_report = matcher.match_skills(resume_skills=raw_skills, jd_text=jd_text)
            time.sleep(0.4)
            
            # Step 4: ATS Evaluation
            timeline_placeholder.markdown(render_timeline(4), unsafe_allow_html=True)
            metrics = {
                "resume_score": float(parsed_data.get("resume_score", 75.0)),
                "experience_score": float(parsed_data.get("experience_score", 70.0)),
                "education_score": float(parsed_data.get("education_score", 80.0))
            }
            evaluation = engine.evaluate_candidate(metrics, skill_report)
            time.sleep(0.4)
            
            # Step 5: AI Processing (Role extracted directly from JD "Job Title:")
            timeline_placeholder.markdown(render_timeline(5), unsafe_allow_html=True)
            
            extracted_role = "Unknown Role"
            if jd_text:
                for line in jd_text.split("\n"):
                    if line.lower().startswith("job title"):
                        extracted_role = line.split(":", 1)[1].strip()
                        break
            if extracted_role == "Unknown Role":
                extracted_role = jd_text.strip().split("\n")[0][:35] if jd_text else "Software Engineer"

            ai_payload = {
                "name": extracted_name,
                "education": parsed_data.get("education", "Not Found"),
                "experience": parsed_data.get("experience", "Not Found"),
                "ats_score": evaluation["ats_score"],
                "role": extracted_role,
                "Matched_Skills": skill_report["Matched_Skills"],
                "Missing_Skills": skill_report["Missing_Skills"],
                "Additional_Skills": skill_report["Additional_Skills"]
            }
            ai_insights = ai_engine.generate_insights(ai_payload)
            if isinstance(ai_insights, dict) and "error" in ai_insights:
                ai_insights = {}

            skill_score = float(skill_report.get("Match_Percentage_Value", 60.0))
            resume_quality_num = float(parsed_data.get("resume_score", 83.0))
            exp_score_num = float(parsed_data.get("experience_score", 75.0))
            edu_score_num = float(parsed_data.get("education_score", 80.0))

            phone_val = parsed_data.get("phone", "Not Provided")
            if phone_val == "Not Found" or not phone_val:
                phone_val = "Contact via Email"

            candidate_record = {
                "name": extracted_name,
                "email": extracted_email if extracted_email != "Not Found" else f"candidate_{int(time.time())}@ats.com",
                "phone": phone_val,
                "role": extracted_role,
                "experience": parsed_data.get("experience", "Fresher"),
                "education": parsed_data.get("education", "Bachelor Degree"),
                "location": parsed_data.get("location", "India") if parsed_data.get("location") != "Not Found" else "India",
                "ats_score": evaluation["ats_score"],
                "jd_match": skill_score,
                "resume_quality": resume_quality_num,
                "exp_score": exp_score_num,
                "edu_score": edu_score_num,
                "status": evaluation["recommendation"],
                "matched_skills": skill_report["Matched_Skills"],
                "missing_skills": skill_report["Missing_Skills"],
                "additional_skills": skill_report.get("Additional_Skills", []),
                "ai_summary": ai_insights.get("candidate_summary", f"Candidate profile analyzed for {extracted_role}. Demonstrates aligned skills with core requirements."),
                "swot": json.dumps(ai_insights.get("swot_analysis", {})),
                "interview_questions": json.dumps(ai_insights.get("interview_questions", [])),
                "ai_recommendation": ai_insights.get("ai_hiring_recommendation", "Candidate matches key requirements. Suitable for technical screening."),
                "duplicate": parsed_data.get("duplicate", False)
            }
            
            # ⭐ STEP 6: DATABASE SAVE WITH DATABASE-DRIVEN DUPLICATE FEEDBACK
            timeline_placeholder.markdown(render_timeline(6), unsafe_allow_html=True)
            saved = db.insert_candidate(candidate_record)
            if not saved:
                st.error("❌ Duplicate candidate detected! Record already exists in the database.")
            else:
                st.session_state.latest_candidate_data = candidate_record
            time.sleep(0.4)

        # Step 7: Complete Status
        timeline_placeholder.markdown(render_timeline(7), unsafe_allow_html=True)
        st.session_state.analysis_done = True
        st.success(f"✅ Successfully analyzed and processed {len(uploaded_files)} candidate(s)!")

# --- 10. DISPLAY PROCESSED ANALYSIS RESULTS ---
if st.session_state.analysis_done and st.session_state.latest_candidate_data:
    c = st.session_state.latest_candidate_data
    st.divider()
    
    # ⭐ SAFE GETTERS TO PREVENT ANY KEYERROR
    c_name = c.get('name', 'Candidate Applicant')
    c_exp = c.get('experience', 'Fresher')
    c_email = c.get('email', 'N/A')
    c_edu = c.get('education', 'Graduate')
    c_phone = c.get('phone', 'Contact via Email')
    c_loc = c.get('location', 'India')
    c_role = c.get('role', 'Applicant')
    
    c_ats = float(c.get('ats_score', 0))
    c_jd = float(c.get('jd_match', 0))
    c_q = float(c.get('resume_quality', 80))
    c_status = c.get('status', 'Evaluated')
    
    c_matched = c.get('matched_skills', [])
    c_missing = c.get('missing_skills', [])
    c_additional = c.get('additional_skills', [])

    ats_col = "#10B981" if c_ats >= 75 else "#F59E0B"
    jd_col = "#3B82F6" if c_jd >= 70 else "#F59E0B"
    q_col = "#8B5CF6"
    
    rec_color = "#10B981" if "Shortlist" in c_status or "Recommend" in c_status else "#F59E0B"
    avatar_url = f"https://ui-avatars.com/api/?name={c_name.replace(' ', '+')}&background=1E1B4B&color=38BDF8&bold=true"

    # ⭐ UNIFORM GRID HEIGHT & ALIGNMENT STYLING (FIXES GAP & HEIGHT MISMATCH)
    grid_html = f'''
    <div style="display: grid; grid-template-columns: 2.2fr 1fr 1fr 1fr 1.4fr; gap: 14px; margin-top: 15px; align-items: stretch;">
        <div class="result-card" style="padding: 18px;">
            <div style="color: #38BDF8; font-size: 13px; font-weight: 800; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">👤 Candidate Information</div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="{avatar_url}" style="width: 65px; height: 65px; border-radius: 50%; border: 2px solid #38BDF8;">
                <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 8px 12px; font-size: 11px;">
                    <div><span style="color: #64748B;">👤 Name</span><br><b style="color: #FFF; font-size: 12px;">{c_name}</b></div>
                    <div><span style="color: #64748B;">💼 Experience</span><br><b style="color: #E2E8F0;">{c_exp}</b></div>
                    <div><span style="color: #64748B;">📧 Email</span><br><b style="color: #E2E8F0; font-size: 10px;">{c_email}</b></div>
                    <div><span style="color: #64748B;">🎓 Education</span><br><b style="color: #E2E8F0; font-size: 10px;">{c_edu}</b></div>
                    <div><span style="color: #64748B;">📞 Phone</span><br><b style="color: #E2E8F0;">{c_phone}</b></div>
                    <div><span style="color: #64748B;">📍 Location</span><br><b style="color: #38BDF8;">{c_loc}</b></div>
                    <div style="grid-column: span 2;"><span style="color: #64748B;">👔 Role</span><br><b style="color: #38BDF8; font-size: 11px;">{c_role}</b></div>
                </div>
            </div>
        </div>
        <div class="result-card" style="text-align: center;">
            <div style="font-size: 12px; font-weight: 700; color: #94A3B8;">ATS Score</div>
            <div class="ring-box" style="background: conic-gradient({ats_col} {c_ats}%, #1E293B 0);"><div class="ring-core">{int(c_ats)}%</div></div>
            <div><div style="font-size: 11px; font-weight: 800; color: {ats_col};">ATS Evaluation</div><div style="font-size: 9px; color: #64748B;">Score Rank</div></div>
        </div>
        <div class="result-card" style="text-align: center;">
            <div style="font-size: 12px; font-weight: 700; color: #94A3B8;">JD Match</div>
            <div class="ring-box" style="background: conic-gradient({jd_col} {c_jd}%, #1E293B 0);"><div class="ring-core">{int(c_jd)}%</div></div>
            <div><div style="font-size: 11px; font-weight: 800; color: {jd_col};">Skill Overlap</div><div style="font-size: 9px; color: #64748B;">Relevance Match</div></div>
        </div>
        <div class="result-card" style="text-align: center;">
            <div style="font-size: 12px; font-weight: 700; color: #94A3B8;">Resume Quality</div>
            <div class="ring-box" style="background: conic-gradient({q_col} {int(c_q)}%, #1E293B 0);"><div class="ring-core">{int(c_q)}%</div></div>
            <div><div style="font-size: 11px; font-weight: 800; color: {q_col};">Formatting</div><div style="font-size: 9px; color: #64748B;">Well Structured</div></div>
        </div>
        <div class="result-card">
            <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-align: center;">Recommendation</div>
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid {rec_color}; color: {rec_color}; padding: 12px; border-radius: 8px; text-align: center; margin-top: auto; margin-bottom: auto;">
                <div style="font-weight: 800; font-size: 13px;">★ {c_status}</div>
                <div style="font-size: 10px; color: #94A3B8; margin-top:4px;">Evaluated by Engine</div>
            </div>
        </div>
    </div>
    '''
    st.markdown(grid_html, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 🔥 SECTION 6 — ATS SCORE BREAKDOWN ⭐⭐⭐⭐⭐
    # -------------------------------------------------------------
    st.write("")
    s_match_val = c.get('jd_match', 70.0)
    q_val = c.get('resume_quality', 80.0)
    exp_val = c.get('exp_score', 75.0)
    edu_val = c.get('edu_score', 80.0)

    breakdown_html = f'<div style="background:#0D1127; border:1px solid #1E293B; border-radius:12px; padding:20px; margin-top:15px;"><div style="color:#38BDF8; font-size:15px; font-weight:800; margin-bottom:15px;">⭐ ATS Score Breakdown</div><div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr 1.2fr; gap:15px; align-items:center;"><div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Skill Match</span><b style="color:#34D399;">40% Weight</b></div><div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{s_match_val}%</div><div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{s_match_val}%; height:100%; background:#10B981;"></div></div></div><div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Resume Quality</span><b style="color:#A78BFA;">30% Weight</b></div><div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{q_val}%</div><div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{q_val}%; height:100%; background:#8B5CF6;"></div></div></div><div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Experience</span><b style="color:#60A5FA;">20% Weight</b></div><div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{exp_val}%</div><div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{exp_val}%; height:100%; background:#3B82F6;"></div></div></div><div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Education</span><b style="color:#FBBF24;">10% Weight</b></div><div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{edu_val}%</div><div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{edu_val}%; height:100%; background:#F59E0B;"></div></div></div><div style="background:linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); padding:14px; border-radius:10px; border:1px solid #4F46E5; text-align:center;"><div style="font-size:11px; color:#38BDF8; font-weight:700;">FINAL ATS SCORE</div><div style="font-size:26px; font-weight:900; color:#FFF; margin:2px 0;">{int(c_ats)}%</div><div style="font-size:9px; color:#C7D2FE;">Weighted Algorithm Result</div></div></div></div>'
    st.markdown(breakdown_html, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 🔥 SECTION 7 — SKILLS (3 BADGES CARDS)
    # -------------------------------------------------------------
    st.write("")
    sk1, sk2, sk3 = st.columns(3)
    
    with sk1:
        st.markdown("#### 🟢 Matched Skills")
        matched_html = "".join([f'<span class="pill-match">✓ {s}</span>' for s in c_matched]) if c_matched else "<p style='color:#94A3B8; font-size:12px;'>No direct matched skills found.</p>"
        st.markdown(f'<div style="background:#0D1127; border:1px solid #1E293B; border-radius:12px; padding:15px; min-height:110px;">{matched_html}</div>', unsafe_allow_html=True)

    with sk2:
        st.markdown("#### 🔴 Missing Skills")
        missing_html = "".join([f'<span class="pill-missing">✗ {s}</span>' for s in c_missing]) if c_missing else "<p style='color:#94A3B8; font-size:12px;'>No critical skills missing!</p>"
        st.markdown(f'<div style="background:#0D1127; border:1px solid #1E293B; border-radius:12px; padding:15px; min-height:110px;">{missing_html}</div>', unsafe_allow_html=True)

    with sk3:
        st.markdown("#### 🔵 Additional Skills")
        add_html = "".join([f'<span class="pill-add">+ {s}</span>' for s in c_additional]) if c_additional else "<p style='color:#94A3B8; font-size:12px;'>No additional candidate skills detected.</p>"
        st.markdown(f'<div style="background:#0D1127; border:1px solid #1E293B; border-radius:12px; padding:15px; min-height:110px;">{add_html}</div>', unsafe_allow_html=True)

    # 🔥 SECTION 9 — EXPORT
    # -------------------------------------------------------------
    st.write("")
    st.markdown("### 📥 Export Candidate Report")
    
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    
    with exp_col1:
        report_text = f"HIRESENSE-AI EVALUATION REPORT\n-------------------------------\nCandidate Name: {c_name}\nTarget Role   : {c_role}\nATS Score     : {c_ats}%\nJD Match      : {c_jd}%\nStatus        : {c_status}\nEmail         : {c_email}\nPhone         : {c_phone}\nDate          : {datetime.now().strftime('%d %b %Y')}\n"
        st.download_button(
            label="📄 Download Analysis Report (.TXT)",
            data=report_text,
            file_name=f"{c_name.replace(' ', '_')}_ATS_Report.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with exp_col2:
        df_single = pd.DataFrame([c])
        csv_data = df_single.to_csv(index=False)
        st.download_button(
            label="📊 Export Candidate Data (.CSV)",
            data=csv_data,
            file_name=f"{c_name.replace(' ', '_')}_Data.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col3:
        pdf_bytes = generate_pdf_report(c)
        st.download_button(
            label="📑 Download PDF Report (.PDF)",
            data=pdf_bytes,
            file_name=f"{c_name.replace(' ', '_')}_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )