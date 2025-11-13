# frontend_app.py
"""
SmartPay — Beautiful Streamlit Frontend
- Tabs: Home | Prediction | Analysis | Model Insights
- Sends payload exactly matching backend schema:
  age, gender, education, marital_status, experience_level, employment_type,
  job_title, hours_per_week, employee_residence, company_location, remote_ratio, company_size
- Output displayed ONLY after user clicks Predict
"""

import os
import time
from datetime import datetime
from typing import Dict, Any

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

# -------------------------
# CONFIG
# -------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "https://redemption-of-ai.onrender.com/").rstrip("/")
API_KEY = os.getenv("API_KEY")
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None
HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["x-api-key"] = API_KEY

st.set_page_config(page_title="SmartPay — AI Salary Prediction", page_icon="💼", layout="wide")

# -------------------------
# THEME / STYLES (Attractive palette)
# -------------------------
st.markdown(
    """
    <style>
    :root{
      --bg1: #f6fbff;
      --accent1: #0066ff;
      --accent2: #00d4ff;
      --card-bg: rgba(255,255,255,0.95);
      --muted: #6b7a86;
      --glass: rgba(255,255,255,0.88);
    }
    .block-container { padding-top: 18px; padding-left:36px; padding-right:36px; }
    body { background: linear-gradient(180deg,#f6fbff 0%, #eef9ff 100%); color: #042231; font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial; }
    .hero-title { font-size:42px; font-weight:800; margin-bottom:6px; }
    .hero-sub { color:var(--muted); font-size:15px; margin-bottom:20px; }
    .glass { background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.94)); border-radius:14px; padding:22px; box-shadow: 0 10px 30px rgba(2,20,40,0.06); border:1px solid rgba(5,30,60,0.04); }
    .accent-btn { background: linear-gradient(90deg,var(--accent1), var(--accent2)); color: white; font-weight:700; border-radius:10px; padding:10px 16px; width:100%; border: none;}
    .accent-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 24px rgba(0,102,255,0.14); }
    .small-muted { color:var(--muted); font-size:13px; }
    .salary-val { color:var(--accent1); font-size:36px; font-weight:800; }
    .kpi { font-weight:700; font-size:20px; color:#073659; }
    footer { color: #6b7a86; text-align:center; padding-top:20px; padding-bottom:20px; }
    .tab-title { font-weight:700; font-size:18px; }
    .card-compact { padding:14px; border-radius:12px; background:var(--card-bg); border:1px solid rgba(5,30,60,0.03); }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Header / Hero
# -------------------------
st.markdown("<div><div class='hero-title'>SmartPay — AI Powered Salary Prediction System</div></div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Predict. Analyze. Explain. A Professional Portfolio-Grade Interface For Salary Intelligence.</div>", unsafe_allow_html=True)

# -------------------------
# Initialize session state
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # newest first
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_payload" not in st.session_state:
    st.session_state.last_payload = None

# -------------------------
# Tabs
# -------------------------
tab_home, tab_pred, tab_analysis, tab_insights = st.tabs(["🏠 Home", "💰 Prediction", "📊 Analysis", "🧠 Model Insights"])

# -------------------------
# HOME TAB - portfolio / project description
# -------------------------
with tab_home:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("## Project Overview", unsafe_allow_html=True)
    st.markdown(
        """
        **SmartPay** Is An AI-Powered Salary Prediction System Built With A Production-Grade Backend (FastAPI + LightGBM)
        And A Professional Frontend (Streamlit). The System Predicts Annual Salary Based On Candidate And Job Features,
        Provides Dataset-Level Analysis, And Offers Model Explainability Information For Trustworthy Decisions.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Key Features", unsafe_allow_html=True)
    st.markdown(
        """
        - Precise Salary Predictions Using A Trained Regression Pipeline.  
        - Clear, Corporate UI With Glassy Cards, KPI Panels, And Visual Gauges.  
        - Protected Backend With API Key Authentication.  
        - Analysis Tab For Dataset Insights And Model Metrics.  
        - Model Insights Tab For Feature Importance And Explainability.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### How To Use", unsafe_allow_html=True)
    st.markdown(
        """
        1. Open Prediction Tab.  
        2. Fill In Candidate Details.  
        3. Click **Predict** (Output Appears Below).  
        4. Check Analysis & Model Insights For Deeper Understanding.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr/>", unsafe_allow_html=True)

    # Quick portfolio style cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='card-compact'><div class='kpi'>Production Ready</div><div class='small-muted'>FastAPI · LightGBM · Joblib</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card-compact'><div class='kpi'>Interactive UI</div><div class='small-muted'>Streamlit · Plotly Gauges · Clean Design</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card-compact'><div class='kpi'>Secure</div><div class='small-muted'>API Key Protected · Config Driven</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PREDICTION TAB
# -------------------------
with tab_pred:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Predict Salary", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Fill the form and press Predict. Output will appear only after clicking Predict.</div>", unsafe_allow_html=True)
    st.write("")  # small gap

    with st.form("predict_form"):
        # two column form for inputs
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1, format="%d")
            education = st.selectbox("Education", ["High School", "Bachelor's", "Master's", "PhD", "Other"])
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer Not To Say"])
            marital_status = st.selectbox("Marital Status", ["Never Married", "Married", "Divorced", "Widowed", "Other"])
            hours_per_week = st.slider("Hours Per Week", min_value=1, max_value=100, value=40)
        with col2:
            job_title = st.text_input("Job Title", value="Data Engineer")
            experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior"], index=0)
            employment_type = st.selectbox("Employment Type", ["FT", "PT", "CT", "FL"], index=0)
            employee_residence = st.text_input("Employee Residence (Country)", value="India")
            company_location = st.text_input("Company Location (Country)", value="India")
            remote_ratio = st.selectbox("Remote Ratio (%)", [0, 25, 50, 75, 100], index=0)
            company_size = st.selectbox("Company Size", ["S", "M", "L"], index=1)

        # Predict button anchored below form
        predict_btn = st.form_submit_button(label="Predict Salary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Output area — show only after predict_btn
    output_col1, output_col2 = st.columns([1, 0.9], gap="large")
    with output_col1:
        if predict_btn:
            # assemble payload exactly as backend expects
            payload = {
                "age": float(age),
                "gender": str(gender).strip(),
                "education": str(education).strip(),
                "marital_status": str(marital_status).strip(),
                "experience_level": str(experience_level).strip(),
                "employment_type": str(employment_type).strip(),
                "job_title": str(job_title).strip(),
                "hours_per_week": float(hours_per_week),
                "employee_residence": str(employee_residence).strip(),
                "company_location": str(company_location).strip(),
                "remote_ratio": float(remote_ratio),
                "company_size": str(company_size).strip()
            }

            # call API
            with st.spinner("Requesting Prediction From Backend..."):
                time.sleep(0.5)
                try:
                    if not PREDICT_ENDPOINT:
                        st.error("Backend URL Not Configured. Set BACKEND_URL Environment Variable.")
                    else:
                        resp = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=20)
                        if resp.status_code == 200:
                            data = resp.json()
                            predicted = float(data.get("predicted_salary_usd", data.get("predicted_salary", 0.0)))
                            low = data.get("low") or predicted * 0.85
                            high = data.get("high") or predicted * 1.15

                            # store in session history
                            st.session_state.history.insert(0, {
                                "ts": datetime.utcnow().isoformat(),
                                "payload": payload,
                                "predicted": predicted,
                                "low": low,
                                "high": high
                            })
                            st.session_state.last_result = {"predicted": predicted, "low": low, "high": high}
                            st.session_state.last_payload = payload

                        else:
                            # try decode JSON error
                            try:
                                err = resp.json()
                            except Exception:
                                err = resp.text
                            st.error(f"API Error {resp.status_code}: {err}")
                            st.session_state.last_result = None

                except requests.exceptions.RequestException as e:
                    st.error(f"Network Error: {e}")
                    st.session_state.last_result = None

        # Display result if exists
        if st.session_state.last_result:
            result = st.session_state.last_result
            predicted = result["predicted"]
            low = result["low"]
            high = result["high"]

            # Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted,
                number={"prefix": "$", "valueformat": ",.0f"},
                title={"text": "Annual Salary (USD)", "font": {"size": 16}},
                gauge={
                    "axis": {"range": [0, max(200000, high * 1.2)]},
                    "bar": {"color": "#0066ff"},
                    "steps": [
                        {"range": [0, predicted * 0.6], "color": "#eef6ff"},
                        {"range": [predicted * 0.6, predicted * 0.9], "color": "#e6f2ff"},
                        {"range": [predicted * 0.9, predicted * 1.2], "color": "#dff7ff"}
                    ]
                }
            ))
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"<div style='text-align:center; margin-top:10px;'>"
                        f"<div class='salary-val'>${predicted:,.0f}</div>"
                        f"<div class='small-muted'>Per Year</div>"
                        f"<div style='margin-top:12px; color:var(--muted)'>Expected Range</div>"
                        f"<div style='font-weight:700; margin-top:6px;'>${float(low):,.0f} - ${float(high):,.0f}</div>"
                        f"</div>", unsafe_allow_html=True)

        else:
            st.info("Predicted Salary Will Appear Here After Clicking Predict.")

    with output_col2:
        # recent history
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Recent Predictions")
        if not st.session_state.history:
            st.markdown("<div class='small-muted'>No Predictions Yet.</div>", unsafe_allow_html=True)
        else:
            # show up to 6 recent
            for h in st.session_state.history[:6]:
                ts = datetime.fromisoformat(h["ts"]).strftime("%b %d %Y • %I:%M %p")
                st.markdown(f"**${h['predicted']:,.0f}**  •  {h['payload']['job_title'].title()}  ")
                st.markdown(f"<div class='small-muted'>{ts} — {h['payload']['employee_residence']}</div>", unsafe_allow_html=True)
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# ANALYSIS TAB
# -------------------------
with tab_analysis:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Dataset & System Analysis", unsafe_allow_html=True)
    st.markdown("Below Are Quick Dataset KPIs Provided By The Backend (If Available).", unsafe_allow_html=True)

    if st.button("Fetch Analysis From Backend"):
        with st.spinner("Fetching Analysis..."):
            time.sleep(0.4)
            try:
                if not BACKEND_URL:
                    st.error("Set BACKEND_URL Environment Variable.")
                else:
                    resp = requests.get(f"{BACKEND_URL}/analyze", headers=HEADERS, timeout=20)
                    if resp.status_code == 200:
                        summary = resp.json().get("summary", {})
                        cols = st.columns(3)
                        cols[0].metric("Records", f"{summary.get('record_count', 'N/A'):,}")
                        cols[1].metric("Average Salary (USD)", f"${summary.get('average_salary', 'N/A'):,.2f}" if summary.get('average_salary') else "N/A")
                        cols[2].metric("Max Salary (USD)", f"${summary.get('max_salary', 'N/A'):,.2f}" if summary.get('max_salary') else "N/A")
                        st.markdown("#### Raw Summary")
                        st.json(summary)
                    else:
                        try:
                            err = resp.json()
                        except Exception:
                            err = resp.text
                        st.error(f"API Error {resp.status_code}: {err}")
            except Exception as e:
                st.error(f"Request Failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# MODEL INSIGHTS TAB
# -------------------------
with tab_insights:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Model Insights & Feature Importance", unsafe_allow_html=True)
    st.markdown("Click The Button To Request Top Features From The Backend.", unsafe_allow_html=True)

    if st.button("Fetch Model Insights"):
        with st.spinner("Getting Model Insights..."):
            time.sleep(0.4)
            try:
                if not BACKEND_URL:
                    st.error("Set BACKEND_URL Environment Variable.")
                else:
                    resp = requests.get(f"{BACKEND_URL}/explain", headers=HEADERS, timeout=20)
                    if resp.status_code == 200:
                        top = resp.json().get("top_features", [])
                        if top:
                            df = pd.DataFrame(top)
                            df["feature"] = df["feature"].apply(lambda x: str(x).replace("_", " ").title())
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("No Feature Importance Data Returned.")
                    else:
                        try:
                            err = resp.json()
                        except Exception:
                            err = resp.text
                        st.error(f"API Error {resp.status_code}: {err}")
            except Exception as e:
                st.error(f"Request Failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Footer
# -------------------------
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay — Developed By <b>Yuvaraja P</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
