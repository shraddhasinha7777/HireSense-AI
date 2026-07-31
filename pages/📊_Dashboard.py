import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import Database

db = Database()

st.set_page_config(page_title="Analytics Dashboard | HireSense-AI", page_icon="📊", layout="wide")

# PREMIUM DARK THEME WITH PROFESSIONAL PLOTLY STYLING
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #090514 0%, #0F0B26 100%) !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background-color: #030108 !important; border-right: 1px solid #1E293B !important; }
.block-container { padding-top: 2rem; max-width: 1350px !important; }

.kpi-card { background: #0D1127; border: 1px solid #1E293B; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.kpi-val { font-size: 32px; font-weight: 900; color: #FFFFFF; margin-bottom: 5px; }
.kpi-label { font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;}

.chart-card { background: #0D1127; border: 1px solid #1E293B; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.chart-title { color: #38BDF8; font-size: 16px; font-weight: 800; margin-bottom: 15px; border-bottom: 1px solid #1E293B; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: white;'>📊 Recruitment Analytics Dashboard</h2>", unsafe_allow_html=True)
st.caption("High-level overview of candidate processing, ATS pipeline, and visual analytics")

records = db.get_all_candidates()

if not records:
    st.info("No candidate data available. Please process resumes in the Resume Analyzer.")
else:
    df = pd.DataFrame(records)
    
    # -------------------------------------------------------------
    # 1. KPI CARDS
    # -------------------------------------------------------------
    total_cands = len(df)
    avg_ats = round(df['ats_score'].mean(), 1)
    highly_rec = len(df[df['status'] == 'Highly Recommended'])
    rejected = len(df[df['status'] == 'Rejected'])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#38BDF8;">{total_cands}</div><div class="kpi-label">Total Processed</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#A78BFA;">{avg_ats}%</div><div class="kpi-label">Average ATS Score</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#10B981;">{highly_rec}</div><div class="kpi-label">Highly Recommended</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#F87171;">{rejected}</div><div class="kpi-label">Rejected Candidates</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # -------------------------------------------------------------
    # 2. ATS COMPARISON (Bar) & RECOMMENDATION DISTRIBUTION (Donut)
    # -------------------------------------------------------------
    ch1, ch2 = st.columns(2)
    
    with ch1:
        st.markdown('<div class="chart-card"><div class="chart-title">📊 ATS Score Comparison</div>', unsafe_allow_html=True)
        if not df.empty and 'name' in df.columns and 'ats_score' in df.columns:
            df_sorted = df.sort_values("ats_score", ascending=False)
            
            fig_bar = px.bar(
                df_sorted, 
                x='name', 
                y='ats_score', 
                color='ats_score',
                color_continuous_scale=['#3B82F6', '#38BDF8', '#10B981'],
                labels={'name': 'Candidate Name', 'ats_score': 'ATS Score (%)'}
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#E2E8F0',
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                coloraxis_showscale=False 
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        st.markdown('<div class="chart-card"><div class="chart-title">🥧 Recommendation Distribution</div>', unsafe_allow_html=True)
        if not df.empty and 'status' in df.columns:
            status_counts_df = df['status'].value_counts().reset_index()
            status_counts_df.columns = ['Status', 'Count']
            
            color_map = {
                "Highly Recommended": "#10B981",
                "Recommended": "#3B82F6",
                "Pending Review": "#F59E0B",
                "Rejected": "#EF4444"
            }
            
            fig_pie = px.pie(
                status_counts_df, 
                names='Status', 
                values='Count',
                hole=0.4,
                color='Status',
                color_discrete_map=color_map
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#E2E8F0',
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=10, b=30, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. RECRUITMENT PIPELINE & RECRUITMENT INSIGHTS
    # -------------------------------------------------------------
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">📈 Recruitment Pipeline</div>', unsafe_allow_html=True)
        status_counts = df['status'].value_counts()
        
        for stat, count in status_counts.items():
            pct = (count / total_cands) * 100
            if stat == "Highly Recommended": color = "#10B981"
            elif stat == "Recommended": color = "#3B82F6"
            elif stat == "Pending Review": color = "#F59E0B"
            else: color = "#EF4444"
            
            st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:#E2E8F0; margin-bottom:4px;">
                        <span>{stat}</span><span>{count} Candidates ({int(pct)}%)</span>
                    </div>
                    <div style="height: 8px; background: #1E293B; border-radius: 4px; overflow: hidden;">
                        <div style="width: {pct}%; height: 100%; background: {color};"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">💡 Recruitment Insights</div>', unsafe_allow_html=True)
        
        if not df.empty:
            best_cand_row = df.loc[df['ats_score'].idxmax()]
            highest_score = best_cand_row['ats_score']
            best_cand_name = best_cand_row['name']
            lowest_score = df['ats_score'].min()
            
            st.markdown(f"""
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 2px;">🏆 Highest ATS Score</div>
                    <div style="font-size: 24px; font-weight: 900; color: #10B981; line-height: 1.1;">{highest_score}%</div>
                    <div style="font-size: 12px; color: #E2E8F0; margin-top: 4px;">👤 Best Candidate: <b>{best_cand_name}</b></div>
                </div>
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 2px;">📉 Lowest ATS Score</div>
                    <div style="font-size: 24px; font-weight: 900; color: #EF4444; line-height: 1.1;">{lowest_score}%</div>
                </div>
                <div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 2px;">📊 Average ATS</div>
                    <div style="font-size: 24px; font-weight: 900; color: #38BDF8; line-height: 1.1;">{avg_ats}%</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("Not enough data for insights.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 4. RECENT CANDIDATES
    # -------------------------------------------------------------
    st.markdown('<div class="chart-card"><div class="chart-title">🕒 Recent Candidates</div>', unsafe_allow_html=True)
    recent_df = df.sort_values("created_at", ascending=False).head(5)
    recent_df = recent_df[['name', 'role', 'ats_score', 'status', 'created_at']].rename(columns={
        "name": "Candidate", "role": "Target Role", "ats_score": "ATS", "status": "Status", "created_at": "Date"
    })
    recent_df["ATS"] = recent_df["ATS"].round(1)
    
    # Format the Date nicely (e.g., 30 Jul 2026)
    recent_df["Date"] = pd.to_datetime(recent_df["Date"]).dt.strftime('%d %b %Y')
    
    st.dataframe(recent_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
