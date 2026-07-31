from database import Database
from ai_service import AIService
import json
import os
import sys
import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

db = Database()
ai_service = AIService()

st.set_page_config(
    page_title="AI Insights | HireSense-AI", page_icon="🧠", layout="wide"
)

# PREMIUM DARK THEME STYLING
st.markdown(
    """
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
div.stButton > button[kind="secondary"] {
    background: #1E293B !important;
    color: #38BDF8 !important;
    border: 1px solid #334155 !important;
    font-size: 12px !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
}
div.stButton > button[kind="secondary"]:hover {
    background: #334155 !important;
    border-color: #38BDF8 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

records = db.get_all_candidates()
if not records:
  st.warning(
      "⚠️ No candidate found in database. Please process a resume first."
  )
  st.stop()

df = pd.DataFrame(records)
df["created_at"] = pd.to_datetime(df["created_at"])

# Dropdown to select primary candidate
cand_names = df["name"].tolist()
selected_cand = st.selectbox(
    "Select Candidate for Deep AI Insight", reversed(cand_names)
)
candidate = df[df["name"] == selected_cand].iloc[0]

ats_val = float(candidate.get("ats_score", 70.0))
jd_val = float(candidate.get("jd_match", 70.0))

st.markdown("## 🧠 AI Insights & Decision Support")
st.divider()

ai_summary = (
    candidate.get("ai_summary") or "AI Summary not available in database."
)

# Handle Education Fallback
raw_edu = str(candidate.get("education", "Not Found"))
if not raw_edu or raw_edu in ["Not Found", "None", "Unknown", "NaN"]:
  display_education = "Education details not mentioned in resume."
else:
  display_education = raw_edu

applied_role = candidate.get("role", "Professional")

# Determine Fit Rating Stars
fit_rating = (
    "⭐⭐⭐⭐⭐"
    if ats_val >= 80
    else "⭐⭐⭐⭐☆"
    if ats_val >= 65
    else "⭐⭐⭐☆☆"
)

# =============================================================
# ⭐ 1. CANDIDATE PROFILE SUMMARY (WHITE BACKGROUND)
# =============================================================
summary_html = f"""
<div class="card" style="background: #FFFFFF; border-top: 4px solid #8B5CF6; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:20px; margin-bottom:15px;">
        <div>
            <h3 style="margin:0; color:#0F172A;">👤 {candidate["name"]}</h3>
            <div style="margin-top:6px; display:flex; gap:15px; font-size:13px; flex-wrap:wrap;">
                <span style="color:#6366F1; font-weight:700;">Applied Role: <b style="color:#0F172A;">{applied_role}</b></span>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="color:#64748B; font-size:13px; margin-bottom:4px;"><b>💼 Experience:</b> <span style="color:#0F172A;">{candidate["experience"]}</span></div>
            <div style="color:#64748B; font-size:13px;"><b>⭐ Overall Fit:</b> <span style="color:#FBBF24;">{fit_rating}</span></div>
        </div>
    </div>
    <div style="margin-bottom:15px; font-size:13px; color:#334155;">
        <b>🎓 Education:</b> {display_education}
    </div>
    <div style="background:#F8FAFC; padding:14px; border-radius:8px; border-left:4px solid #38BDF8; border:1px solid #E2E8F0;">
        <p style="margin:0; color:#1E293B; font-size:13px; line-height:1.6; font-weight:500;"><b>🤖 AI Executive Summary:</b> {ai_summary}</p>
    </div>
</div>
"""
st.markdown("### 👤 Candidate Profile Summary")
st.markdown(summary_html, unsafe_allow_html=True)


# =============================================================
# ⭐ 2. AI RECRUITER ASSISTANT & EMAIL GENERATOR
# =============================================================
chat_key = f"chat_{candidate['name']}"
draft_key = f"draft_{candidate['name']}"

if chat_key not in st.session_state:
  st.session_state[chat_key] = []

col_assistant, col_email = st.columns([1.2, 1], gap="large")

# Helper function to process AI Assistant queries
def process_ai_query(query_text):
  st.session_state[chat_key].append({"role": "user", "content": query_text})
  
  cand_ctx = {
      "name": candidate["name"],
      "role": applied_role,
      "ats_score": ats_val,
      "jd_match": jd_val,
      "experience": candidate.get("experience", "Fresher"),
      "education": candidate.get("education", "Graduate"),
      "matched_skills": candidate.get("matched_skills", ""),
      "missing_skills": candidate.get("missing_skills", ""),
  }
  
  ai_reply = ai_service.chat_with_recruiter(
      query_text, cand_ctx, st.session_state[chat_key]
  )
  st.session_state[chat_key].append({"role": "assistant", "content": ai_reply})
  st.rerun()


with col_assistant:
  st.markdown('<div class="card">', unsafe_allow_html=True)
  st.markdown(
      '<div style="font-size:18px; font-weight:700; color:#38BDF8;'
      ' margin-bottom:15px;">🤖 AI Recruiter Assistant</div>',
      unsafe_allow_html=True,
  )

  # Chat History Display
  chat_container = st.container(height=350)
  with chat_container:
      if not st.session_state[chat_key]:
          st.info("Ask anything about this candidate, or use Quick AI Actions below to generate insights on demand.")
      
      for msg in st.session_state[chat_key]:
        if msg["role"] == "user":
          st.markdown(
              '<div class="chat-msg-user"><b>👤 Recruiter:</b>'
              f' {msg["content"]}</div>',
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              f'<div class="chat-msg-ai"><b>🤖 AI Assistant:</b> {msg["content"]}</div>',
              unsafe_allow_html=True,
          )

  st.write("")
  
  # ✨ QUICK AI ACTIONS
  st.markdown("<span style='font-size:13px; font-weight:700; color:#A78BFA;'>✨ Quick AI Actions</span>", unsafe_allow_html=True)
  
  q_col1, q_col2, q_col3 = st.columns(3)
  
  with q_col1:
      if st.button("📊 Explain ATS Score", use_container_width=True, type="secondary"):
          prompt = f"Explain why {candidate['name']} received an ATS score of {ats_val}%. Mention their matched and missing skills."
          process_ai_query(prompt)
          
  with q_col2:
      if st.button("🎤 Generate Interview Questions", use_container_width=True, type="secondary"):
          prompt = f"Generate 5 technical interview questions for {candidate['name']} based on their resume for the {applied_role} role."
          process_ai_query(prompt)
          
  with q_col3:
      if st.button("🌟 SWOT Analysis", use_container_width=True, type="secondary"):
          prompt = f"Provide a brief SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for {candidate['name']} for the {applied_role} position based on their resume data."
          process_ai_query(prompt)

  # 🆚 DYNAMIC EXPLICIT COMPARISON DROPDOWN
  st.markdown("<div style='margin-top: 15px; margin-bottom: 5px; font-size:13px; font-weight:700; color:#A78BFA;'>🆚 Compare Candidates</div>", unsafe_allow_html=True)
  other_candidates = [name for name in cand_names if name != candidate['name']]
  
  cmp_col1, cmp_col2 = st.columns([2, 1])
  with cmp_col1:
      compare_with = st.selectbox("Select candidate to compare:", other_candidates, label_visibility="collapsed")
  
  with cmp_col2:
      if st.button("Compare with AI", use_container_width=True, type="secondary", disabled=not other_candidates):
          if compare_with:
              # Fetch the 2nd candidate's actual data from the dataframe
              cand2 = df[df['name'] == compare_with].iloc[0]
              
              # Construct a highly detailed prompt injecting BOTH candidates' data explicitly
              prompt = f"Act as an expert Recruiter. Compare {candidate['name']} and {compare_with} for the {applied_role} role and tell me who is better suited and why.\n\n"
              prompt += f"Candidate 1 ({candidate['name']}):\n"
              prompt += f"- ATS Score: {ats_val}%\n"
              prompt += f"- Experience: {candidate.get('experience', 'N/A')}\n"
              prompt += f"- Matched Skills: {candidate.get('matched_skills', 'N/A')}\n"
              prompt += f"- Missing Skills: {candidate.get('missing_skills', 'N/A')}\n\n"
              
              prompt += f"Candidate 2 ({compare_with}):\n"
              prompt += f"- ATS Score: {float(cand2.get('ats_score', 0))}%\n"
              prompt += f"- Experience: {cand2.get('experience', 'N/A')}\n"
              prompt += f"- Matched Skills: {cand2.get('matched_skills', 'N/A')}\n"
              prompt += f"- Missing Skills: {cand2.get('missing_skills', 'N/A')}\n"
              
              process_ai_query(prompt)

  st.divider()

  # Manual Chat Input
  user_query = st.text_input(
      "Type your custom question...",
      key=f"input_{candidate['name']}",
      placeholder="e.g., Does this candidate have leadership experience?",
      label_visibility="collapsed"
  )

  c_btn1, c_btn2 = st.columns([1, 1])
  with c_btn1:
    if st.button(
        "🚀 Ask AI",
        use_container_width=True,
        type="primary",
        key=f"btn_ask_{candidate['name']}",
    ):
      if user_query.strip():
          process_ai_query(user_query)

  with c_btn2:
    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
        key=f"btn_clear_{candidate['name']}",
    ):
      st.session_state[chat_key] = []
      if draft_key in st.session_state:
        del st.session_state[draft_key]
      st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)

# Email Generator Column
with col_email:
  st.markdown('<div class="card">', unsafe_allow_html=True)
  st.markdown(
      '<div style="font-size:18px; font-weight:700; color:#A78BFA;'
      ' margin-bottom:15px;">📧 Generate Candidate Email</div>',
      unsafe_allow_html=True,
  )
  st.caption("Automatically draft personalized emails based on candidate profile.")

  email_type = st.selectbox(
      "Select Email Template Type",
      [
          "Interview Invitation",
          "Shortlisted",
          "Offer Letter",
          "Application Under Review",
          "Rejection Email",
      ],
      key=f"email_select_{candidate['name']}",
  )

  if st.button(
      "✨ Draft Email",
      type="primary",
      use_container_width=True,
      key=f"btn_email_{candidate['name']}",
  ):
    cand_data_for_email = {
        "name": candidate["name"],
        "role": applied_role,
        "ats_score": ats_val,
    }
    drafted_email = ai_service.generate_recruitment_email(
        email_type, cand_data_for_email
    )
    st.session_state[draft_key] = drafted_email

  if draft_key in st.session_state:
    st.text_area(
        "Generated Email Draft",
        value=st.session_state[draft_key],
        height=400,
        key=f"text_email_{candidate['name']}",
    )
    st.caption("📋 Copy this text to send to the candidate.")

  st.markdown("</div>", unsafe_allow_html=True)
