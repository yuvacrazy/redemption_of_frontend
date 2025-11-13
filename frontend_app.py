# frontend_app.py
"""
SmartPay Frontend (Theme Picker + Animated Header + Predict Progress)
- Tabs: Home | Prediction | Analysis | Model Insights
- Theme Picker: Light / Dark / Corporate
- Animated Header and Predict Progress micro-interaction
- Payload matches backend schema of 12 fields
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
# Config / Env
# -------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "").rstrip("/")  # e.g. https://smartpay-ai-backend.onrender.com
API_KEY = os.getenv("API_KEY", "")
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None
HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["x-api-key"] = API_KEY

st.set_page_config(page_title="SmartPay — Salary Intelligence", page_icon="💼", layout="wide")

# -------------------------
# Theme definitions (CSS variable sets)
# -------------------------
THEMES = {
    "Light": {
        "--bg": "linear-gradient(180deg,#f6fbff 0%, #eef9ff 100%)",
        "--text": "#042231",
        "--muted": "#6b7a86",
        "--card-bg": "rgba(255,255,255,0.98)",
        "--accent1": "#0066ff",
        "--accent2": "#00d4ff",
        "--glass-border": "rgba(5,30,60,0.04)",
    },
    "Dark": {
        "--bg": "linear-gradient(180deg,#0b1220 0%, #0f1724 100%)",
        "--text": "#e8f1f8",
        "--muted": "#9fb4c9",
        "--card-bg": "rgba(14,18,25,0.85)",
        "--accent1": "#4fd1c5",
        "--accent2": "#7f5af0",
        "--glass-border": "rgba(255,255,255,0.04)",
    },
    "Corporate": {
        "--bg": "linear-gradient(135deg,#fbfdff 0%, #eef6ff 100%)",
        "--text": "#052033",
        "--muted": "#5b7786",
        "--card-bg": "linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,255,0.95))",
        "--accent1": "#0b6ef6",
        "--accent2": "#00b4d8",
        "--glass-border": "rgba(6,30,50,0.06)",
    },
}

# -------------------------
# UI: theme picker (top right via sidebar)
# -------------------------
with st.sidebar:
    st.markdown("## Theme")
    selected_theme = st.selectbox("Choose Theme", options=list(THEMES.keys()), index=2)
    st.markdown("---")
    st.markdown("**Backend**")
    st.text_input("Backend URL", value=BACKEND_URL or "", key="sb_backend_url", help="Set BACKEND_URL environment variable for production")
    st.text_input("API Key (optional)", value=API_KEY or "", key="sb_api_key", help="Set API_KEY environment variable for production")
    st.markdown("---")
    st.markdown("SmartPay • Developed By Yuvaraja P", unsafe_allow_html=True)

# Apply chosen theme variables into CSS
vars = THEMES[selected_theme]
css = f"""
<style>
:root {{
  --bg: {vars['--bg']};
  --text: {vars['--text']};
  --muted: {vars['--muted']};
  --card-bg: {vars['--card-bg']};
  --accent1: {vars['--accent1']};
  --accent2: {vars['--accent2']};
  --glass-border: {vars['--glass-border']};
}}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial;
}}
.block-container {{ padding-top: 18px; padding-left:36px; padding-right:36px; }}
.hero-title {{
  font-size:42px; font-weight:800; margin:0;
  background: linear-gradient(90deg,var(--accent1), var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-size: 200% 100%;
  animation: slideGradient 6s linear infinite;
}}
@keyframes slideGradient {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
.small-muted {{ color: var(--muted); font-size:13px; }}
.glass {{
  background: var(--card-bg);
  border-radius:14px; padding:20px;
  box-shadow: 0 10px 30px rgba(2,20,40,0.06);
  border: 1px solid var(--glass-border);
}}
.accent-btn {{
  background: linear-gradient(90deg,var(--accent1), var(--accent2));
  color: white; font-weight:700; border-radius:10px; padding:10px 16px; width:100%; border:none;
}}
.salary-val {{ color: var(--accent1); font-size:36px; font-weight:800; }}
.kpi {{ font-weight:700; font-size:20px; color: var(--text); }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'>", unsafe_allow_html=True)
st.markdown("<div><h1 class='hero-title'>SmartPay — AI Salary Intelligence</h1><div class='small-muted'>Predict. Analyze. Explain. Production Ready.</div></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Session state
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_payload" not in st.session_state:
    st.session_state.last_payload = None

# -------------------------
# Tabs
# -------------------------
tab_home, tab_pred, tab_analysis, tab_insights = st.tabs(["🏠 Home", "💰 Prediction", "📊 Analysis", "🧠 Model Insights"])

# -------------------------
# HOME
# -------------------------
with tab_home:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("## Project Overview", unsafe_allow_html=True)
    st.markdown("SmartPay Is An AI-Powered Salary Prediction System With Secure Backend (FastAPI) And A Professional Frontend (Streamlit).", unsafe_allow_html=True)
    st.markdown("### Quick Features", unsafe_allow_html=True)
    st.markdown("- Production Ready Backend With API Key Auth  \n- Clean, Themed UI With Animated Header  \n- Predictive Model (Regression) For Annual Salary", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PREDICTION
# -------------------------
with tab_pred:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Predict Salary", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Fill The Form And Press Predict — Output Appears Only After Clicking Predict.</div>", unsafe_allow_html=True)

    with st.form("predict_form"):
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1)
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

        predict_btn = st.form_submit_button("Predict Salary", help="Click to get prediction")

    st.markdown("</div>", unsafe_allow_html=True)

    # Output area
    out_col_left, out_col_right = st.columns([1, 0.9], gap="large")
    with out_col_left:
        if predict_btn:
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

            # Animated micro-interaction: progress bar + dynamic status messages
            status = st.empty()
            progress = st.progress(0)
            status_texts = [
                "Sending Request To SmartPay Backend...",
                "Model Inference Running — Aggregating Features...",
                "Computing Salary Estimate...",
                "Finalizing Results..."
            ]
            try:
                # start network call concurrently with UX: call early (we'll await result after progress)
                resp_holder = {}
                def call_api():
                    if not PREDICT_ENDPOINT:
                        raise RuntimeError("BACKEND_URL Not Configured.")
                    r = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=25)
                    return r

                # start request (synchronous) but still update UI so user sees progress
                # We'll perform small progress animation while request runs
                start = time.time()
                r = None
                try:
                    r = call_api()
                except Exception as e:
                    r = None
                    api_err = e

                # Animate progress for up to ~2.0 seconds while waiting for/after request
                total_steps = 40
                for i in range(total_steps):
                    pct = int((i+1)/total_steps * 100)
                    progress.progress(min(pct, 100))
                    # update status text rotating
                    txt = status_texts[i % len(status_texts)]
                    status.markdown(f"**{txt}**")
                    time.sleep(0.03)  # smooth animate (~1.2s)
                progress.progress(100)
                status.markdown("**Done — Showing Result**")

                if r is None:
                    # network error
                    raise RuntimeError(f"Prediction request failed: {api_err}")

                if r.status_code == 200:
                    data = r.json()
                    predicted = float(data.get("predicted_salary_usd", data.get("predicted_salary", 0.0)))
                    low = data.get("low") or predicted * 0.85
                    high = data.get("high") or predicted * 1.15

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
                    try:
                        err = r.json()
                    except Exception:
                        err = r.text
                    st.error(f"API Error {r.status_code}: {err}")
                    st.session_state.last_result = None

            except Exception as e:
                st.error(f"Prediction Failed: {e}")
                st.session_state.last_result = None
            finally:
                progress.empty()
                status.empty()

        # Display result only if present
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
                    "bar": {"color": vars['--accent1']},
                    "steps": [
                        {"range": [0, predicted * 0.6], "color": "#f7fbff"},
                        {"range": [predicted * 0.6, predicted * 0.9], "color": "#eef7ff"},
                        {"range": [predicted * 0.9, predicted * 1.2], "color": "#e6fbff"}
                    ]
                }
            ))
            fig.update_layout(margin=dict(t=6, b=6, l=6, r=6), height=260)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"<div style='text-align:center; margin-top:10px;'>"
                        f"<div class='salary-val'>${predicted:,.0f}</div>"
                        f"<div class='small-muted'>Per Year</div>"
                        f"<div style='margin-top:12px; color:var(--muted)'>Expected Range</div>"
                        f"<div style='font-weight:700; margin-top:6px;'>${float(low):,.0f} - ${float(high):,.0f}</div>"
                        f"</div>", unsafe_allow_html=True)
        else:
            st.info("Predicted Salary Will Appear Here After Clicking Predict.")

    with out_col_right:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Recent Predictions")
        if not st.session_state.history:
            st.markdown("<div class='small-muted'>No Predictions Yet.</div>", unsafe_allow_html=True)
        else:
            for h in st.session_state.history[:6]:
                ts = datetime.fromisoformat(h["ts"]).strftime("%b %d %Y • %I:%M %p")
                st.markdown(f"**${h['predicted']:,.0f}**  •  {h['payload']['job_title'].title()}  ")
                st.markdown(f"<div class='small-muted'>{ts} — {h['payload']['employee_residence']}</div>", unsafe_allow_html=True)
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# ANALYSIS Tab
# -------------------------
with tab_analysis:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Dataset & System Analysis", unsafe_allow_html=True)
    st.markdown("Click Fetch To Get Backend Dataset Summary.", unsafe_allow_html=True)
    if st.button("Fetch Analysis"):
        try:
            if not BACKEND_URL:
                st.error("Set BACKEND_URL environment variable.")
            else:
                resp = requests.get(f"{BACKEND_URL}/analyze", headers=HEADERS, timeout=20)
                if resp.status_code == 200:
                    sm = resp.json().get("summary", {})
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Records", f"{sm.get('record_count', 'N/A'):,}")
                    c2.metric("Avg Salary (USD)", f"${sm.get('average_salary', 'N/A'):,.2f}" if sm.get('average_salary') else "N/A")
                    c3.metric("Max Salary (USD)", f"${sm.get('max_salary', 'N/A'):,.2f}" if sm.get('max_salary') else "N/A")
                    st.json(sm)
                else:
                    st.error(f"API Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# INSIGHTS Tab
# -------------------------
with tab_insights:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Model Insights", unsafe_allow_html=True)
    if st.button("Fetch Model Insights"):
        try:
            if not BACKEND_URL:
                st.error("Set BACKEND_URL environment variable.")
            else:
                resp = requests.get(f"{BACKEND_URL}/explain", headers=HEADERS, timeout=20)
                if resp.status_code == 200:
                    top = resp.json().get("top_features", [])
                    if top:
                        df = pd.DataFrame(top)
                        df["feature"] = df["feature"].apply(lambda x: str(x).replace("_", " ").title())
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No feature importance returned.")
                else:
                    st.error(f"API Error: {resp.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay — Developed By <b>Yuvaraja P</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
