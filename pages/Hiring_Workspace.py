import streamlit as st
import pandas as pd
from datetime import datetime
from database import Database

db = Database()

# 1. Page Setup
st.set_page_config(page_title="Hiring Workspace | HireSense-AI", layout="wide")

# 2. Premium CSS
st.markdown("""
    <style>
    .kpi-card { background: #FFF; padding: 16px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
    .kpi-val { font-size: 26px; font-weight: 900; color: #1E1B4B; margin: 4px 0; }
    .kpi-label { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    .summary-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; text-align: center; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("## 💼 Hiring Workspace")
st.caption("Manage, Compare and Shortlist Candidates")

# 4. Dynamic KPI Logic
records = db.get_all_candidates()

if records:
    df_raw = pd.DataFrame(records)
    total = len(df_raw)
    recommended = len(df_raw[df_raw["status"] == "Highly Recommended"])
    pending = len(df_raw[df_raw["status"] == "Review"]) # Assuming 'Review' status
    rejected = len(df_raw[df_raw["status"] == "Rejected"])
    avg = df_raw["ats_score"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">👥 Total Candidates</div><div class="kpi-val">{total}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">🎯 Highly Recommended</div><div class="kpi-val">{recommended}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-label">⭐ Avg ATS Score</div><div class="kpi-val">{round(avg, 1)}%</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-label">System Status</div><div class="kpi-val">Operational</div></div>', unsafe_allow_html=True)
    st.divider()

    # 5. Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1: search = st.text_input("🔍 Search by Candidate Name, Skill or Role...")
    with col2: status_filter = st.selectbox("📋 Filter by Status", ["All", "Highly Recommended", "Review", "Rejected"])
    with col3: sort = st.selectbox("⬇ Sort by", ["ATS Score", "JD Match", "Experience"])

    blind_hiring = st.toggle("🕶️ Enable Blind Hiring (Hide Candidate Identity)")
    st.write("")

    # 6. Leaderboard Logic
    df = df_raw.copy()
    if blind_hiring:
        df["name"] = [f"Candidate #{i:03d}" for i in range(1, len(df)+1)]
        if "email" in df.columns: df = df.drop(columns=["email"])

    df = df.rename(columns={"name": "Candidate", "role": "Applied Role", "experience": "Experience", "ats_score": "ATS Score", "jd_match": "JD Match", "status": "Status"})
    df = df[["Candidate", "Applied Role", "Experience", "ATS Score", "JD Match", "Status"]]
    df["Exp_Num"] = df["Experience"].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
    
    if search: df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    if status_filter != "All": df = df[df["Status"] == status_filter]
    if sort == "ATS Score": df = df.sort_values("ATS Score", ascending=False)
    elif sort == "JD Match": df = df.sort_values("JD Match", ascending=False)
    elif sort == "Experience": df = df.sort_values("Exp_Num", ascending=False)

    st.markdown("### 📋 Candidate Leaderboard")
    st.caption(f"Showing {len(df)} candidate(s)")
    st.dataframe(df.drop(columns=["Exp_Num"]), use_container_width=True, hide_index=True)

    # 7. Hiring Summary (Improved Stats)
    st.markdown("### 📊 Hiring Summary")
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(f'<div class="summary-card" style="border-left:4px solid #10B981; color:#065F46;">Highly Recommended<br><b>{recommended}</b></div>', unsafe_allow_html=True)
    s2.markdown(f'<div class="summary-card" style="border-left:4px solid #F59E0B; color:#92400E;">Pending Review<br><b>{pending}</b></div>', unsafe_allow_html=True)
    s3.markdown(f'<div class="summary-card" style="border-left:4px solid #EF4444; color:#991B1B;">Rejected<br><b>{rejected}</b></div>', unsafe_allow_html=True)
    s4.markdown(f'<div class="summary-card" style="border-left:4px solid #3B82F6; color:#1E40AF;">Active Candidates<br><b>{total}</b></div>', unsafe_allow_html=True)

else:
    st.warning("No candidates found. Please analyze and save a resume first.")

st.divider()
st.caption("© 2026 HireSense-AI | Hiring Workspace Module")