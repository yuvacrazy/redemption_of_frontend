# frontend_app.py
"""
SmartPay — Streamlit Frontend (Purple Glassy UI, Tabs: Home / Predict / History)
Sends payload matching backend:
age, gender, education, marital_status, experience_level, employment_type,
job_title, hours_per_week, employee_residence, company_location, remote_ratio, company_size
"""

import os
import time
from datetime import datetime
from typing import Dict, Any

import streamlit as st
import requests
import plotly.graph_objects as go

# ----------------------------
# Config
# ----------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "https://redemption-of-ai.onrender.com/").rstrip("/")   # e.g. https://smartpay-ai-backend.onrender.com
API_KEY = os.getenv("API_KEY")
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None

HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["x-api-key"] = API_KEY

st.set_page_config(page_title="SmartPay — AI Salary Prediction", page_icon="💜", layout="wide")

# ----------------------------
# Styling - Purple Glassy
# ----------------------------
st.markdown(
    """
    <style>
    :root{
      --bg1: #0f0529;
      --bg2: #2b0b4a;
      --accent1: #7c3aed;
      --accent2: #a78bfa;
      --glass: rgba(255,255,255,0.06);
      --card-bg: rgba(255,255,255,0.04);
      --muted: #c7bfe9;
    }
    /* page background */
    .stApp {
      background: linear-gradient(180deg, #0a0420 0%, #190733 50%, #2b0b4a 100%);
      color: #efe8ff;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .title {
      font-size: 42px;
      font-weight: 800;
      margin-bottom: 2px;
      color: white;
    }
    .subtitle {
      color: var(--muted);
      margin-bottom: 18px;
      font-size: 14px;
    }
    .glass-card {
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
      border-radius: 14px;
      padding: 22px;
      border: 1px solid rgba(255,255,255,0.05);
      box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    }
    .glass-input {
      background: rgba(255,255,255,0.02);
      border-radius: 8px;
      padding: 10px;
      border: 1px solid rgba(255,255,255,0.03);
    }
    .purple-btn {
      display:inline-block;
      background: linear-gradient(90deg, var(--accent1), var(--accent2));
      border-radius: 12px;
      padding: 12px 18px;
      color: #fff !important;
      font-weight: 800;
      font-size: 16px;
      border: none;
      box-shadow: 0 8px 30px rgba(124,58,237,0.28);
      transition: transform .12s ease;
      width:100%;
    }
    .purple-btn:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(124,58,237,0.34); }
    .muted { color: var(--muted); }
    .card-title { font-weight:700; font-size:16px; color: #fff; }
    footer { color: #bfb3ff; text-align:center; margin-top:22px; }
    .small { color:var(--muted); font-size:13px; }
    .block-container { padding-top: 18px; padding-left: 32px; padding-right: 32px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header - Landing Title
# ----------------------------
st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'>", unsafe_allow_html=True)
st.markdown("""
<div>
  <div class="title">SmartPay — Ai Powered Salary Prediction System</div>
  <div class="subtitle">Predict. Analyze. Understand. Your Market Salary Powered By LightGBM & FastAPI</div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Session state
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # newest first
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

# ----------------------------
# Tabs: Home / Predict / History
# ----------------------------
tab_home, tab_predict, tab_history = st.tabs(["🏠 Home", "💰 Predict", "📜 History"])

# ----------------------------
# HOME Tab (Portfolio / Project Description)
# ----------------------------
with tab_home:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; gap:20px; align-items:center;'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='flex:1;'>
          <h3 class='card-title'>Project Overview</h3>
          <p class='small'>SmartPay Is A Modern Ai Powered Salary Prediction System Designed To Help Users And Recruiters Estimate Annual Salaries Based On Candidate Features. The Backend Uses A Trained LightGBM Model Exposed Via Fastapi, While The Frontend Provides An Interactive Dashboard Built With Streamlit.</p>
          <ul style='color:var(--muted)'>
            <li>Clean Secure Api With Api Key Authentication</li>
            <li>Feature Rich Model: Age, Education, Job Title, Experience, Hours And More</li>
            <li>Deployable On Render / Heroku / Any Cloud With Docker</li>
          </ul>
        </div>
        <div style='width:320px;'>
          <div style='background:linear-gradient(180deg,#41107a,#7c3aed); padding:16px; border-radius:10px;'>
            <div style='font-weight:800; font-size:18px; color:white;'>Project By Yuvaraja P</div>
            <div class='small' style='margin-top:6px;'>Final Year CSE (IoT) • Paavai Engineering College</div>
          </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# PREDICT Tab (Form + Predict Button + Output)
# ----------------------------
with tab_predict:
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Candidate Details</div>", unsafe_allow_html=True)
        with st.form("predict_form"):
            # two-column layout inside form
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1, key="age")
                education = st.selectbox("Education", ["High School", "Bachelor'S Degree", "Master'S Degree", "PhD", "Other"], index=1, key="education")
                gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer Not To Say"], index=0, key="gender")
                experience_level = st.selectbox("Experience Level", ["Junior", "Mid", "Senior"], index=0, key="experience_level")
            with c2:
                hours_per_week = st.slider("Hours Per Week", min_value=1, max_value=100, value=40, key="hours")
                job_title = st.text_input("Job Title", value="Software Engineer", key="job_title")
                marital_status = st.selectbox("Marital Status", ["Never Married", "Married", "Divorced", "Other"], index=0, key="marital_status")

            st.markdown("<hr/>", unsafe_allow_html=True)
            # residence / company
            c3, c4 = st.columns(2)
            with c3:
                employee_residence = st.text_input("Employee Residence (Country)", value="India", key="employee_residence")
            with c4:
                company_location = st.text_input("Company Location (Country)", value="India", key="company_location")

            # remaining fields
            remote_ratio = st.selectbox("Remote Ratio", [0, 25, 50, 75, 100], index=0, format_func=lambda x: f"{x}%", key="remote_ratio")
            company_size = st.selectbox("Company Size", ["S", "M", "L"], index=1, key="company_size")
            employment_type = st.selectbox("Employment Type", ["FT", "PT", "CT", "FL"], index=0, key="employment_type")

            # Predict button anchored at bottom
            predict_clicked = st.form_submit_button(
                label="<span style='font-weight:800'>Predict Salary</span>",
                help="Click To Predict Salary",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        # Output card (initially hidden until user clicks Predict)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Prediction Result</div>", unsafe_allow_html=True)
        result_placeholder = st.empty()
        st.markdown("<div class='small muted'>Prediction Will Appear After Clicking The Predict Button</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Only call API if Predict button pressed
    if predict_clicked:
        # Build payload using exact backend schema keys (lowercase underscores)
        payload = {
            "age": float(age),
            "gender": gender.title(),
            "education": education.title(),
            "marital_status": marital_status.title(),
            "experience_level": experience_level.lower(),   # keep model-friendly value like 'junior'
            "employment_type": employment_type,
            "job_title": job_title.title(),
            "hours_per_week": float(hours_per_week),
            "employee_residence": employee_residence.title(),
            "company_location": company_location.title(),
            "remote_ratio": float(remote_ratio),
            "company_size": company_size
        }

        # UX spinner & small delay for polished effect
        with st.spinner("Contacting SmartPay Engine..."):
            time.sleep(0.6)
            try:
                if not PREDICT_ENDPOINT:
                    raise RuntimeError("Backend URL Not Configured. Set BACKEND_URL Environment Variable.")

                resp = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=18)
                if resp.status_code != 200:
                    # show nice error box
                    try:
                        body = resp.json()
                    except Exception:
                        body = resp.text
                    st.error(f"Api Error {resp.status_code} — {body}")
                else:
                    data = resp.json()
                    predicted = float(data.get("predicted_salary_usd", data.get("predicted_salary", 0.0)))
                    # derive range if backend not providing
                    low = float(data.get("low", predicted * 0.85))
                    high = float(data.get("high", predicted * 1.15))

                    # store in session history
                    st.session_state.history.insert(0, {
                        "ts": datetime.utcnow().isoformat(),
                        "payload": payload,
                        "predicted": predicted,
                        "low": low,
                        "high": high
                    })
                    st.session_state.last_prediction = {
                        "predicted": predicted,
                        "low": low,
                        "high": high,
                        "payload": payload
                    }

                    # render output (Plotly Gauge with purple gradient)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=predicted,
                        number={"prefix": "$", "valueformat": ",.0f"},
                        title={"text": "Annual Salary (USD)", "font": {"size": 16, "color": "#efe8ff"}},
                        gauge={
                            "axis": {"range": [0, max(200000, high * 1.2)], "tickcolor": "#efe8ff"},
                            "bar": {"color": "#a78bfa"},
                            "bgcolor": "rgba(0,0,0,0)",
                            "steps": [
                                {"range": [0, predicted * 0.6], "color": "rgba(124,58,237,0.12)"},
                                {"range": [predicted * 0.6, predicted * 0.9], "color": "rgba(167,139,250,0.12)"},
                                {"range": [predicted * 0.9, predicted * 1.2], "color": "rgba(199,210,254,0.08)"}
                            ],
                        }
                    ))
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#efe8ff", height=300, margin=dict(t=8,b=8,l=8,r=8))
                    result_placeholder.plotly_chart(fig, use_container_width=True)

                    # textual display
                    st.markdown(f"<div style='text-align:center; margin-top:8px;'>"
                                f"<div style='font-size:28px; font-weight:800; color:#f5ecff'>${predicted:,.0f}</div>"
                                f"<div class='small' style='margin-top:6px;color:var(--muted)'>Estimated Range</div>"
                                f"<div style='font-weight:700; color:#e9d9ff'>${low:,.0f} - ${high:,.0f}</div>"
                                f"</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Prediction Failed: {e}")
                if BACKEND_URL:
                    st.info(f"Check Backend Health: {BACKEND_URL}/health")

# ----------------------------
# HISTORY Tab
# ----------------------------
with tab_history:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Recent Predictions</div>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("<div class='small'>No Predictions Yet. Generate a Prediction In The Predict Tab.</div>", unsafe_allow_html=True)
    else:
        for item in st.session_state.history[:12]:
            ts = datetime.fromisoformat(item["ts"]).strftime("%b %d %Y • %I:%M %p")
            with st.expander(f"${item['predicted']:,.0f} — {item['payload']['job_title']} — {ts}", expanded=False):
                st.markdown("**Inputs**")
                st.json(item["payload"])
                st.markdown("**Prediction**")
                st.write(f"**Predicted:** ${item['predicted']:,.0f}")
                st.write(f"**Range:** ${item['low']:,.0f} - ${item['high']:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Footer
# ----------------------------
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay — Developed By <b>Redemption</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
