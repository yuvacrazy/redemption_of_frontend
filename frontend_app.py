# frontend_app.py
"""
SmartPay - Streamlit Frontend (final, backend-aligned)
Sends payload exactly matching backend schema:
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
BACKEND_URL = os.getenv("BACKEND_URL", "https://redemption-of-ai.onrender.com/").rstrip("/")  # e.g. https://smartpay-ai-backend.onrender.com
API_KEY = os.getenv("API_KEY")                      # must match backend API_KEY
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None

HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["x-api-key"] = API_KEY

st.set_page_config(page_title="SmartPay — Salary Intelligence", page_icon="💼", layout="wide")

# ----------------------------
# Styling
# ----------------------------
st.markdown(
    """
    <style>
    :root{ --accent1:#0072ff; --accent2:#00c6ff; }
    .block-container { padding-top: 18px; padding-left: 44px; padding-right: 44px; }
    body { background: linear-gradient(135deg,#f7fbff 0%, #f1fbff 100%); color: #071a2b; font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial; }
    .title { font-size: 44px; font-weight:800; letter-spacing:-0.02em; }
    .subtitle { color:#6b7a86; font-size:15px; margin-bottom:26px; }
    .glass { background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.96)); border-radius:12px; padding:24px; box-shadow: 0 12px 30px rgba(6,30,45,0.06); border:1px solid rgba(9,30,45,0.04); }
    .big-btn { background: linear-gradient(90deg,var(--accent1),var(--accent2)); color:white; font-weight:700; border-radius:10px; padding:12px 18px; border:none; width:100%; }
    .small-muted { color:#8b9aa6; font-size:13px; }
    footer { color:#6b7a86; text-align:center; padding-top:24px; padding-bottom:24px; }
    .salary-val { color:var(--accent1); font-size:40px; font-weight:800; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header / Hero
# ----------------------------
st.markdown(f"<div class='title'>Discover Your <span style='background:linear-gradient(90deg,#0072ff,#00c6ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent'>Salary Potential</span></div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Get accurate salary predictions powered by AI and real market data. Understand your worth and make informed career decisions.</div>", unsafe_allow_html=True)

# ----------------------------
# Session state: history
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # newest first

# ----------------------------
# Layout: form (left) and output (right)
# ----------------------------
col_left, col_right = st.columns([1.2, 0.9], gap="large")

with col_left:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Enter Candidate Details", unsafe_allow_html=True)

    # We include ALL backend-required fields (defaults where appropriate)
    with st.form("predict_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1)
            education = st.selectbox("Education Level", ["High School", "Bachelor's", "Master's", "PhD", "Other"], index=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], index=0)
            experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior"], index=0)  # you chose 'junior' default
        with c2:
            hours_per_week = st.slider("Hours per Week", min_value=1, max_value=100, value=40)
            job_title = st.text_input("Job Title", value="Data Engineer")
            marital_status = st.selectbox("Marital Status", ["Never Married", "Married", "Divorced", "Widowed", "Other"], index=0)
            employment_type = st.selectbox("Employment Type", ["FT", "PT", "CT", "FL"], index=0)  # FT default

        # Residence / company location — you requested India defaults
        c3, c4 = st.columns(2)
        with c3:
            employee_residence = st.text_input("Employee Residence (Country)", value="India")
        with c4:
            company_location = st.text_input("Company Location (Country)", value="India")

        # Other backend fields
        remote_ratio = st.selectbox("Remote Ratio", [0, 25, 50, 75, 100], index=0, format_func=lambda x: f"{x}%")
        company_size = st.selectbox("Company Size", ["S", "M", "L"], index=1, help="S=Small M=Medium L=Large")

        submit = st.form_submit_button("Predict My Salary", help="Click to request prediction", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='glass' style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:center; align-items:center; flex-direction:column;'>", unsafe_allow_html=True)
    st.markdown("<div style='width:64px; height:64px; border-radius:50%; background:linear-gradient(135deg,#0072ff,#00c6ff); display:flex; align-items:center; justify-content:center; box-shadow:0 8px 22px rgba(0,114,255,0.12); margin-bottom:10px;'><svg width='28' height='28' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M3 17h4l5-9 5 7 4-11' stroke='white' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round' /></svg></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; font-size:18px;'>Predicted Salary</div>", unsafe_allow_html=True)
    output_area = st.empty()
    range_area = st.empty()
    st.markdown("</div></div>", unsafe_allow_html=True)

    # profile summary
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("**Profile Summary**  \n<small class='small-muted'>Quick view of input</small>", unsafe_allow_html=True)
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown(f"**Education**  \n{education}")
        st.markdown(f"**Hours / wk**  \n{hours_per_week}")
    with pcol2:
        st.markdown(f"**Job Title**  \n{job_title}")
        st.markdown(f"**Age**  \n{age}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# API call helper
# ----------------------------
def call_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not PREDICT_ENDPOINT:
        raise RuntimeError("BACKEND_URL not configured. Set BACKEND_URL environment variable.")
    try:
        r = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=18)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {e}")
    if r.status_code == 200:
        return r.json()
    else:
        # try to decode json error
        try:
            return {"__error__": True, "status": r.status_code, "body": r.json()}
        except Exception:
            return {"__error__": True, "status": r.status_code, "body": r.text}

# ----------------------------
# Trigger prediction when submitted
# ----------------------------
if submit:
    # Assemble payload EXACTLY matching backend schema (12 fields)
    payload = {
        "age": float(age),
        "gender": gender,
        "education": education,
        "marital_status": marital_status,
        "experience_level": experience_level,
        "employment_type": employment_type,
        "job_title": job_title,
        "hours_per_week": float(hours_per_week),
        "employee_residence": employee_residence,
        "company_location": company_location,
        "remote_ratio": float(remote_ratio),
        "company_size": company_size
    }

    # show spinner + small delay for UX
    with st.spinner("Requesting prediction from SmartPay..."):
        time.sleep(0.6)
        try:
            resp = call_predict(payload)
            if resp.get("__error__"):
                st.error(f"API Error {resp['status']}: {resp['body']}")
            else:
                # expected response model: {"predicted_salary_usd": float}
                predicted = float(resp.get("predicted_salary_usd", resp.get("predicted_salary", 0.0)))
                # optional tolerance range or derive if missing
                low = resp.get("low") or resp.get("low_usd") or max(0.0, predicted * 0.85)
                high = resp.get("high") or resp.get("high_usd") or predicted * 1.15

                # record history
                st.session_state.history.insert(0, {
                    "ts": datetime.utcnow().isoformat(),
                    "payload": payload,
                    "predicted": predicted,
                    "low": low,
                    "high": high
                })

                # show gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=predicted,
                    number={"prefix": "$", "valueformat": ",.0f"},
                    title={"text": "Annual Salary (USD)", "font": {"size": 16}},
                    gauge={
                        "axis": {"range": [0, max(200000, high * 1.2)]},
                        "bar": {"color": "#0072ff"},
                        "steps": [
                            {"range": [0, predicted * 0.6], "color": "#f4fbff"},
                            {"range": [predicted * 0.6, predicted * 0.9], "color": "#e9f8ff"},
                            {"range": [predicted * 0.9, predicted * 1.2], "color": "#dff7ff"}
                        ],
                    }
                ))
                fig.update_layout(margin=dict(t=6, b=6, l=6, r=6), height=260)
                output_area.plotly_chart(fig, use_container_width=True)

                # textual range & main value
                range_area.markdown(f"""
                    <div style='text-align:center; padding-top:8px;'>
                      <div class='salary-val'>${predicted:,.0f}</div>
                      <div class='small-muted'>per year</div>
                      <div style='margin-top:12px; color:#5f6f7b;'>Expected Range</div>
                      <div style='font-weight:700; margin-top:6px;'>${float(low):,.0f} - ${float(high):,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)

        except Exception as ex:
            st.error(f"Prediction request failed: {ex}")
            if BACKEND_URL:
                st.info(f"Check backend health: {BACKEND_URL}/health")

# ----------------------------
# Show recent predictions (history)
# ----------------------------
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.markdown("### Prediction History", unsafe_allow_html=True)
if not st.session_state.history:
    st.markdown("<div class='small-muted'>No predictions yet. Generate one from the form above.</div>", unsafe_allow_html=True)
else:
    for i, item in enumerate(st.session_state.history[:8]):
        ts = datetime.fromisoformat(item["ts"]).strftime("%b %d %Y • %I:%M %p")
        with st.expander(f"${item['predicted']:,.0f} · {item['payload']['job_title']} · {ts}", expanded=False):
            st.write("**Inputs**")
            st.json(item["payload"])
            st.write("**Prediction**")
            st.write(f"Predicted: ${item['predicted']:,.0f}")
            st.write(f"Range: ${float(item['low']):,.0f} - ${float(item['high']):,.0f}")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Footer
# ----------------------------
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay — Developed by <b>Redemption of IoT</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
