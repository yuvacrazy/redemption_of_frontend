# frontend_app.py
"""
SmartPay Frontend (Streamlit)
- Theme Picker (Light/Dark/Corporate)
- Lottie header (Laptop Productivity) + Lottie loader (AI Spinning Cube)
- Animated microcopy and progress during prediction
- Tabs: Home | Prediction | Analysis | Model Insights
- Backend URL & API key configurable via sidebar (no code change required)
- Payload / API flow unchanged (POST to {BACKEND_URL}/predict)
"""

import os
import time
from datetime import datetime
from typing import List, Optional

import requests
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Lottie helper
from streamlit_lottie import st_lottie  # ensure streamlit-lottie in requirements.txt

# ----------------------------
# CONFIG (edit at runtime in sidebar; set env vars if you prefer)
# ----------------------------
DEFAULT_BACKEND = os.getenv("BACKEND_URL", "").rstrip("/")  # leave blank or set env var
DEFAULT_API_KEY = os.getenv("API_KEY", "")  # set env var in deploy for production

# ----------------------------
# LOTTIE ASSET URLs (CDN)
# - Header (Laptop Productivity) and Loader (AI Spinning Cube)
# - If you prefer other animations, swap the URLs.
# ----------------------------
HEADER_LOTTIE_URL = "https://assets9.lottiefiles.com/packages/lf20_jyhigb2b.json"  # Laptop-like/professional
LOADER_LOTTIE_URL = "https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json"   # spinner / cube style

# ----------------------------
# Utility: load lottie JSON (cached)
# ----------------------------
@st.cache_data(show_spinner=False)
def load_lottie_url(url: str):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ----------------------------
# Theme definitions
# ----------------------------
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


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="SmartPay • AI Salary Intelligence",
                   page_icon="💼", layout="wide")


# ----------------------------
# Sidebar: backend config + theme
# ----------------------------
with st.sidebar:
    st.markdown("## SmartPay Settings")
    backend_input = st.text_input("Backend Root URL (e.g. https://your-backend.com)", value=DEFAULT_BACKEND,
                                 placeholder="Leave blank and set it here", help="Enter your backend root URL. App will POST to {URL}/predict")
    api_key_input = st.text_input("API Key (optional)", value=DEFAULT_API_KEY,
                                  placeholder="Optional: API key for backend", help="If your backend uses API key auth, paste it here.")
    st.markdown("---")
    st.markdown("## UI Theme")
    theme_choice = st.selectbox("Theme", options=list(THEMES.keys()), index=2)
    st.markdown("---")
    st.markdown("Developed By **Yuvaraja P** — Final Year CSE (IoT), Paavai Engineering College", unsafe_allow_html=True)

# Compute predict endpoint from sidebar input
BACKEND_URL = backend_input.rstrip("/") if backend_input else ""
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict" if BACKEND_URL else None

# HEADERS for requests
HEADERS = {"Content-Type": "application/json"}
if api_key_input:
    HEADERS["x-api-key"] = api_key_input


# ----------------------------
# Apply theme CSS
# ----------------------------
vars = THEMES[theme_choice]
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
  font-size:40px; font-weight:800; margin:0;
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
  border-radius:12px; padding:18px;
  box-shadow: 0 8px 30px rgba(2,20,40,0.06);
  border: 1px solid var(--glass-border);
}}
.stButton>button {{
  background: linear-gradient(90deg,var(--accent1), var(--accent2));
  color: white; border:none; border-radius:10px; padding:10px 14px; font-weight:700;
}}
.salary-val {{ color: var(--accent1); font-size:34px; font-weight:800; }}
.kpi {{ font-weight:700; font-size:18px; color: var(--text); }}
.microcopy {{ color: var(--muted); font-size:14px; margin-top:6px; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)


# ----------------------------
# Header: Lottie + Title (Laptop Productivity)
# ----------------------------
header_lottie_json = load_lottie_url(HEADER_LOTTIE_URL)
st.markdown("<div style='display:flex; gap:18px; align-items:center;'>", unsafe_allow_html=True)
if header_lottie_json:
    # render Lottie (small)
    st_lottie(header_lottie_json, height=80, key="header_lottie")
st.markdown("<div><h1 class='hero-title'>SmartPay — AI Salary Intelligence</h1>"
            "<div class='small-muted'>Predict · Analyze · Explain · Export Reports</div></div>",
            unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# Initialize session state
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_payload" not in st.session_state:
    st.session_state.last_payload = None


# ----------------------------
# Tabs
# ----------------------------
tab_home, tab_pred, tab_analysis, tab_insights = st.tabs(["🏠 Home", "💰 Prediction", "📊 Analysis", "🧠 Model Insights"])


# ----------------------------
# HOME
# ----------------------------
with tab_home:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("## Project Overview")
    st.markdown("SmartPay Is An AI-Powered Salary Prediction System With A Secure FastAPI Backend And A Professional Streamlit Frontend.")
    st.markdown("**Quick Highlights**")
    st.markdown("- Production-grade Backend With Optional API Key Authentication  \n- Interactive, Themed Frontend With Lottie Animations  \n- Predictive Model (LightGBM) For Annual Salary Estimation")
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# PREDICTION Tab
# ----------------------------
with tab_pred:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Predict Salary")
    st.markdown("<div class='small-muted'>Fill the form and press Predict. The output appears only after you click Predict.</div>", unsafe_allow_html=True)

    # --- form
    with st.form("predict_form"):
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1)
            education = st.selectbox("Education", ["High School", "Bachelor's", "Master's", "PhD", "Other"])
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer Not To Say"])
            marital_status = st.selectbox("Marital Status", ["Never Married", "Married", "Divorced", "Widowed", "Other"])
            hours_per_week = st.slider("Hours Per Week", min_value=1, max_value=100, value=40)
        with col2:
            job_title = st.text_input("Job Title", value="Software Engineer")
            experience_level = st.selectbox("Experience Level", ["junior", "mid", "senior"], index=0)
            employment_type = st.selectbox("Employment Type", ["FT", "PT", "CT", "FL"], index=0)
            employee_residence = st.text_input("Employee Residence (Country)", value="India")
            company_location = st.text_input("Company Location (Country)", value="India")
            remote_ratio = st.selectbox("Remote Ratio (%)", [0, 25, 50, 75, 100], index=0)
            company_size = st.selectbox("Company Size", ["S", "M", "L"], index=1)

        predict_btn = st.form_submit_button("🔍 Predict Salary")

    st.markdown("</div>", unsafe_allow_html=True)

    # Output layout
    left_col, right_col = st.columns([1.2, 0.8], gap="large")

    with left_col:
        if predict_btn:
            # Prepare payload (matches backend schema you showed earlier)
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

            # Microcopy messages (elaborate)
            micro_msgs: List[str] = [
                "Preparing And Validating Inputs...",
                "Encoding Categorical Features...",
                "Applying Job Title Embeddings (TF-IDF + SVD)...",
                "Running Model Inference (LightGBM) ...",
                "Calibrating Output And Confidence Range..."
            ]

            # Show loader Lottie during inference (AI Spinning Cube)
            loader_json = load_lottie_url(LOADER_LOTTIE_URL)

            # placeholders
            status_ph = st.empty()
            micro_ph = st.empty()
            lottie_ph = st.empty()
            prog_ph = st.empty()

            # start request (synchronously) — UI animation runs while waiting
            r = None
            api_err = None
            try:
                if PREDICT_ENDPOINT is None:
                    raise RuntimeError("Backend URL not configured. Paste backend root URL in sidebar (e.g. https://your-backend.com)")

                # Start request
                # We still animate microcopy to show progress; request can be fast or slow.
                # Request is synchronous; microcopy + progress are visual only (no backend change).
                # We intentionally do the request before long animation so small fast responses still show microcopy briefly.
                r = requests.post(PREDICT_ENDPOINT, json=payload, headers=HEADERS, timeout=25)
            except Exception as ex:
                api_err = ex
                r = None

            # Animate microcopy + progress while we have response or until finished animation
            total_ticks = 50
            per_msg_ticks = max(4, total_ticks // max(1, len(micro_msgs)))
            tick = 0
            if loader_json:
                lottie_ph.st_lottie(loader_json, height=140, key=f"loader_{datetime.utcnow().timestamp()}")

            for i, m in enumerate(micro_msgs):
                for _ in range(per_msg_ticks):
                    tick += 1
                    pct = int(tick / (per_msg_ticks * len(micro_msgs)) * 100)
                    if pct > 100:
                        pct = 100
                    prog_ph.progress(pct)
                    status_ph.markdown(f"**{m}**")
                    micro_ph.markdown(f"<div class='microcopy'>Step {i+1}/{len(micro_msgs)}</div>", unsafe_allow_html=True)
                    # if request returned, speed the animation
                    if r is not None:
                        time.sleep(0.02)
                    else:
                        time.sleep(0.05)

            # finalize
            prog_ph.progress(100)
            status_ph.markdown("**Finalizing Result...**")
            micro_ph.markdown("<div class='microcopy'>Almost Done...</div>", unsafe_allow_html=True)
            time.sleep(0.12)

            # Clear loader early if exists
            lottie_ph.empty()

            # Handle response
            if r is None:
                st.error(f"Prediction request failed: {api_err or 'No backend URL provided.'}")
                st.session_state.last_result = None
            else:
                if r.status_code == 200:
                    j = r.json()
                    predicted = float(j.get("predicted_salary_usd", j.get("predicted_salary", 0.0)))
                    low = j.get("low") or predicted * 0.85
                    high = j.get("high") or predicted * 1.15

                    # store history
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
                        err_json = r.json()
                    except Exception:
                        err_json = r.text
                    st.error(f"API Error {r.status_code}: {err_json}")
                    st.session_state.last_result = None

            # clear placeholders
            prog_ph.empty()
            status_ph.empty()
            micro_ph.empty()

        # Display result if available
        if st.session_state.last_result:
            res = st.session_state.last_result
            predicted = res["predicted"]
            low = res["low"]
            high = res["high"]

            # Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted,
                number={"prefix": "$", "valueformat": ",.0f"},
                title={"text": "Annual Salary (USD)", "font": {"size": 16}},
                gauge={
                    "axis": {"range": [0, max(200000, high * 1.2)]},
                    "bar": {"color": vars["--accent1"]},
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
            st.info("Predicted salary will appear here after clicking Predict.")

    with right_col:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Recent Predictions")
        if not st.session_state.history:
            st.markdown("<div class='small-muted'>No predictions yet.</div>", unsafe_allow_html=True)
        else:
            for entry in st.session_state.history[:6]:
                ts = datetime.fromisoformat(entry["ts"]).strftime("%b %d %Y • %I:%M %p")
                st.markdown(f"**${entry['predicted']:,.0f}**  •  {entry['payload']['job_title'].title()}  ")
                st.markdown(f"<div class='small-muted'>{ts} • {entry['payload']['employee_residence']}</div>", unsafe_allow_html=True)
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# ANALYSIS Tab
# ----------------------------
with tab_analysis:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Dataset & System Analysis")
    st.markdown("Click the button to fetch backend analytics (records, avg salary, min/max).")
    if st.button("Fetch Analysis"):
        if not BACKEND_URL:
            st.error("Backend URL is not set in the sidebar.")
        else:
            try:
                resp = requests.get(f"{BACKEND_URL}/analyze", headers=HEADERS, timeout=20)
                if resp.status_code == 200:
                    summary = resp.json().get("summary", {})
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Records", f"{summary.get('record_count', 'N/A'):,}")
                    c2.metric("Avg Salary (USD)", f"${summary.get('average_salary', 'N/A'):,.2f}" if summary.get('average_salary') else "N/A")
                    c3.metric("Max Salary (USD)", f"${summary.get('max_salary', 'N/A'):,.2f}" if summary.get('max_salary') else "N/A")
                    st.json(summary)
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Failed to fetch analysis: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# MODEL INSIGHTS Tab
# ----------------------------
with tab_insights:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Model Insights / Explainability")
    if st.button("Fetch Model Insights"):
        if not BACKEND_URL:
            st.error("Backend URL is not set in the sidebar.")
        else:
            try:
                resp = requests.get(f"{BACKEND_URL}/explain", headers=HEADERS, timeout=20)
                if resp.status_code == 200:
                    top_features = resp.json().get("top_features", [])
                    if top_features:
                        df = pd.DataFrame(top_features)
                        df["feature"] = df["feature"].apply(lambda x: str(x).replace("_", " ").title())
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No top features returned by backend.")
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Failed to fetch insights: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# Footer
# ----------------------------
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown("<footer>SmartPay — Developed By <b>Yuvaraja P</b> | Final Year CSE (IoT), Paavai Engineering College</footer>", unsafe_allow_html=True)
