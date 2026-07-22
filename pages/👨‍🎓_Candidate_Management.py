import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import Database

db = Database()

st.set_page_config(page_title="Candidate Management", page_icon="👥", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #090514 0%, #0F0B26 100%) !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background-color: #030108 !important; border-right: 1px solid #1E293B !important; }
.block-container { padding-top: 1.5rem; max-width: 1350px !important; }

.kpi-card { background: #0D1127; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.25); text-align: center;}
.kpi-val { font-size: 26px; font-weight: 900; color: #FFFFFF; margin: 4px 0; }
.kpi-label { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }

.stTextInput input, .stSelectbox select { background-color: #060813 !important; color: #FFFFFF !important; border: 1px solid #1E293B !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: white;'>👥 Candidate Management & Interview Shortlisting</h2>", unsafe_allow_html=True)
st.caption("Manage, Compare, Select and Shortlist Evaluated Candidates for Interviews")

records = db.get_all_candidates()

if records:
    df_raw = pd.DataFrame(records)
    total = len(df_raw)
    
    # ⭐ EXACT ATS ENGINE SYNC - OPTION A (RECOMMENDED COMBINATION)
    target_positive_statuses = ["Recommended", "Highly Recommended", "Shortlisted", "Excellent"]
    recommended_count = len(df_raw[df_raw["status"].isin(target_positive_statuses)])
    
    pending = len(df_raw[df_raw["status"] == "Pending Review"])
    rejected = len(df_raw[df_raw["status"] == "Rejected"])
    avg = df_raw["ats_score"].mean() if "ats_score" in df_raw.columns else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">👥 Total Candidates</div><div class="kpi-val" style="color:#38BDF8;">{total}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">🎯 Recommended Candidates</div><div class="kpi-val" style="color:#10B981;">{recommended_count}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-label">⭐ Avg ATS Score</div><div class="kpi-val" style="color:#A78BFA;">{round(avg, 1)}%</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-label">System Status</div><div class="kpi-val" style="color:#10B981; font-size:20px; margin-top:6px;">● Operational</div></div>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1: search = st.text_input("🔍 Search by Candidate Name or Role...", placeholder="Type keyword...")
    with col2: status_filter = st.selectbox("📋 Filter Status", ["All", "Shortlisted", "Recommended", "Under Review", "Rejected"])
    with col3: sort = st.selectbox("⬇ Sort by", ["ATS Score", "JD Match", "Experience"])

    blind_hiring = st.toggle("🕶️ Enable Blind Hiring (Hide Candidate Identity)")
    st.write("")

    df = df_raw.copy()
    if blind_hiring:
        df["name"] = [f"Candidate #{i:03d}" for i in range(1, len(df)+1)]
        if "email" in df.columns: df = df.drop(columns=["email"])

    # Filtering & Sorting before rendering selection table
    if "experience" in df.columns:
        df["Exp_Num"] = df["experience"].astype(str).str.extract(r'(\d+\.?\d*)')[0].astype(float).fillna(0.0)
    else: df["Exp_Num"] = 0.0
    
    if search: 
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    if status_filter != "All" and "status" in df.columns: 
        df = df[df["status"] == status_filter]
        
    if sort == "ATS Score" and "ats_score" in df.columns: df = df.sort_values("ats_score", ascending=False)
    elif sort == "JD Match" and "jd_match" in df.columns: df = df.sort_values("jd_match", ascending=False)
    elif sort == "Experience": df = df.sort_values("Exp_Num", ascending=False)

    st.markdown("### 📋 Candidate Leaderboard & Selection Workspace")
    st.caption("☑️ Check the box against any candidate to add them to the Interview Shortlist table below.")

    # ⭐ INTERACTIVE SELECTION FORM TABLE
    selected_candidates_list = []
    
    if not df.empty:
        # Header row for interactive selection table
        header_cols = st.columns([0.6, 2.2, 2.2, 1.2, 1.2, 1.5])
        header_cols[0].markdown("<b>Select</b>", unsafe_allow_html=True)
        header_cols[1].markdown("<b>Candidate 👤</b>", unsafe_allow_html=True)
        header_cols[2].markdown("<b>Applied Role</b>", unsafe_allow_html=True)
        header_cols[3].markdown("<b>ATS Score</b>", unsafe_allow_html=True)
        header_cols[4].markdown("<b>JD Match</b>", unsafe_allow_html=True)
        header_cols[5].markdown("<b>Status</b>", unsafe_allow_html=True)
        st.divider()

        for idx, row in df.iterrows():
            r_cols = st.columns([0.6, 2.2, 2.2, 1.2, 1.2, 1.5])
            
            # Unique checkbox for each candidate record
            is_checked = r_cols[0].checkbox("", key=f"select_{row.get('id', idx)}")
            
            r_cols[1].write(row.get("name", "Unknown"))
            r_cols[2].write(row.get("role", "N/A"))
            r_cols[3].write(f"{int(row.get('ats_score', 0))}%")
            r_cols[4].write(f"{int(row.get('jd_match', 0))}%")
            r_cols[5].write(row.get("status", "Evaluated"))

            if is_checked:
                selected_candidates_list.append({
                    "Candidate": row.get("name", "Unknown"),
                    "Role": row.get("role", "N/A"),
                    "ATS Score": f"{int(row.get('ats_score', 0))}%",
                    "Interview Status": "Selected"
                })

    # ⭐ DYNAMIC INTERVIEW SHORTLIST TABLE DISPLAY
    st.write("")
    st.markdown("---")
    st.markdown("### 📋 Interview Shortlist Workspace")
    
    if selected_candidates_list:
        st.success(f"🎯 Total {len(selected_candidates_list)} candidate(s) shortlisted for upcoming interview rounds.")
        shortlist_df = pd.DataFrame(selected_candidates_list)
        st.dataframe(shortlist_df, use_container_width=True, hide_index=True)
        
        # Action button for shortlisted candidates
        if st.button("📤 Export Shortlist to CSV", type="primary"):
            csv_shortlist = shortlist_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Shortlist Data",
                data=csv_shortlist,
                file_name="Interview_Shortlist_Candidates.csv",
                mime="text/csv"
            )
    else:
        st.info("ℹ️ No candidates selected yet. Check the selection boxes in the leaderboard above to build your Interview Shortlist.")

else:
    st.info("No candidates found in database. Please analyze and save a resume from the Home/Analyzer page first.")