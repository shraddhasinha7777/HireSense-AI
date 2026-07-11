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

st.markdown("""
    <style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; }
    .title-text { font-size: 28px; font-weight: 800; color: #1E1B4B; margin-bottom: 0px; }
    .card { background: #FFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); margin-bottom: 15px; }
    .ats-card { background: #FFF; border: 1px solid #E2E8F0; border-top: 4px solid #4F46E5; border-radius: 12px; padding: 15px; text-align: center; height: 100%; }
    .score-val { font-size: 32px; font-weight: 900; color: #1E1B4B; margin: 4px 0; }
    .pill-green { background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin: 3px; }
    .pill-red { background: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin: 3px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🤖 HireSense-AI\nAI Powered Recruitment Analytics Platform")
    st.divider()
    st.markdown(f"#### 👤 User Profile\n**Role:** Recruitment Manager\n📅 **Date:** {datetime.now().strftime('%d %b %Y')}")
    st.divider()
    st.caption("© 2026 HireSense-AI | Enterprise ATS Architecture")

st.markdown('<p class="title-text">📄 AI Resume Analyzer & ATS Evaluation</p>', unsafe_allow_html=True)
st.write("")

col_jd, col_up = st.columns(2, gap="large")
with col_jd:
    st.markdown("**📋 1. Job Description**")
    jd_text = st.text_area("JD", placeholder="Paste target Job Description here...", height=160, label_visibility="collapsed")
with col_up:
    st.markdown("**📤 2. Upload Resume(s)**")
    uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    st.caption("⚡ Bulk Process: Upload multiple PDFs to analyze them all at once!")

# ⭐ UPGRADE: Multi-Resume Processing Loop
if st.columns([1, 1.2, 1])[1].button(f"🚀 Analyze {len(uploaded_files) if uploaded_files else ''} Resume(s)", type="primary", use_container_width=True):
    if not jd_text or not uploaded_files: 
        st.toast("⚠️ Please provide both JD and Resume(s)!", icon="🚨")
    else:
        with st.spinner(f"⚡ Bulk Processing {len(uploaded_files)} Candidate(s) & Generating AI Insights..."): 
            
            # Loop through ALL uploaded resumes
            for file in uploaded_files:
                parsed_data = parser.parse_resume(file)
                raw_resume_skills = parsed_data.get("skills", [])
                skill_match_report = matcher.match_skills(resume_skills=raw_resume_skills, jd_text=jd_text)
                
                resume_metrics = {
                    "resume_score": float(parsed_data.get("resume_score", 70.0)),
                    "experience_score": float(parsed_data.get("experience_score", 70.0)),
                    "education_score": float(parsed_data.get("education_score", 70.0))
                }
                
                evaluation = engine.evaluate_candidate(resume_metrics, skill_match_report)
                
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
                    st.toast(f"⚠️ AI Notice for {parsed_data.get('name')}: {ai_insights['error']}", icon="💡")
                    ai_insights = {}

                extracted_role = "Software Engineer"
                if isinstance(ai_insights, dict) and ai_insights.get("suitable_roles"):
                    extracted_role = ai_insights["suitable_roles"][0]
                elif jd_text and len(jd_text.strip()) > 3:
                    extracted_role = jd_text.strip().split("\n")[0][:35]

                # Serialize AI JSON Data for DB Storage
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
                    # Database AI Fields
                    "ai_summary": ai_insights.get("candidate_summary", "Summary not generated."),
                    "swot": json.dumps(ai_insights.get("swot_analysis", {})),
                    "interview_questions": json.dumps(ai_insights.get("interview_questions", [])),
                    "ai_recommendation": ai_insights.get("ai_hiring_recommendation", "")
                }
                
                # Auto-Save to Database!
                db.insert_candidate(candidate_final_record)
                
                # Keep the last one in session to display below
                st.session_state.latest_candidate_data = candidate_final_record
                st.session_state.current_missing_skills = skill_match_report["Missing_Skills"]

            st.session_state.analysis_done = True
            st.success(f"✅ Successfully Processed and Auto-Saved {len(uploaded_files)} Candidate(s) to Database!")
            st.balloons()

# 7. DISPLAY LATEST PROCESSED RESULTS
if st.session_state.analysis_done and st.session_state.latest_candidate_data:
    c_data = st.session_state.latest_candidate_data
    st.markdown(f"### 👤 Latest Processed: {c_data['name']}")
    st.markdown(f'''<div class="card" style="border-left:5px solid #4F46E5;">
        <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:15px;">
            <div><h3 style="margin:0; color:#1E1B4B;">👤 {c_data['name']}</h3><span style="color:#4F46E5; font-weight:600; font-size:13px;">Target Position: {c_data['role']}</span></div>
            <div><b>📧 Email:</b> {c_data['email']}<br><b>💼 Experience:</b> {c_data['experience']}</div>
        </div></div>''', unsafe_allow_html=True)

    a1, a2, a3, a4 = st.columns(4)
    a1.markdown(f'<div class="ats-card" style="border-top:4px solid #10B981;"><div style="font-size:11px; font-weight:700; color:#64748B;">🎯 ATS SCORE</div><div class="score-val" style="color:#10B981;">{c_data["ats_score"]}%</div></div>', unsafe_allow_html=True)
    a2.markdown(f'<div class="ats-card" style="border-top:4px solid #3B82F6;"><div style="font-size:11px; font-weight:700; color:#64748B;">📊 JD MATCH</div><div class="score-val" style="color:#3B82F6;">{c_data["jd_match"]}%</div></div>', unsafe_allow_html=True)
    a3.markdown(f'<div class="ats-card" style="border-top:4px solid #8B5CF6;"><div style="font-size:11px; font-weight:700; color:#64748B;">📄 STATUS</div><div style="font-size:20px; font-weight:800; margin:15px 0;">{c_data["status"]}</div></div>', unsafe_allow_html=True)
    a4.markdown(f'<div class="ats-card" style="border-top:4px solid #059669; background:#F0FDF4;"><div style="font-size:11px; font-weight:700; color:#64748B;">✅ DB STATUS</div><div style="background:#059669; color:#FFF; padding:6px 10px; border-radius:6px; font-weight:800; font-size:12px; margin:10px 0;">SAVED TO DB</div></div>', unsafe_allow_html=True)
    
    st.info("💡 **Note:** All uploaded candidates have been securely stored in the database. Head over to **Hiring Workspace** or **AI Insights** to view full details.")

st.divider()
with st.expander("📊 View All Database Records"):
    if st.button("🗑️ Clear Database"):
        db.clear_database()
        st.success("Database cleared successfully!")
        st.rerun()

    records = db.get_all_candidates()
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True)
    else:
        st.info("No candidates found in database.")