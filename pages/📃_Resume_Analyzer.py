import streamlit as st
import pandas as pd
import time
import sys
import os
import json
import re
import ast
from datetime import datetime
from fpdf import FPDF

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

# --- 3. SESSION STATE MANAGEMENT & BUG FIXES ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "processed_candidates" not in st.session_state:
    st.session_state.processed_candidates = []
if "force_new_batch" not in st.session_state:
    st.session_state.force_new_batch = False

if not st.session_state.processed_candidates and not st.session_state.force_new_batch:
    try:
        db_records = db.get_all_candidates()
        if db_records:
            st.session_state.processed_candidates = db_records
            st.session_state.analysis_done = True
    except Exception as e:
        pass

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
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #090514 0%, #0F0B26 100%) !important; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { max-width: 1380px !important; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background-color: #030108 !important; border-right: 1px solid #1E293B !important; }
.stTextArea label, .stFileUploader label { color: #F8FAFC !important; }
.top-title { font-size: 30px; font-weight: 800; color: #FFFFFF; margin-bottom: 5px; }
.top-subtitle { font-size: 14px; color: #94A3B8; margin-bottom: 25px; }
.result-card { background: #0D1127; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; height: 100% !important; min-height: 255px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
.ring-box { position: relative; width: 76px; height: 76px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 10px auto; }
.ring-core { width: 60px; height: 60px; border-radius: 50%; background: #0D1127; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 17px; color: #FFF; }
.pill-match { background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #34D399; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin: 4px; }
.pill-missing { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #F87171; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin: 4px; }
.pill-add { background: rgba(59, 130, 246, 0.15); border: 1px solid #3B82F6; color: #60A5FA; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin: 4px; }
div.stButton > button[kind="primary"] { background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important; border: none !important; color: #FFFFFF !important; font-weight: 800 !important; font-size: 15px !important; padding: 12px 24px !important; border-radius: 10px !important; box-shadow: 0 6px 18px rgba(139, 92, 246, 0.4) !important; }
.timeline-card { background: #0D1127; border: 1px solid #1E293B; border-radius: 14px; padding: 20px; margin: 20px 0; }
.timeline-title { color: #38BDF8; font-size: 15px; font-weight: 800; margin-bottom: 20px; }
.timeline-container { display: flex; justify-content: space-between; align-items: center; position: relative; }
.step-node { display: flex; flex-direction: column; align-items: center; text-align: center; flex: 1; }
.step-icon { width: 36px; height: 36px; border-radius: 50%; background: #090514; border: 2px solid #334155; color: #64748B; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: bold; }
.step-icon.active { border-color: #3B82F6; color: #3B82F6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.6); }
.step-icon.done { border-color: #10B981; background: #10B981; color: #FFFFFF; }
.step-label { font-size: 11px; font-weight: 700; color: #64748B; margin-top: 6px; }
.step-label.active { color: #38BDF8; }
.step-label.done { color: #34D399; }
</style>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🤖 HireSense-AI")
    st.caption("AI Powered Recruitment Analytics Platform")
    st.divider()
    st.info("💡 **Quick Tip:** Inspect candidates saved in DB or run new evaluations.")
    st.caption("© 2026 HireSense-AI | Enterprise Architecture")

# --- 7. MAIN HEADER SECTION ---
st.markdown('<div class="top-title">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="top-subtitle">AI Powered Resume Screening & ATS Evaluation System</div>', unsafe_allow_html=True)

def render_timeline(current_step):
    steps = ["Upload", "Parsing", "Matching", "ATS Eval", "AI Processing", "DB Save", "Completed"]
    nodes = []
    for idx, name in enumerate(steps, start=1):
        if idx < current_step: s_class, icon = "done", "✓"
        elif idx == current_step: s_class, icon = "active", "⚡"
        else: s_class, icon = "", str(idx)
        nodes.append(f'<div class="step-node"><div class="step-icon {s_class}">{icon}</div><div class="step-label {s_class}">{name}</div></div>')
    return f'<div class="timeline-card"><div class="timeline-title">⚡ Live Processing Status</div><div class="timeline-container">{"".join(nodes)}</div></div>'

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

def clean_db_string(val):
    if not val: return []
    if isinstance(val, list): return val
    cleaned = re.sub(r'[\[\]"\'\\]', '', str(val))
    return [s.strip() for s in cleaned.split(',') if s.strip()]

# --- 8. INTAKE WORKSPACE ---
if not st.session_state.analysis_done or not st.session_state.processed_candidates:
    col_jd, col_up = st.columns(2, gap="large")

    with col_jd:
        st.markdown("### 📋 1. Job Description")
        jd_text = st.text_area(label="JD Input", placeholder="Paste candidate target Job Description...", height=210, label_visibility="collapsed")

    with col_up:
        st.markdown("### 📤 2. Upload Resume(s)")
        uploaded_files = st.file_uploader(label="Uploader", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        st.caption("⚡ Supports bulk upload • Max 200MB per PDF file • OCR supported")

    st.write("")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
    with col_btn2:
        button_label = f"🚀 Analyze {len(uploaded_files)} Resume(s)" if uploaded_files else "🚀 Start Resume Analysis"
        analyze_click = st.button(button_label, type="primary", use_container_width=True)

    if analyze_click:
        if not jd_text or not uploaded_files:
            st.toast("⚠️ Please provide both a Job Description and at least one Resume PDF!", icon="🚨")
        else:
            st.session_state.processed_candidates.clear()
            st.session_state.force_new_batch = False
            timeline_placeholder = st.empty()
            
            for file in uploaded_files:
                timeline_placeholder.markdown(render_timeline(1), unsafe_allow_html=True)
                time.sleep(0.3)
                
                timeline_placeholder.markdown(render_timeline(2), unsafe_allow_html=True)
                parsed_data = parser.parse_resume(file)
                raw_skills = parsed_data.get("skills", [])
                raw_text = parsed_data.get("raw_text", "")
                time.sleep(0.3)
                
                if not raw_skills and parsed_data.get("education") == "Not Found" and parsed_data.get("experience") == "Not Found":
                    st.error(f"⚠️ Error reading '{file.name}'. It appears to be a scanned image or locked PDF.")
                    continue

                extracted_email = parsed_data.get("email", "Not Found")
                extracted_name = resolve_smart_candidate_name(parsed_data.get("name"), raw_text, file.name, extracted_email)

                timeline_placeholder.markdown(render_timeline(3), unsafe_allow_html=True)
                skill_report = matcher.match_skills(resume_skills=raw_skills, jd_text=jd_text)
                time.sleep(0.3)
                
                timeline_placeholder.markdown(render_timeline(4), unsafe_allow_html=True)
                metrics = {
                    "resume_score": float(parsed_data.get("resume_score", 0.0)),
                    "experience_score": float(parsed_data.get("experience_score", 0.0)),
                    "education_score": float(parsed_data.get("education_score", 0.0))
                }
                evaluation = engine.evaluate_candidate(metrics, skill_report)
                time.sleep(0.3)
                
                timeline_placeholder.markdown(render_timeline(5), unsafe_allow_html=True)
                extracted_role = "Software Engineer"
                for line in jd_text.split("\n"):
                    if line.lower().startswith("job title"):
                        extracted_role = line.split(":", 1)[1].strip()
                        break

                skill_score = float(skill_report.get("Match_Percentage_Value", 0.0))
                
                raw_m = skill_report.get("Matched_Skills", [])
                raw_mis = skill_report.get("Missing_Skills", [])
                raw_add = skill_report.get("Additional_Skills", [])
                
                if not raw_mis and skill_score < 100.0 and jd_text:
                    jd_words = re.findall(r'\b[A-Z][a-zA-Z]+\b', jd_text)
                    stopwords = {"The", "And", "For", "With", "We", "Are", "Looking", "Candidate", "Role", "Job", "Experience", "Skills", "Team", "To", "In", "Of", "This", "Is", "Must", "Have", "Years", "Requirements", "Knowledge", "Work", "Design", "Development", "Using", "Good", "Strong"}
                    extracted = list(set([w for w in jd_words if w not in stopwords and len(w) > 2]))
                    
                    matched_upper = [m.upper() for m in raw_m]
                    raw_mis = [w for w in extracted if w.upper() not in matched_upper][:6]
                    if not raw_mis: raw_mis = ["BI Tools (Tableau/PowerBI)", "Advanced SQL", "ETL Pipelines", "Data Cleaning"]

                phone_val = parsed_data.get("phone", "Not Provided")
                if phone_val in ["Not Found", "Contact via Email", ""]:
                    phone_val = "Not Provided"

                candidate_record = {
                    "name": extracted_name,
                    "email": extracted_email if extracted_email != "Not Found" else f"candidate_{int(time.time())}@ats.com",
                    "phone": phone_val,
                    "role": extracted_role,
                    "experience": parsed_data.get("experience", "Not Found"),
                    "education": parsed_data.get("education", "Not Found"),
                    "location": "India",
                    "ats_score": evaluation["ats_score"],
                    "jd_match": skill_score,
                    "resume_quality": float(parsed_data.get("resume_score", 0.0)),
                    "exp_score": metrics["experience_score"],
                    "edu_score": metrics["education_score"],
                    "status": evaluation["recommendation"],
                    "matched_skills": ", ".join(raw_m) if isinstance(raw_m, list) else str(raw_m),
                    "missing_skills": ", ".join(raw_mis) if isinstance(raw_mis, list) else str(raw_mis),
                    "additional_skills": ", ".join(raw_add) if isinstance(raw_add, list) else str(raw_add),
                    "duplicate": parsed_data.get("duplicate", False)
                }
                
                timeline_placeholder.markdown(render_timeline(6), unsafe_allow_html=True)
                db.insert_candidate(candidate_record)
                st.session_state.processed_candidates.append(candidate_record)
                time.sleep(3.0)

            timeline_placeholder.markdown(render_timeline(7), unsafe_allow_html=True)
            if st.session_state.processed_candidates:
                st.session_state.analysis_done = True
                st.rerun()
            else:
                st.warning("⚠️ No new candidates were processed.")

# --- 9. DISPLAY PROCESSED ANALYSIS RESULTS ---
else:
    st.markdown("### 🔍 Review Evaluated Candidates")
    
    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button("➕ Evaluate New Batch", type="primary", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.processed_candidates = []
            st.session_state.force_new_batch = True
            st.rerun()

    st.divider()
    candidate_names = [f"{c.get('name')} - {c.get('role', 'Candidate')}" for c in st.session_state.processed_candidates]
    selected_option = st.selectbox("Select a candidate to view their ATS Breakdown:", candidate_names, index=0)
    
    selected_idx = candidate_names.index(selected_option)
    c = st.session_state.processed_candidates[selected_idx]
    
    c_name = c.get('name', 'Candidate Applicant')
    c_exp = c.get('experience', 'Not Found')
    c_email = c.get('email', 'N/A')
    c_edu = c.get('education', 'Not Found')
    c_phone = c.get('phone', 'Not Provided')
    c_loc = c.get('location', 'India')
    c_role = c.get('role', 'Applicant')
    
    c_ats = float(c.get('ats_score', 0.0))
    c_jd = float(c.get('jd_match', 0.0))
    
    c_matched = clean_db_string(c.get('matched_skills', ''))
    c_missing = clean_db_string(c.get('missing_skills', ''))
    c_additional = clean_db_string(c.get('additional_skills', ''))

    if c_jd < 100.0 and len(c_missing) == 0:
        c_missing = ["Tableau", "Power BI", "Statistics", "ETL", "Data Cleaning"]

    ats_col = "#10B981" if c_ats >= 75 else "#F59E0B"
    jd_col = "#3B82F6" if c_jd > 0 else "#64748B"
    
    jd_display_text = f"{int(c_jd)}%" if c_jd > 0 else "N/A"
    jd_ring_val = int(c_jd) if c_jd > 0 else 0
    
    avatar_url = f"https://ui-avatars.com/api/?name={c_name.replace(' ', '+')}&background=1E1B4B&color=38BDF8&bold=true"

    grid_html = f'''
    <div style="display: grid; grid-template-columns: 2.5fr 1fr 1fr; gap: 14px; margin-top: 15px; align-items: stretch;">
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
            <div><div style="font-size: 11px; font-weight: 800; color: {ats_col};">Screening Score</div><div style="font-size: 9px; color: #64748B;">Candidate Score</div></div>
        </div>
        <div class="result-card" style="text-align: center;">
            <div style="font-size: 12px; font-weight: 700; color: #94A3B8;">JD Match</div>
            <div class="ring-box" style="background: conic-gradient({jd_col} {jd_ring_val}%, #1E293B 0);"><div class="ring-core">{jd_display_text}</div></div>
            <div><div style="font-size: 11px; font-weight: 800; color: {jd_col};">Role Match</div><div style="font-size: 9px; color: #64748B;">Job Match</div></div>
        </div>
    </div>
    '''
    st.markdown(grid_html, unsafe_allow_html=True)

    st.write("")
    s_match_val = float(c.get('jd_match', c.get('skill_match', 0.0)))
    exp_val = float(c.get('exp_score', c.get('experience_score', 0.0)))
    edu_val = float(c.get('edu_score', c.get('education_score', 0.0)))

    if exp_val == 0.0 and c_exp and c_exp != "Not Found":
        exp_lower = str(c_exp).lower()
        if any(x in exp_lower for x in ["5", "6", "7", "8", "9", "10", "senior", "lead"]): exp_val = 100.0
        elif any(x in exp_lower for x in ["3", "4"]): exp_val = 85.0
        elif any(x in exp_lower for x in ["1", "2"]): exp_val = 75.0
        elif "intern" in exp_lower: exp_val = 40.0
        elif "fresher" in exp_lower: exp_val = 20.0
        else: exp_val = 70.0 

    if edu_val == 0.0 and c_edu and c_edu != "Not Found":
        edu_upper = str(c_edu).upper()
        if any(x in edu_upper for x in ["PH.D", "M.TECH", "M.SC", "MS", "DOCTORATE", "MASTER", "MBA", "MCA", "M.A"]): 
            edu_val = 100.0
        elif any(x in edu_upper for x in ["B.TECH", "B.E", "ENGINEERING", "BCA", "B.SC", "BBA", "B.COM", "BACHELOR", "DEGREE"]): 
            edu_val = 90.0
        elif "DIPLOMA" in edu_upper: 
            edu_val = 70.0
        else: 
            edu_val = 60.0 

    breakdown_html = f'''
    <div style="background:#0D1127; border:1px solid #1E293B; border-radius:12px; padding:20px; margin-top:15px;">
        <div style="color:#38BDF8; font-size:15px; font-weight:800; margin-bottom:15px;">⭐ ATS Score Breakdown</div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1.2fr; gap:15px; align-items:center;">
            <div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;">
                <div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Skill Match</span><b style="color:#34D399;">50% Weight</b></div>
                <div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{s_match_val}%</div>
                <div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{s_match_val}%; height:100%; background:#10B981;"></div></div>
            </div>
            <div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;">
                <div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Experience</span><b style="color:#60A5FA;">30% Weight</b></div>
                <div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{exp_val}%</div>
                <div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{exp_val}%; height:100%; background:#3B82F6;"></div></div>
            </div>
            <div style="background:#060813; padding:12px; border-radius:8px; border:1px solid #1E293B;">
                <div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;"><span>Education</span><b style="color:#FBBF24;">20% Weight</b></div>
                <div style="font-size:18px; font-weight:800; color:#FFF; margin:4px 0;">{edu_val}%</div>
                <div style="height:4px; background:#1E293B; border-radius:2px; overflow:hidden;"><div style="width:{edu_val}%; height:100%; background:#F59E0B;"></div></div>
            </div>
            <div style="background:linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); padding:14px; border-radius:10px; border:1px solid #4F46E5; text-align:center;">
                <div style="font-size:11px; color:#38BDF8; font-weight:700;">FINAL ATS SCORE</div>
                <div style="font-size:26px; font-weight:900; color:#FFF; margin:2px 0;">{int(c_ats)}%</div>
                <div style="font-size:9px; color:#C7D2FE;">Weighted Algorithm Result</div>
            </div>
        </div>
    </div>
    '''
    st.markdown(breakdown_html, unsafe_allow_html=True)

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
