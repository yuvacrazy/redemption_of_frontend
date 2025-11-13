# frontend_app.py
"""
SmartPay - Streamlit Frontend (Professional UI)
- Single-file Streamlit app that calls your FastAPI backend /predict endpoint.
- Expects environment variables BACKEND_URL and API_KEY (optional).
- Stores prediction history in session_state (transient).
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, Any

import streamlit as st
import requests
import plotly.graph_objects as go

# -----------------------------
# Configuration
# -----------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "https://redemption-of-ai.onrender.com/").rstrip("/")
API_KEY = os.getenv("API_KEY", "")  # set in Render/host secrets
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None
HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["x-api-key"] = API_KEY

st.set_page_config(page_title="SmartPay — Salary Intelligence", page_icon="💼", layout="wide")

# -----------------------------
# CSS / Visual Theme
# -----------------------------
st.markdown(
    """
    <style>
    :root{
      --accent-1: #0072ff;
      --accent-2: #00c6ff;
      --card-bg: rgba(255,255,255,0.98);
      --glass: rgba(255,255,255,0.75);
    }
    body {
      background: linear-gradient(135deg, #f6fbff 0%, #eef8fb 50%, #f8fcff 100%);
      color: #0b2538;
      font-family: 'Inter', system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .main-header {
      text-align: center;
      margin-top: 10px;
      margin-bottom: 10px;
    }
    .title {
      font-size: 44px;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 4px;
      color: #061826;
    }
    .subtitle {
      color: #6b7a86;
      font-size: 15px;
      margin-bottom: 26px;
    }
    .glass-card {
      background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.90));
      border-radius: 12px;
      padding: 26px;
      box-shadow: 0 10px 30px rgba(14, 30, 37, 0.08);
      border: 1px solid rgba(15, 40, 60, 0.06);
    }
    .big-predict {
      background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
      color: white !important;
      font-weight: 700;
      font-size: 16px;
      border-radius: 10px;
      padding: 12px 18px;
      width: 100%;
      border: none;
    }
    .small-muted { color:#92a0ad; font-size:13px; }
    .salary-value { color: var(--accent-1); font-size: 42px; font-weight: 800; }
    footer { color:#6b7a86; text-align:center; padding-top:28px; }
    /* tighten streamlit default paddings a bit */
    .block-container { padding-top: 20px; padding-left:40px; padding-right:40px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header / Hero
# -----------------------------
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.markdown("<div class='title'>Discover Your <span style='background:linear-gradient(90deg,#0072ff,#00c6ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent'>Salary Potential</span></div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Get accurate salary predictions powered by AI and real market data. Understand your worth and make informed career decisions.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Session state: history
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {timestamp, payload, predicted_salary}

# -----------------------------
# Main layout - left: form, right: output/insights
# -----------------------------
left_col, right_col = st.columns([1.2, 0.9], gap="large")

# ---------- Left: Form ----------
with left_col:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # Input grid
    form = st.form(key="predict_form", clear_on_submit=False)

    with form:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", min_value=16, max_value=100, value=25, step=1)
            education = st.selectbox("Education Level", options=[
                "High School", "Bachelor's Degree", "Master's Degree", "PhD", "Other"
            ])
            gender = st.selectbox("Gender", options=["Male", "Female", "Other", "Prefer not to say"])
        with c2:
            hours_per_week = st.slider("Hours per Week", 1, 100, value=40)
            job_title = st.text_input("Job Title", value="Data Engineer")
            marital_status = st.selectbox("Marital Status", options=["Never Married", "Married", "Divorced", "Widowed", "Other"])

        # optional: extra fields expected by backend
        st.markdown("<hr/>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            remote_ratio = st.selectbox("Remote Ratio", options=[0, 25, 50, 75, 100], index=0, format_func=lambda x: f"{x}%")
        with c4:
            company_size = st.selectbox("Company Size", options=["S", "M", "L"], index=1, help="S=Small, M=Medium, L=Large")

        submit_btn = st.form_submit_button(label="Predict My Salary", help="Click to get a prediction", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Right: Output ----------
with right_col:
    # salary card placeholder
    st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='padding-top:8px; padding-bottom:6px;'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; align-items:center; justify-content:center; flex-direction:column;'>", unsafe_allow_html=True)
    st.markdown("<div style='width:72px; height:72px; border-radius:50%; background:linear-gradient(135deg,#0072ff,#00c6ff); display:flex; align-items:center; justify-content:center; box-shadow:0 6px 18px rgba(0,114,255,0.12); margin-bottom:12px;'> <svg width='28' height='28' viewBox='0 0 24 24' fill='white' xmlns='http://www.w3.org/2000/svg'><path d='M3 17h4l5-9 5 7 4-11' stroke='white' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' fill='none'></path></svg></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; font-size:18px;'>Predicted Salary</div>", unsafe_allow_html=True)
    salary_area = st.empty()
    range_area = st.empty()
    st.markdown("</div></div></div>", unsafe_allow_html=True)

    # small profile summary card
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'>", unsafe_allow_html=True)
    st.markdown("<div><div style='font-weight:700; margin-bottom:6px;'>Your Profile</div><div class='small-muted'>Quick summary of inputs</div></div>", unsafe_allow_html=True)
    st.markdown("</div>")
    st.markdown("<div style='padding-top:12px;'></div>", unsafe_allow_html=True)

    # two-column profile details
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown(f"**Education**  \n{education}")
        st.markdown(f"**Hours / week**  \n{hours_per_week} hours")
    with pcol2:
        st.markdown(f"**Job Title**  \n{job_title}")
        st.markdown(f"**Age**  \n{age} years")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Predict: when form submitted
# -----------------------------
def call_predict_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call backend predict endpoint and return JSON. Raises on errors."""
    if not PREDICT_ENDPOINT:
        raise RuntimeError("BACKEND_URL not configured. Set BACKEND_URL environment variable.")
    try:
        resp = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=18)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request error: {e}")
    if resp.status_code == 200:
        return resp.json()
    else:
        # propagate server error message if JSON else text
        try:
            text = resp.json()
        except Exception:
            text = resp.text
        raise RuntimeError(f"API returned status {resp.status_code}: {text}")

# ---------- handle submission ----------
if submit_btn:
    # compose payload for your backend. keys must match backend schema.
    payload = {
        "age": age,
        "education": education,
        "job_title": job_title,
        "hours_per_week": hours_per_week,
        "gender": gender,
        "marital_status": marital_status,
        "remote_ratio": remote_ratio,
        "company_size": company_size,
        # add additional backend-expected keys if needed (use defaults)
    }

    # show progress and call
    with st.spinner("Contacting SmartPay engine..."):
        # small UX pause to show spinner and avoid flash
        time.sleep(0.6)
        try:
            result = call_predict_api(payload)
            # expected field predicted_salary_usd in response
            predicted = float(result.get("predicted_salary_usd") or result.get("predicted_salary") or 0.0)
            # optional: if backend returns lower/upper range, use it
            low = result.get("low") or result.get("low_usd") or max(0, predicted * 0.85)
            high = result.get("high") or result.get("high_usd") or predicted * 1.15

            # save to history
            st.session_state.history.insert(0, {
                "ts": datetime.now().isoformat(),
                "payload": payload,
                "predicted": predicted,
                "low": low,
                "high": high
            })

            # render salary card & gauge
            salary_area.empty()
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted,
                number={"prefix": "$", "valueformat": ",.0f"},
                title={"text": "Annual Salary (USD)", "font": {"size": 16}},
                gauge={
                    "axis": {"range": [0, max(200000, high * 1.2)]},
                    "bar": {"color": "#0072ff"},
                    "steps": [
                        {"range": [0, predicted * 0.6], "color": "#eef6ff"},
                        {"range": [predicted * 0.6, predicted * 0.9], "color": "#e6f6ff"},
                        {"range": [predicted * 0.9, predicted * 1.2], "color": "#dff7ff"}
                    ],
                }
            ))
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260)
            st.plotly_chart(fig, use_container_width=True)

            # textual value + range
            range_area.markdown(f"<div style='text-align:center; padding-top:10px;'>"
                                f"<div class='salary-value'>${predicted:,.0f}</div>"
                                f"<div class='small-muted'>per year</div>"
                                f"<div style='margin-top:12px; color:#5f6f7b;'>Expected Range</div>"
                                f"<div style='font-weight:700; margin-top:6px;'>${float(low):,.0f} - ${float(high):,.0f}</div>"
                                f"</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Prediction failed — {e}")
            # show backend debug link if available
            if BACKEND_URL:
                st.info(f"Check backend: {BACKEND_URL}/health")

# -----------------------------
# History panel (bottom)
# -----------------------------
st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### Prediction History")
if len(st.session_state.history) == 0:
    st.markdown("<div class='small-muted'>No predictions yet. Use the form to generate your first prediction.</div>", unsafe_allow_html=True)
else:
    for h in st.session_state.history[:8]:
        ts = datetime.fromisoformat(h["ts"]).strftime("%b %d %Y • %I:%M %p")
        with st.expander(f"${h['predicted']:,.0f} — {h['payload']['job_title']} ({ts})", expanded=False):
            st.json(h["payload"], expanded=False)
            st.markdown(f"**Predicted:** ${h['predicted']:,.0f}")
            st.markdown(f"**Range:** ${float(h['low']):,.0f} - ${float(h['high']):,.0f}")
            st.markdown(f"**Time:** {ts}")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay – Developed by <b>Redemption of IoT</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
