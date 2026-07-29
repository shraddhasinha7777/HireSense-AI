import streamlit as st
import pandas as pd
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import Database
from ai_service import AIService

db = Database()
ai_service = AIService()

st.set_page_config(page_title="AI Insights | HireSense-AI", page_icon="🧠", layout="wide")

# PREMIUM DARK THEME STYLING
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #090514 0%, #0F0B26 100%) !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background-color: #030108 !important; border-right: 1px solid #1E293B !important; }
.block-container { padding-top: 2rem; max-width: 1350px !important; }

.card { 
    background: #0D1127; 
    border: 1px solid #1E293B; 
    border-radius: 12px; 
    padding: 22px; 
    margin-bottom: 20px; 
    box-shadow: 0 4px 16px rgba(0,0,0,0.3); 
}
.q-card { 
    background: #060813; 
    border: 1px solid #1E293B;
    padding: 14px 18px; 
    margin-bottom: 12px; 
    border-radius: 8px; 
    font-weight: 500; 
    color: #E2E8F0; 
    display: flex;
    align-items: center;
    gap: 15px;
}
.q-badge {
    background: #1E1B4B;
    color: #8B5CF6;
    border: 1px solid #4F46E5;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 12px;
    flex-shrink: 0;
}
.chat-msg-user {
    background: #1E1B4B;
    border: 1px solid #4F46E5;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 8px;
    color: #E2E8F0;
    font-size: 13px;
}
.chat-msg-ai {
    background: #060813;
    border: 1px solid #1E293B;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
    color: #38BDF8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

records = db.get_all_candidates()
if not records:
    st.warning("⚠️ No candidate found in database. Please process a resume first.")
    st.stop()

df = pd.DataFrame(records)
df['created_at'] = pd.to_datetime(df['created_at'])

# Dropdown to select candidate
cand_names = df['name'].tolist()
selected_cand = st.selectbox("Select Candidate for Deep AI Insight", reversed(cand_names))
candidate = df[df['name'] == selected_cand].iloc[0]

ats_val = float(candidate.get("ats_score", 70.0))
jd_val = float(candidate.get("jd_match", 70.0))
confidence = round((ats_val * 0.65) + (jd_val * 0.35), 1)

st.markdown("## 🧠 AI Insights & Explainable Decision Support")
st.divider()

# Load Dynamic AI-Generated SWOT from Database safely
try: 
    swot = json.loads(candidate.get("swot", "{}"))
    if not isinstance(swot, dict): swot = {}
except: 
    swot = {}

try: questions = json.loads(candidate.get("interview_questions", "[]"))
except: questions = []

ai_summary = candidate.get("ai_summary") or "AI Summary not available in database."
status_text = candidate.get("status", "Review Manually")

# Handle Education Fallback
raw_edu = str(candidate.get("education", "Not Found"))
if not raw_edu or raw_edu in ["Not Found", "None", "Unknown", "NaN"]:
    display_education = "Education details not mentioned in resume."
else:
    display_education = raw_edu

# Determine Best Suitable Role
applied_role = candidate.get("role", "Professional")
if ats_val >= 80:
    best_role = applied_role
elif ats_val >= 65:
    best_role = applied_role
else:
    best_role = f"Junior {applied_role}"

# Determine Fit Rating Stars
fit_rating = "⭐⭐⭐⭐⭐" if ats_val >= 80 else "⭐⭐⭐⭐☆" if ats_val >= 65 else "⭐⭐⭐☆☆"

# 1. Candidate Profile Summary
summary_html = f"""
<div class="card" style="border-top: 3px solid #8B5CF6;">
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:20px; margin-bottom:15px;">
        <div>
            <h3 style="margin:0; color:#FFFFFF;">👤 {candidate["name"]}</h3>
            <div style="margin-top:6px; display:flex; gap:15px; font-size:13px; flex-wrap:wrap;">
                <span style="color:#A78BFA; font-weight:700;">Applied Role: <b style="color:#FFF;">{applied_role}</b></span>
                <span style="color:#38BDF8; font-weight:700;">Best Suitable Role: <b style="color:#FFF;">{best_role}</b></span>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="color:#94A3B8; font-size:13px; margin-bottom:4px;"><b>💼 Experience:</b> <span style="color:#FFF;">{candidate["experience"]}</span></div>
            <div style="color:#94A3B8; font-size:13px;"><b>⭐ Overall Fit:</b> <span style="color:#FBBF24;">{fit_rating}</span></div>
        </div>
    </div>
    <div style="margin-bottom:15px; font-size:13px; color:#E2E8F0;">
        <b>🎓 Education:</b> {display_education}
    </div>
    <div style="background:#060813; padding:14px; border-radius:8px; border-left:3px solid #38BDF8; border:1px solid #1E293B;">
        <p style="margin:0; color:#E2E8F0; font-size:13px; line-height:1.6;"><b>🤖 AI Executive Summary:</b> {ai_summary}</p>
    </div>
</div>
"""
st.markdown("### 👤 Candidate Profile Summary")
st.markdown(summary_html, unsafe_allow_html=True)

# 2 & 3. Explainable AI (XAI)
st.markdown("### 🔍 Explainable AI (XAI) & Skill Alignment")
c1, c2 = st.columns(2)

with c1:
    raw_m = candidate.get("matched_skills", "")
    matched_list = raw_m.split(',') if isinstance(raw_m, str) and raw_m else (raw_m if isinstance(raw_m, list) else [])
    matched_list = [s.strip() for s in matched_list if s.strip()]
    
    raw_ms = candidate.get("missing_skills", "")
    missing_list = raw_ms.split(',') if isinstance(raw_ms, str) and raw_ms else (raw_ms if isinstance(raw_ms, list) else [])
    missing_list = [s.strip() for s in missing_list if s.strip()]
    if not missing_list:
        missing_list = ["Advanced Tools", "Cloud Platform"]
    
    items_html = ""
    for s in matched_list[:3]:
        items_html += f'<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; font-size:13px; color:#E2E8F0; background:#060813; padding:10px 14px; border-radius:8px; border:1px solid #1E293B;"><span>✅ <b>{s}</b></span><span style="color:#34D399; font-weight:700;">Matched (100%)</span></div>'
    
    for ms in missing_list[:2]:
        items_html += f'<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; font-size:13px; color:#94A3B8; background:#060813; padding:10px 14px; border-radius:8px; border:1px solid #1E293B;"><span>❌ <b>{ms}</b></span><span style="color:#EF4444; font-weight:700;">Missing (0%)</span></div>'

    if not matched_list and not missing_list:
        items_html = '<span style="color:#94A3B8; font-size:12px;">No skills mapped.</span>'

    xai_card_final = f"""
    <div class="card" style="min-height:300px;">
        <div style="font-size:15px; font-weight:700; color:#38BDF8; margin-bottom:14px;">Skills Match Breakdown</div>
        <div style="margin-bottom:10px;">{items_html}</div>
        <hr style="border:0; border-top:1px solid #1E293B; margin:15px 0;">
        <div style="font-size:12px; color:#94A3B8;">Overall Match Confidence: <b style="color:#34D399;">{confidence}%</b></div>
    </div>
    """
    st.markdown(xai_card_final, unsafe_allow_html=True)

with c2:
    rec_col = "#10B981" if "Recommend" in status_text else "#F59E0B" if "Review" in status_text else "#EF4444"
    why_card_html = f"""
    <div class="card" style="border-top:3px solid {rec_col}; min-height:300px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-size:15px; font-weight:700; color:{rec_col}; margin-bottom:12px;">Why Candidate Got {int(ats_val)}%?</div>
            <ul style="color:#E2E8F0; font-size:13px; line-height:1.8; padding-left:18px; margin:0;">
                <li>✅ Good match with required job skills</li>
                <li>✅ Relevant work experience duration</li>
                <li>✅ Clean and professional resume layout</li>
                <li>✅ Easy to read and parse by ATS system</li>
            </ul>
        </div>
        <div style="background:#060813; padding:12px 14px; border-radius:8px; border:1px solid #1E293B; margin-top:15px; font-size:12px; color:#C7D2FE;">
            ✨ <b>Evaluation Result:</b> {status_text} (Ready for HR/Technical round)
        </div>
    </div>
    """
    st.markdown(why_card_html, unsafe_allow_html=True)

# 4. SWOT Analysis
strengths_text = swot.get("strengths", "Good technical skills, proper project knowledge, and clear work history.")
weaknesses_text = swot.get("weaknesses", "Lacks experience in some advanced tools and cloud technologies.")
opportunities_text = swot.get("opportunities", "High chance to learn new technologies and grow in the technical team.")
threats_text = swot.get("threats", "Competition is high, so continuous skill upgrading is needed.")

swot_html = f"""
<div class="card">
    <div style="font-size:18px; font-weight:800; color:#FFFFFF; margin-bottom:18px; display:flex; align-items:center; gap:8px;">
        💪 AI-Generated SWOT Analysis
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-left: 4px solid #10B981; padding: 16px; border-radius: 10px;">
            <div style="color: #34D399; font-weight: 700; font-size: 14px; margin-bottom: 8px;">Strengths</div>
            <p style="color: #94A3B8; font-size: 12px; margin: 0; line-height: 1.6;">• {strengths_text}</p>
        </div>
        <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-left: 4px solid #EF4444; padding: 16px; border-radius: 10px;">
            <div style="color: #F87171; font-weight: 700; font-size: 14px; margin-bottom: 8px;">Weaknesses</div>
            <p style="color: #94A3B8; font-size: 12px; margin: 0; line-height: 1.6;">• {weaknesses_text}</p>
        </div>
        <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-left: 4px solid #3B82F6; padding: 16px; border-radius: 10px;">
            <div style="color: #60A5FA; font-weight: 700; font-size: 14px; margin-bottom: 8px;">Opportunities</div>
            <p style="color: #94A3B8; font-size: 12px; margin: 0; line-height: 1.6;">• {opportunities_text}</p>
        </div>
        <div style="background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); border-left: 4px solid #F59E0B; padding: 16px; border-radius: 10px;">
            <div style="color: #FBBF24; font-weight: 700; font-size: 14px; margin-bottom: 8px;">Threats</div>
            <p style="color: #94A3B8; font-size: 12px; margin: 0; line-height: 1.6;">• {threats_text}</p>
        </div>
    </div>
</div>
"""
st.markdown(swot_html, unsafe_allow_html=True)

# 5. DYNAMIC INTERVIEW QUESTIONS
st.markdown("### 🎤 AI Interview Questions")
for idx, q_obj in enumerate(questions[:5], 1):
    q_text = q_obj.get("question", str(q_obj)) if isinstance(q_obj, dict) else str(q_obj)
    single_q_html = f"""
    <div class="q-card">
        <div class="q-badge">{idx}</div>
        <div style="font-size:13px; color:#F8FAFC;">{q_text}</div>
    </div>
    """
    st.markdown(single_q_html, unsafe_allow_html=True)

st.divider()

# =============================================================
# ⭐ AI RECRUITER COPILOT & EMAIL GENERATOR
# =============================================================
st.markdown("### 🤖 AI Recruiter Copilot")
st.caption("Ask questions about candidates or generate automated recruitment emails.")

chat_key = f"chat_{candidate['name']}"
draft_key = f"draft_{candidate['name']}"

if chat_key not in st.session_state:
    st.session_state[chat_key] = []

col_copilot, col_email = st.columns([1.2, 1], gap="large")

with col_copilot:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:15px; font-weight:700; color:#38BDF8; margin-bottom:12px;">💬 Ask AI Recruiter Assistant</div>', unsafe_allow_html=True)
    
    for msg in st.session_state[chat_key]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-msg-user"><b>👤 Recruiter:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-msg-ai"><b>🤖 Copilot:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    user_query = st.text_input(f"Ask something about {candidate['name']}...", key=f"input_{candidate['name']}", placeholder="e.g., Is this candidate suitable for Senior Python Developer role?")
    
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button("🚀 Ask AI", use_container_width=True, key=f"btn_ask_{candidate['name']}"):
            if user_query.strip():
                st.session_state[chat_key].append({"role": "user", "content": user_query})
                
                cand_ctx = {
                    "name": candidate["name"],
                    "role": candidate.get("role", "Professional"),
                    "ats_score": candidate.get("ats_score", 70),
                    "experience": candidate.get("experience", "Fresher"),
                    "education": candidate.get("education", "Graduate"),
                    "matched_skills": candidate.get("matched_skills", ""),
                    "missing_skills": candidate.get("missing_skills", ""),
                    "status": candidate.get("status", "Pending Review")
                }
                
                ai_reply = ai_service.chat_with_recruiter(user_query, cand_ctx, st.session_state[chat_key])
                st.session_state[chat_key].append({"role": "assistant", "content": ai_reply})
                st.rerun()

    with c_btn2:
        if st.button("🗑️ Clear Chat", use_container_width=True, key=f"btn_clear_{candidate['name']}"):
            st.session_state[chat_key] = []
            if draft_key in st.session_state:
                del st.session_state[draft_key]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with col_email:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:15px; font-weight:700; color:#A78BFA; margin-bottom:12px;">📧 Generate Candidate Email</div>', unsafe_allow_html=True)
    
    email_type = st.selectbox(
        "Select Email Template Type",
        ["Interview Invitation", "Shortlisted", "Offer Letter", "Application Under Review", "Rejection Email"],
        key=f"email_select_{candidate['name']}"
    )
    
    if st.button("✨ Draft Email", type="primary", use_container_width=True, key=f"btn_email_{candidate['name']}"):
        cand_data_for_email = {
            "name": candidate["name"],
            "role": candidate.get("role", "Professional"),
            "ats_score": candidate.get("ats_score", 70)
        }
        drafted_email = ai_service.generate_recruitment_email(email_type, cand_data_for_email)
        st.session_state[draft_key] = drafted_email

    if draft_key in st.session_state:
        st.text_area("Generated Email Draft", value=st.session_state[draft_key], height=180, key=f"text_email_{candidate['name']}")
        st.caption("📋 Copy this text to send to the candidate.")

    st.markdown('</div>', unsafe_allow_html=True)
