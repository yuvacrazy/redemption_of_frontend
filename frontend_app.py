# frontend_app.py
"""
SmartPay — Streamlit Frontend (Improved UI)
- Purple glassy palette
- Tabs: Home / Predict / History
- Predict button visible (large, glassy) and only shows output after click
- Payload matches backend schema (12 fields)
"""

import os
import time
from datetime import datetime
from typing import Dict, Any

import streamlit as st
import requests
import plotly.graph_objects as go

# ----------------------------
# CONFIG
# ----------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "https://redemption-of-ai.onrender.com/").rstrip("/")  # e.g. https://smartpay-ai-backend.onrender.com
API_KEY = os.getenv("API_KEY")
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None

HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["x-api-key"] = API_KEY

st.set_page_config(page_title="SmartPay — Salary Prediction", page_icon="💜", layout="wide")

# ----------------------------
# CSS Styling (purple glassy)
# ----------------------------
st.markdown(
    """
    <style>
    :root{
      --bg1:#0b0320; --bg2:#22063a;
      --accent1:#7c3aed; --accent2:#9f7cff;
      --muted:#c9bff6;
    }
    .stApp { background: linear-gradient(180deg,var(--bg1), var(--bg2)); color:#f7eefc; }
    .title { font-size:42px; font-weight:800; margin-bottom:6px; color:#fff; }
    .subtitle { color:var(--muted); margin-bottom:18px; }
    .glass { background: rgba(255,255,255,0.03); border-radius:14px; padding:18px; border:1px solid rgba(255,255,255,0.04); box-shadow: 0 12px 30px rgba(0,0,0,0.45); }
    .small { color:var(--muted); font-size:13px; }
    .card-title { font-weight:700; color:#fff; margin-bottom:8px; }

    /* Style the Streamlit button reliably */
    .stButton>button {
        background: linear-gradient(90deg,var(--accent1), var(--accent2)) !important;
        color: white !important;
        border-radius:12px !important;
        padding: 14px 18px !important;
        font-weight:800 !important;
        font-size:16px !important;
        width:100% !important;
        box-shadow: 0 12px 36px rgba(124,58,237,0.28) !important;
        border: none !important;
        transition: transform .12s ease;
    }
    .stButton>button:hover { transform: translateY(-3px) !important; box-shadow: 0 20px 50px rgba(124,58,237,0.36) !important; }

    /* Smaller input visual */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        background: rgba(255,255,255,0.02) !important;
        color: #fff !important;
        border-radius:8px !important;
        padding:8px !important;
        border: 1px solid rgba(255,255,255,0.03) !important;
    }
    footer { color: #d9ccff; text-align:center; margin-top:22px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header
# ----------------------------
st.markdown("<div class='title'>SmartPay — Ai Powered Salary Prediction System</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Predict · Analyze · Understand · Your Market Salary</div>", unsafe_allow_html=True)

# ----------------------------
# Session state
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

# ----------------------------
# Tabs
# ----------------------------
tab_home, tab_predict, tab_history = st.tabs(["Home", "Predict", "History"])

# ----------------------------
# HOME Tab
# ----------------------------
with tab_home:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Project Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>SmartPay Is An Ai Powered Salary Prediction System Built With A FastAPI Backend (LightGBM Model) And A Streamlit Frontend. Use The Predict Tab To Estimate Salaries Based On Candidate Features. The History Tab Stores Recent Predictions Locally In Your Session.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# PREDICT Tab (no st.form — ensures button always visible)
# ----------------------------
with tab_predict:
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Candidate Details</div>", unsafe_allow_html=True)

        # two column inputs
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1)
            education = st.selectbox("Education", ["High School", "Bachelor'S Degree", "Master'S Degree", "PhD", "Other"], index=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer Not To Say"], index=0)
            experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior"], index=0)
        with c2:
            hours_per_week = st.slider("Hours Per Week", min_value=1, max_value=100, value=40)
            job_title = st.text_input("Job Title", value="Software Engineer")
            marital_status = st.selectbox("Marital Status", ["Never Married", "Married", "Divorced", "Other"], index=0)

        # residence / employer details
        st.markdown("<hr/>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            employee_residence = st.text_input("Employee Residence (Country)", value="India")
            remote_ratio = st.selectbox("Remote Ratio", [0, 25, 50, 75, 100], index=0, format_func=lambda x: f"{x}%")
        with c4:
            company_location = st.text_input("Company Location (Country)", value="India")
            company_size = st.selectbox("Company Size", ["S", "M", "L"], index=1)

        employment_type = st.selectbox("Employment Type", ["FT", "PT", "CT", "FL"], index=0)

        st.markdown("</div>", unsafe_allow_html=True)

        # Anchor the predict button outside any hidden form
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        predict_clicked = st.button("Predict Salary", help="Click To Predict Salary", use_container_width=True)

    # Right column: output placeholder (only shown after click)
    with right:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Prediction Result</div>", unsafe_allow_html=True)
        result_box = st.empty()
        note_box = st.empty()
        st.markdown("<div class='small'>Prediction Appears Only After Clicking The Predict Button.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Perform prediction only when button clicked
    if predict_clicked:
        # Build payload matching backend schema
        payload = {
            "age": float(age),
            "gender": gender.title(),
            "education": education.title(),
            "marital_status": marital_status.title(),
            "experience_level": experience_level,  # backend expects 'junior' etc.
            "employment_type": employment_type,
            "job_title": job_title.title(),
            "hours_per_week": float(hours_per_week),
            "employee_residence": employee_residence.title(),
            "company_location": company_location.title(),
            "remote_ratio": float(remote_ratio),
            "company_size": company_size
        }

        # UX spinner
        with st.spinner("Contacting SmartPay Engine..."):
            time.sleep(0.5)  # small delay for polish
            try:
                if not PREDICT_ENDPOINT:
                    raise RuntimeError("BACKEND_URL Not Configured. Set BACKEND_URL Environment Variable.")
                resp = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=18)

                if resp.status_code != 200:
                    # attempt to show JSON error
                    try:
                        body = resp.json()
                    except Exception:
                        body = resp.text
                    note_box.error(f"API Error {resp.status_code} — {body}")
                else:
                    data = resp.json()
                    predicted = float(data.get("predicted_salary_usd", data.get("predicted_salary", 0.0)))
                    low = float(data.get("low", predicted * 0.85))
                    high = float(data.get("high", predicted * 1.15))

                    # save history
                    st.session_state.history.insert(0, {
                        "ts": datetime.utcnow().isoformat(),
                        "payload": payload,
                        "predicted": predicted,
                        "low": low,
                        "high": high
                    })
                    st.session_state.last_prediction = {"predicted": predicted, "low": low, "high": high, "payload": payload}

                    # Render gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=predicted,
                        number={"prefix": "$", "valueformat": ",.0f"},
                        title={"text": "Annual Salary (USD)", "font": {"size": 14}},
                        gauge={
                            "axis": {"range": [0, max(200000, high * 1.2)]},
                            "bar": {"color": "#b794f4"},
                            "steps": [
                                {"range": [0, predicted * 0.6], "color": "rgba(124,58,237,0.08)"},
                                {"range": [predicted * 0.6, predicted * 0.9], "color": "rgba(159,127,255,0.06)"},
                                {"range": [predicted * 0.9, predicted * 1.2], "color": "rgba(199,210,254,0.04)"}
                            ],
                        }
                    ))
                    fig.update_layout(margin=dict(t=8,b=8,l=8,r=8), height=280, paper_bgcolor="rgba(0,0,0,0)")

                    result_box.plotly_chart(fig, use_container_width=True)
                    result_box.markdown(f"<div style='text-align:center; font-weight:800; font-size:20px; margin-top:6px;'>${predicted:,.0f}</div>", unsafe_allow_html=True)
                    result_box.markdown(f"<div style='text-align:center; color:#d9ccff'>Estimated Range: ${low:,.0f} - ${high:,.0f}</div>", unsafe_allow_html=True)

            except requests.exceptions.RequestException as e:
                note_box.error(f"Network Error: {e}")
            except Exception as e:
                note_box.error(f"Prediction Failed: {e}")

# ----------------------------
# HISTORY Tab
# ----------------------------
with tab_history:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Recent Predictions</div>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("<div class='small'>No Predictions Yet. Generate One In The Predict Tab.</div>", unsafe_allow_html=True)
    else:
        for item in st.session_state.history[:12]:
            ts = datetime.fromisoformat(item["ts"]).strftime("%b %d %Y • %I:%M %p")
            with st.expander(f"${item['predicted']:,.0f} — {item['payload']['job_title']} — {ts}", expanded=False):
                st.json(item["payload"])
                st.write(f"Predicted: ${item['predicted']:,.0f}")
                st.write(f"Range: ${item['low']:,.0f} - ${item['high']:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Footer
# ----------------------------
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay — Developed By <b>Yuvaraja P</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
