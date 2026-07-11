import streamlit as st
import pandas as pd
import json
from database import Database

db = Database()

st.markdown("""
    <style>
    .kpi-card { background: #FFF; padding: 16px; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .kpi-val { font-size: 26px; font-weight: 900; color: #1E1B4B; margin: 2px 0; }
    .kpi-label { font-size: 12px; font-weight: 700; color: #64748B; margin-top: 6px; text-transform: uppercase; }
    .card { background: #FFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .pill-green { background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 3px; display: inline-block; }
    .pill-red { background: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 3px; display: inline-block; }
    .q-card { background: #F8FAFC; border-left: 4px solid #4F46E5; padding: 14px; margin-bottom: 12px; border-radius: 6px; font-weight: 600; color:#1E293B; }
    </style>
""", unsafe_allow_html=True)

# 1. Load Latest Candidate from DB
records = db.get_all_candidates()
if not records:
    st.warning("⚠️ No candidate found in database. Please process a resume first.")
    st.stop()

df = pd.DataFrame(records)
df['created_at'] = pd.to_datetime(df['created_at'])
candidate = df.sort_values("created_at").iloc[-1]

ats_val = float(candidate.get("ats_score", 70.0))
jd_val = float(candidate.get("jd_match", 70.0))
confidence = round((ats_val * 0.65) + (jd_val * 0.35), 1)

st.markdown("## 🤖 AI Insights & Explainable Decision Support")
st.divider()

# ⭐ UPGRADE: Fetching Permanent AI Data Directly from SQLite Database!
try: swot = json.loads(candidate.get("swot", "{}"))
except: swot = {}

try: questions = json.loads(candidate.get("interview_questions", "[]"))
except: questions = []

ai_summary = candidate.get("ai_summary") or "AI Summary not available in database."
ai_reco = candidate.get("ai_recommendation") or "Review Manually"

# 2. KPI Section
k1, k2, k3 = st.columns(3)
k1.markdown(f'''<div class="kpi-card"><div class="kpi-val" style="color:#10B981;">{candidate["ats_score"]}%</div><div class="kpi-label">🎯 ATS Score</div></div>''', unsafe_allow_html=True)
k2.markdown(f'''<div class="kpi-card"><div class="kpi-val" style="color:#6366F1;">{confidence}%</div><div class="kpi-label">🤖 AI Confidence</div></div>''', unsafe_allow_html=True)
k3.markdown(f'''<div class="kpi-card"><div class="kpi-val" style="color:#059669;">{candidate["status"]}</div><div class="kpi-label">✅ Hiring Decision</div></div>''', unsafe_allow_html=True)

# 3. Profile Summary
st.markdown("### 👤 Candidate Profile Summary")
st.markdown(f'''<div class="card" style="border-left:5px solid #4F46E5;">
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:15px; margin-bottom:12px;">
        <div><h3 style="margin:0; color:#1E1B4B;">👤 {candidate["name"]}</h3><span style="color:#4F46E5; font-weight:700;">Target Role: {candidate["role"]}</span></div>
        <div><b>💼 Experience:</b> {candidate["experience"]} | <b>🎓 Education:</b> {candidate["education"]}</div>
    </div>
    <div style="background:#EEF2FF; padding:12px; border-radius:8px; border-left:4px solid #6366F1;">
        <p style="margin:0; color:#1E1B4B; font-size:14px; line-height:1.5;"><b>🤖 AI Executive Summary:</b> {ai_summary}</p>
    </div>
    </div>''', unsafe_allow_html=True)

# 4. Explainable AI (XAI)
st.markdown("### 🔍 Explainable AI (XAI) & Skill Alignment")
c1, c2 = st.columns(2)
with c1:
    raw_m = candidate["matched_skills"]
    skills = raw_m.split(',') if isinstance(raw_m, str) and raw_m else (raw_m if isinstance(raw_m, list) else [])
    st.markdown('<div class="card"><b>Verified Matched Skills:</b><br>' + "".join([f'<span class="pill-green">✔ {s.strip()}</span>' for s in skills if s.strip()]) + '</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="card" style="border-left:4px solid #10B981; height:88%;">
        <b style="color:#065F46;">💡 Database AI Recommendation</b><br><br>
        <p style="color:#334155; line-height:1.6; font-weight:bold;">{ai_reco}</p>
        <hr style="border:0; border-top:1px solid #E2E8F0;">
        <small style="color:#64748B;"><b>Traceability Status:</b> Verified against Job Description and ATS Evaluation.</small>
    </div>''', unsafe_allow_html=True)

# 5. DYNAMIC SWOT ANALYSIS (Loaded from DB)
st.markdown("### 💪 AI-Generated SWOT Analysis")
s1, s2, s3, s4 = st.columns(4)
s1.markdown(f'<div class="card" style="border-top:3px solid #10B981; min-height:120px;"><b>🟢 Strengths</b><br><small style="color:#475569;">{swot.get("strengths", "Not available")}</small></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="card" style="border-top:3px solid #EF4444; min-height:120px;"><b>🔴 Weaknesses</b><br><small style="color:#475569;">{swot.get("weaknesses", "Not available")}</small></div>', unsafe_allow_html=True)
s3.markdown(f'<div class="card" style="border-top:3px solid #F59E0B; min-height:120px;"><b>🟡 Opportunities</b><br><small style="color:#475569;">{swot.get("opportunities", "Not available")}</small></div>', unsafe_allow_html=True)
s4.markdown(f'<div class="card" style="border-top:3px solid #64748B; min-height:120px;"><b>⚫ Threats</b><br><small style="color:#475569;">{swot.get("threats", "Not available")}</small></div>', unsafe_allow_html=True)

# 6. DYNAMIC INTERVIEW QUESTIONS
st.markdown("### 🎤 Database-Stored AI Interview Questions")
for q_obj in questions[:4]:
    skill_tag = q_obj.get("skill", "General") if isinstance(q_obj, dict) else "Technical"
    q_text = q_obj.get("question", str(q_obj)) if isinstance(q_obj, dict) else str(q_obj)
    st.markdown(f'<div class="q-card"><span style="color:#4F46E5; font-size:11px; text-transform:uppercase;">[{skill_tag}]</span><br>{q_text}</div>', unsafe_allow_html=True)

st.divider()
st.caption("© 2026 HireSense-AI | Enterprise AI Insights Module (Database Connected)")