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
    .q-card { background: #F8FAFC; border-left: 4px solid #4F46E5; padding: 14px; margin-bottom: 12px; border-radius: 6px; font-weight: 600; color:#1E293B; }
    </style>
""", unsafe_allow_html=True)

records = db.get_all_candidates()
if not records:
    st.warning("⚠️ No candidate found. Please go to **Resume Analyzer** first.")
    st.stop()

df = pd.DataFrame(records)
df['created_at'] = pd.to_datetime(df['created_at'])
candidate = df.sort_values("created_at").iloc[-1]

ats_val = float(candidate.get("ats_score", 70.0))
jd_val = float(candidate.get("jd_match", 70.0))
confidence = round((ats_val * 0.65) + (jd_val * 0.35), 1)

try: swot = json.loads(candidate.get("swot", "{}"))
except: swot = {}

try: questions = json.loads(candidate.get("interview_questions", "[]"))
except: questions = []

st.markdown("## 🤖 AI Insights Dashboard")
st.divider()

k1, k2, k3 = st.columns(3)
k1.markdown(f'''<div class="kpi-card"><div class="kpi-val" style="color:#10B981;">{candidate["ats_score"]}%</div><div class="kpi-label">🎯 ATS Score</div></div>''', unsafe_allow_html=True)
k2.markdown(f'''<div class="kpi-card"><div class="kpi-val" style="color:#6366F1;">{confidence}%</div><div class="kpi-label">🤖 AI Confidence</div></div>''', unsafe_allow_html=True)
k3.markdown(f'''<div class="kpi-card"><div class="kpi-val" style="color:#059669;">{candidate["status"]}</div><div class="kpi-label">✅ Hiring Decision</div></div>''', unsafe_allow_html=True)

st.markdown("### 👤 Candidate Profile Summary")
st.markdown(f'''<div class="card" style="border-left:5px solid #4F46E5;">
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:15px;">
        <div><h3 style="margin:0; color:#1E1B4B;">👤 {candidate["name"]}</h3><span style="color:#4F46E5; font-weight:700;">Target Position: {candidate["role"]}</span></div>
        <div><b>💼 Experience:</b> {candidate["experience"]} | <b>🎓 Education:</b> {candidate["education"]}</div>
        <div><b>🤖 AI Confidence:</b> {confidence}% | <b>📄 Status:</b> DB Verified</div>
    </div></div>''', unsafe_allow_html=True)

st.markdown("### 💪 Executive SWOT Overview (DB Cached)")
s1, s2, s3, s4 = st.columns(4)
s1.markdown(f'<div class="card" style="border-top:3px solid #10B981; min-height:110px;"><b>🟢 Strengths</b><br><small>{swot.get("strengths", "N/A")}</small></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="card" style="border-top:3px solid #EF4444; min-height:110px;"><b>🔴 Weaknesses</b><br><small>{swot.get("weaknesses", "N/A")}</small></div>', unsafe_allow_html=True)
s3.markdown(f'<div class="card" style="border-top:3px solid #F59E0B; min-height:110px;"><b>🟡 Opportunities</b><br><small>{swot.get("opportunities", "N/A")}</small></div>', unsafe_allow_html=True)
s4.markdown(f'<div class="card" style="border-top:3px solid #64748B; min-height:110px;"><b>⚫ Threats</b><br><small>{swot.get("threats", "N/A")}</small></div>', unsafe_allow_html=True)

st.divider()
st.caption("© 2026 HireSense-AI | Dashboard Module")