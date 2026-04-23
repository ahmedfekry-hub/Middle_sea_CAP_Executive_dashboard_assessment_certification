from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Middle Sea CAP Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Middle Sea CAP Dashboard")
st.caption("Embedded HTML dashboard packaged for Streamlit Community Cloud deployment.")

html_file = Path(__file__).parent / "middle_sea_cap_executive_dashboard_v9_assessment_certification.html"
html_content = html_file.read_text(encoding="utf-8")

components.html(html_content, height=6500, scrolling=True)
