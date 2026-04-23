from pathlib import Path
import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Middle Sea CAP Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def img_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")

base_dir = Path(__file__).parent
logo_path = base_dir / "middle_sea_logo.jpg"
html_file = base_dir / "middle_sea_cap_executive_dashboard_v9_assessment_certification.html"

logo_b64 = img_to_base64(logo_path)
html_content = html_file.read_text(encoding="utf-8")

st.markdown(
    f'''
    <style>
    .shell-card {{
        background: linear-gradient(135deg, #0f3d8c, #1f6feb);
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 16px;
        color: white;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.18);
    }}
    .shell-grid {{
        display: grid;
        grid-template-columns: 130px 1fr;
        gap: 18px;
        align-items: center;
    }}
    .shell-logo {{
        width: 120px;
        height: 120px;
        border-radius: 16px;
        background: rgba(255,255,255,0.98);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 8px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.14);
    }}
    .shell-logo img {{
        width: 100%;
        height: auto;
        object-fit: contain;
        border-radius: 10px;
    }}
    .shell-title {{
        font-size: 30px;
        font-weight: 800;
        margin: 0 0 6px 0;
    }}
    .shell-meta {{
        font-size: 16px;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #c7e0ff);
        color: #0f172a;
        display: inline-block;
        padding: 10px 16px;
        border-radius: 999px;
        margin-top: 8px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }}
    @media (max-width: 768px) {{
        .shell-grid {{
            grid-template-columns: 1fr;
        }}
        .shell-logo {{
            width: 100px;
            height: 100px;
        }}
        .shell-title {{
            font-size: 24px;
        }}
    }}
    </style>

    <div class="shell-card">
        <div class="shell-grid">
            <div class="shell-logo">
                <img src="data:image/jpeg;base64,{logo_b64}" alt="Middle Sea Telecom Logo" />
            </div>
            <div>
                <div class="shell-title">Middle Sea CAP Assessment & Certification Dashboard</div>
                <div class="shell-meta">Prepared by Eng/Ahmed Fekry (Quality & Performance Director)</div>
            </div>
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

components.html(html_content, height=7200, scrolling=True)
