import streamlit as st
from datetime import datetime

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE CSS STYLING
# =====================================================================
st.set_page_config(
    page_title="Home | HireSense-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium SaaS CSS with Advanced Hero Box & Ultra-Premium Dropzone
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    
    /* ⭐ ADVANCED CSS: Richer Hero Box Framing */
    .hero-box {
        background: linear-gradient(135deg, #FFFFFF 0%, #EEF2FF 100%);
        padding: 35px 20px;
        border-radius: 16px;
        border: 1px solid #C7D2FE;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.08);
    }
    .welcome-title { font-size: 38px; font-weight: 800; color: #1E1B4B; margin-bottom: 8px; }
    .welcome-subtitle { font-size: 17px; color: #334155; margin-bottom: 12px; font-weight: 600; }
    .welcome-tagline { font-size: 13px; font-weight: 700; color: #4F46E5; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Intake Split Cards */
    .intake-box {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        height: 100%;
    }
    .intake-header { font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    
    /* ⭐ ADVANCED CSS: Ultra-Premium Drag & Drop Uploader Styling */
    [data-testid="stFileUploadDropzone"] {
        background-color: #F8FAFC !important;
        border: 2px dashed #4F46E5 !important;
        border-radius: 14px !important;
        padding: 28px !important;
        transition: all 0.3s ease-in-out !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: #EEF2FF !important;
        border-color: #312E81 !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.15) !important;
        transform: scale(1.01);
    }
    
    /* Feature Grid Cards (5 Column) */
    .feature-card {
        background: #FFFFFF;
        padding: 18px 14px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        text-align: center;
        transition: all 0.2s ease;
        min-height: 140px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .feature-card:hover { transform: translateY(-3px); border-color: #6366F1; box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1); }
    .feature-icon { font-size: 24px; margin-bottom: 8px; }
    .feature-title { font-size: 13px; font-weight: 700; color: #1E293B; margin-bottom: 6px; }
    .feature-desc { font-size: 11px; color: #64748B; line-height: 1.4; }
    
    /* Workflow Steps (Horizontal Flow) */
    .workflow-title { font-size: 18px; font-weight: 700; color: #4F46E5; margin-top: 30px; margin-bottom: 15px; }
    .step-card {
        background: #FFFFFF;
        padding: 14px;
        border-radius: 10px;
        border: 1px dashed #CBD5E1;
        text-align: center;
        position: relative;
    }
    .step-num { font-size: 10px; font-weight: 800; color: #6366F1; text-transform: uppercase; letter-spacing: 1px; }
    .step-name { font-size: 13px; font-weight: 700; color: #1E293B; margin: 4px 0; }
    .step-desc { font-size: 11px; color: #64748B; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. SIMPLIFIED & CLEAN SIDEBAR (100% Onboarding Focused - No Clutter!)
# =====================================================================
with st.sidebar:
    st.markdown("### 🤖 HireSense-AI")
    st.caption("AI Powered Recruitment Analytics Platform")
    st.divider()
    
    st.info("💡 **Quick Tip:** Start by pasting your target Job Description and uploading candidate resumes on this page.")
    
    st.divider()
    st.caption("© 2026 HireSense-AI | AI Powered Recruitment Analytics Platform")

# =====================================================================
# 3. WELCOME HERO BANNER (RICHER & ENHANCED AS REQUESTED 🔒)
# =====================================================================
st.markdown("""
    <div class="hero-box">
        <p class="welcome-title">Welcome to <span style="color:#4F46E5;">HireSense-AI</span></p>
        <p class="welcome-subtitle">AI Powered Resume Screening & Recruitment Analytics Platform</p>
        <p class="welcome-tagline">Smart • Fast • Explainable • Bias Aware</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 4. MIDDLE SECTION: INTAKE WORKSPACE (JD Paste & Resume Upload)
# =====================================================================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
        <div class="intake-header">
            <span>📋</span> 1. Paste Job Description
        </div>
    """, unsafe_allow_html=True)
    
    job_desc = st.text_area(
        label="Job Description Input",
        placeholder="Enter job title, required skills, experience, qualifications, responsibilities, etc...",
        height=180,
        label_visibility="collapsed"
    )
    st.caption("💡 **Tip:** More details in JD gives better AI matching results.")

with col2:
    st.markdown("""
        <div class="intake-header">
            <span>📤</span> 2. Upload Resumes (PDF)
        </div>
    """, unsafe_allow_html=True)
    
    # Ultra-Premium CSS styling automatically applied here!
    uploaded_files = st.file_uploader(
        label="Resume Uploader",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Drag & drop PDF files here or browse from your computer."
    )
    st.caption("⚡ You can upload multiple candidate resumes simultaneously for batch processing.")

# Action Trigger (Short Button Label & Professional Notice)
st.write("")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
with col_btn2:
    if st.button("🚀 Start Resume Analysis", use_container_width=True, type="primary"):
        if not job_desc or not uploaded_files:
            st.warning("⚠️ Please provide both a Job Description and at least one Resume PDF to begin.")
        else:
            st.success("✅ Resume processing initiated successfully.")
            st.info("📌 Navigate to **Resume Analyzer** from the sidebar to view extracted candidate information.")

st.divider()

# =====================================================================
# 5. FEATURE SHOWCASE GRID (RENAMED TO CORPORATE STANDARD 🔒)
# =====================================================================
st.markdown("### ✨ Core Platform Features")
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

with f_col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">AI Resume Parsing</div>
            <div class="feature-desc">Extracts key info, skills, experience & education automatically.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Matching</div>
            <div class="feature-desc">Matches candidates with JD using advanced AI algorithms.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">ATS Scoring</div>
            <div class="feature-desc">Generates accurate ATS score with explainable breakdown.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-title">Rank & Compare</div>
            <div class="feature-desc">Ranks candidates and allows side-by-side comparison.</div>
        </div>
    """, unsafe_allow_html=True)

with f_col5:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI Insights</div>
            <div class="feature-desc">Get AI summaries, SWOT, interview questions & more.</div>
        </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# =====================================================================
# 6. WORKFLOW DIAGRAM: HOW HIRESENSE-AI WORKS (5 Horizontal Steps)
# =====================================================================
st.markdown('<p class="workflow-title">⚙️ How HireSense-AI Works</p>', unsafe_allow_html=True)
w_col1, w_col2, w_col3, w_col4, w_col5 = st.columns(5)

with w_col1:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 01</div>
            <div class="step-name">📤 Upload Resumes</div>
            <div class="step-desc">Upload single or multiple PDF resumes.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col2:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 02</div>
            <div class="step-name">📄 Parse & Extract</div>
            <div class="step-desc">AI parses resumes and extracts key data.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col3:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 04</div>
            <div class="step-name">🎯 Match & Score</div>
            <div class="step-desc">Candidates matched with JD and scored.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col4:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 04</div>
            <div class="step-name">📊 Rank & Analyze</div>
            <div class="step-desc">View ranked candidates and analytics.</div>
        </div>
    """, unsafe_allow_html=True)

with w_col5:
    st.markdown("""
        <div class="step-card">
            <div class="step-num">Step 05</div>
            <div class="step-name">✨ AI Insights</div>
            <div class="step-desc">Get AI SWOT, interview Qs & reports.</div>
        </div>
    """, unsafe_allow_html=True)

# Footer Prompt
st.write("")
st.markdown("<p style='text-align:center; color:#64748B; font-size:13px; font-weight:600;'>💜 Ready to analyze candidates? Paste your Job Description and upload PDF resumes above to begin!</p>", unsafe_allow_html=True)