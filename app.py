
%%writefile app.py
import streamlit as st
import pandas as pd
from datetime import date
import io

st.set_page_config(page_title="SEMP Demo", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 SEMP – Supported Employment Management Platform (Demo)")
st.caption("Full BRD9 + ADM 2023-09 + ERD demo • Permanent hosted version")

# --- In-memory data ---
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.individuals = pd.DataFrame([
        {"TABS_ID": "T10001", "NAME": "John Smith", "STATUS": "Active"},
        {"TABS_ID": "T10002", "NAME": "Maria Lopez", "STATUS": "Disenrolled"},
        {"TABS_ID": "T10003", "NAME": "Ahmed Khan", "STATUS": "Active"},
    ])
    st.session_state.quarterly = pd.DataFrame([
        {"TABS_ID": "T10001", "QUARTER": "2025 Q3", "STATUS_TYPE": "Enrolled", "CIE_COMPLIANT_FLAG": "Y", "HOURS": 145},
        {"TABS_ID": "T10002", "QUARTER": "2025 Q3", "STATUS_TYPE": "Disenrolled", "CIE_COMPLIANT_FLAG": "Y", "HOURS": 80},
        {"TABS_ID": "T10003", "QUARTER": "2025 Q3", "STATUS_TYPE": "Enrolled", "CIE_COMPLIANT_FLAG": "N", "HOURS": 210},
    ])
    st.session_state.sessions = pd.DataFrame(columns=["TABS_ID", "SESSION_DATE", "STAFF", "SERVICE_TYPE", "LOCATION_TYPE", "DURATION_MINUTES", "DESCRIPTION"])

# --- Sidebar ---
role = st.sidebar.selectbox("Role", ["Agency Staff", "Central Office"])
quarter = st.sidebar.selectbox("Quarter", ["2025 Q3 (Open)"])

# --- Dashboard ---
st.header("Agency Dashboard")
df = st.session_state.quarterly.copy()
def flag(row):
    if row["STATUS_TYPE"] == "Disenrolled": return "🟡 Disenrolled"
    if row["CIE_COMPLIANT_FLAG"] == "N": return "🔴 Missing CIE"
    if row["HOURS"] > 200: return "🟠 Intensity warning"
    return "🟢 Ready"
df["Flag"] = df.apply(flag, axis=1)
st.dataframe(df, use_container_width=True, hide_index=True)

selected = st.selectbox("Select person", df["TABS_ID"])

# --- Individual Profile ---
st.header(f"Profile – {selected}")
person = st.session_state.individuals[st.session_state.individuals["TABS_ID"] == selected].iloc[0]
st.metric("Name", person["NAME"])

tab1, tab2, tab3 = st.tabs(["Service Sessions", "Job + CIE", "Submit"])

with tab1:
    with st.form("session"):
        date = st.date_input("Date", date.today())
        staff = st.text_input("Staff", "Jane Doe")
        service = st.selectbox("Service", ["Job Development", "Follow-Along", "Benefits Counseling"])
        location = st.selectbox("Location", ["Integrated Community", "Worksite", "Virtual"])
        dur = st.number_input("Minutes", 60, 480, 120)
        desc = st.text_area("Notes")
        if st.form_submit_button("Save Session"):
            new = pd.DataFrame([{"TABS_ID": selected, "SESSION_DATE": date, "STAFF": staff, "SERVICE_TYPE": service,
                                 "LOCATION_TYPE": location, "DURATION_MINUTES": dur, "DESCRIPTION": desc}])
            st.session_state.sessions = pd.concat([st.session_state.sessions, new], ignore_index=True)
            st.success("Session saved!")

    st.dataframe(st.session_state.sessions[st.session_state.sessions["TABS_ID"] == selected])

with tab2:
    st.checkbox("CIE Verified (Attachment #1)", value=True)
    st.number_input("Hourly Wage", 15.50)

with tab3:
    if st.button("✅ Submit Quarter with Attestation", type="primary"):
        if st.checkbox("I attest everything is accurate per ADM 2023-09"):
            st.success("Submitted! Carry-forward applied.")
            st.balloons()
