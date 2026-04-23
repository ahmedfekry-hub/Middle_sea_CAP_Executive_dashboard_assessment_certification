
from pathlib import Path
import base64
import json

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Middle Sea CAP Assessment & Certification Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "middle_sea_violations.csv"
LOGO_PATH = BASE_DIR / "middle_sea_logo.jpg"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="cp1256")
    df["media_count"] = pd.to_numeric(df["media_count"], errors="coerce").fillna(0).astype(int)

    def parse_lat_lon(x):
        try:
            data = json.loads(x)
            if isinstance(data, list) and data:
                return data[0].get("latitude"), data[0].get("longitude")
        except Exception:
            pass
        return None, None

    coords = df["location"].apply(parse_lat_lon)
    df["lat"] = coords.apply(lambda t: t[0])
    df["lon"] = coords.apply(lambda t: t[1])
    df["google_maps"] = df.apply(
        lambda r: f"https://www.google.com/maps?q={r['lat']},{r['lon']}"
        if pd.notna(r["lat"]) and pd.notna(r["lon"])
        else "",
        axis=1,
    )

    def categorize(v: str) -> str:
        txt = str(v)
        if any(k in txt for k in ["الحواجز المؤقتة", "سياج أرضي", "التحويلة المرورية", "فانوس", "انارة تحذيرية", "متهالكة وتالفة", "خطرًا على المشاة", "الحركة المرورية"]):
            return "Protective Cover / الحماية والتغطية"
        if any(k in txt for k in ["لوحات تحمل اسم", "لوحة لبيانات التصريح", "شعار الجهة الخدمية", "شعار المقاول", "إرشادية", "تحذيرية", "لوحات"]):
            return "Signage / اللوحات والإشارات"
        if any(k in txt for k in ["ردم الحفر", "نظافة موقع العمل", "إزالة المخلفات", "رمي مخلفات", "رمي نواتج", "التشوين", "إتلاف الأرصفة", "الاسفلت", "الأساس الحجري"]):
            return "Cleanup / النظافة وإعادة الوضع"
        if any(k in txt for k in ["كابل", "كيبل", "فايبر", "ليف", "fiber", "cable"]):
            return "Cable Installation / تركيبات الكابلات"
        return "Other Compliance / مخالفات أخرى"

    df["category"] = df["violation_name"].map(categorize)
    df["status"] = "Open Baseline / مفتوح - خط أساس"
    df["record_id"] = range(1, len(df) + 1)
    return df


def logo_b64() -> str:
    return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")


def inject_css():
    st.markdown(
        f"""
        <style>
        .main .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}
        .hero {{
            background: linear-gradient(135deg, #0f3d8c, #1f6feb);
            border-radius: 22px;
            padding: 24px 28px;
            color: white;
            box-shadow: 0 12px 32px rgba(15,23,42,.18);
            margin-bottom: 16px;
        }}
        .hero-grid {{
            display: grid;
            grid-template-columns: 130px 1fr;
            gap: 18px;
            align-items: center;
        }}
        .hero-logo {{
            width: 120px;
            height: 120px;
            background: rgba(255,255,255,.98);
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,.16);
        }}
        .hero-logo img {{
            width: 100%;
            height: auto;
            object-fit: contain;
        }}
        .hero-title {{
            font-size: 30px;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 8px;
        }}
        .hero-sub {{
            font-size: 14px;
            opacity: .95;
            line-height: 1.5;
            margin-bottom: 10px;
        }}
        .hero-badge {{
            display: inline-block;
            padding: 10px 16px;
            border-radius: 999px;
            font-size: 16px;
            font-weight: 800;
            background: linear-gradient(90deg, #ffffff, #c7e0ff);
            color: #0f172a;
            box-shadow: 0 4px 14px rgba(0,0,0,.15);
        }}
        .metric-card {{
            background: white;
            border: 1px solid #d9e2ef;
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(15,30,70,.05);
        }}
        .section-card {{
            background: white;
            border: 1px solid #d9e2ef;
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(15,30,70,.05);
        }}
        .mini-note {{
            background:#fff7ed;
            border:1px solid #fed7aa;
            color:#9a3412;
            padding:12px 14px;
            border-radius:12px;
            font-size:13px;
            margin-bottom: 12px;
        }}
        .assessment-card {{
            background: #ffffff;
            border: 1px solid #d9e2ef;
            border-radius: 18px;
            padding: 16px;
            height: 100%;
        }}
        .assessment-anchor {{
            background: #f4f7fb;
            border-radius: 14px;
            padding: 12px;
            color: #475569;
            margin: 10px 0 12px 0;
        }}
        .pass-box {{
            border-left: 4px solid #93c5fd;
            background: #f8fbff;
            padding: 10px 12px;
            margin-top: 8px;
            color: #334155;
        }}
        .trigger-box {{
            border:1px solid #e9d5ff;
            border-left:5px solid #7c3aed;
            background:#faf5ff;
            border-radius:12px;
            padding:12px 14px;
            margin-bottom:10px;
        }}
        .small-muted {{
            color:#607087;
            font-size:12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-grid">
                <div class="hero-logo">
                    <img src="data:image/jpeg;base64,{logo_b64()}" alt="Middle Sea Telecom Logo">
                </div>
                <div>
                    <div class="hero-title">Middle Sea CAP Assessment & Certification Dashboard</div>
                    <div class="hero-sub">
                        Native Streamlit executive dashboard for CAP governance, field assessment, escalation control,
                        and certification readiness using the uploaded violations dataset.
                    </div>
                    <div class="hero-badge">Prepared by Eng/Ahmed Fekry (Quality & Performance Director)</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filtered_df(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters / المرشحات")
    districts = ["All"] + sorted(df["district_name"].dropna().unique().tolist())
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())

    district = st.sidebar.selectbox("District / الحي", districts, index=0)
    category = st.sidebar.selectbox("CAP Category / فئة الخطة", categories, index=0)
    search = st.sidebar.text_input("Search violation text / بحث", "")
    scope = st.sidebar.selectbox(
        "View Scope / نطاق العرض",
        ["All imported records / كل السجلات", "CAP core categories only / فئات الخطة الأساسية فقط"],
    )

    result = df.copy()
    if district != "All":
        result = result[result["district_name"] == district]
    if category != "All":
        result = result[result["category"] == category]
    if search.strip():
        s = search.strip().lower()
        result = result[
            result["violation_name"].astype(str).str.lower().str.contains(s, na=False)
            | result["district_name"].astype(str).str.lower().str.contains(s, na=False)
        ]
    if scope.startswith("CAP core"):
        result = result[result["category"] != "Other Compliance / مخالفات أخرى"]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Visible rows: {len(result):,}")
    return result


def metric_strip(df: pd.DataFrame):
    top_district = df["district_name"].value_counts()
    top_dist_label = f"{top_district.index[0]} ({top_district.iloc[0]})" if not top_district.empty else "-"
    media_total = int(df["media_count"].sum())
    cap_count = int(df[df["category"] != "Other Compliance / مخالفات أخرى"].shape[0])

    cols = st.columns(5)
    vals = [
        ("Total Violations / إجمالي المخالفات", f"{len(df):,}", ""),
        ("Districts Impacted / الأحياء المتأثرة", f"{df['district_name'].nunique():,}", ""),
        ("Media Evidence Count / عدد المرفقات", f"{media_total:,}", ""),
        ("CAP-Covered Violations / مخالفات ضمن الخطة", f"{cap_count:,}", ""),
        ("Top District Share / أعلى حي", top_dist_label, ""),
    ]
    for col, (label, value, delta) in zip(cols, vals):
        with col:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label, value, delta)
            st.markdown("</div>", unsafe_allow_html=True)


def charts_section(df: pd.DataFrame):
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        cat_counts = (
            df.groupby("category", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=False)
        )
        fig = px.bar(
            cat_counts,
            x="category",
            y="count",
            text="count",
            title="Violations by CAP Category / المخالفات حسب الفئة",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        dist_counts = (
            df.groupby("district_name", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=False)
            .head(12)
        )
        fig = px.bar(
            dist_counts,
            x="district_name",
            y="count",
            text="count",
            title="Top Districts / الأحياء الأعلى",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def repeated_and_heatmap(df: pd.DataFrame):
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        top_v = (
            df.groupby("violation_name", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=False)
            .head(12)
        )
        fig = px.bar(
            top_v,
            x="count",
            y="violation_name",
            orientation="h",
            text="count",
            title="Top Repeated Violations / أكثر المخالفات تكرارًا",
        )
        fig.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        piv = pd.pivot_table(
            df,
            index="category",
            columns="district_name",
            values="record_id",
            aggfunc="count",
            fill_value=0,
        )
        fig = px.imshow(
            piv,
            text_auto=True,
            aspect="auto",
            title="District Heatmap – Baseline CAP Exposure",
            color_continuous_scale="Blues",
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def governance_section():
    st.header("2. Corrective Actions & Responsible Parties")
    st.caption("Sequenced in governance order: escalation control first, operating path second, trigger rules third, then ownership.")

    st.subheader("2.1 Escalation Matrix Process")
    esc = pd.DataFrame(
        [
            ["Implementation", "Site Supervisor / (Dynamic)", "Site Engineer / (Dynamic)", "Project Manager / (District)", "Program/Projects Manager / Ghiyath Al-kaed"],
            ["Quality", "Quality Supervisor / Engineer / (Dynamic)", "Project Manager / (District)", "HSEQ Director / Ahmed Fekry", "Program/Projects Manager / Ghiyath Al-kaed"],
            ["Permit", "Permit Task Owner / (District)", "Permit Manager / Muneer Yousef", "Project Manager / (District)", "Program/Projects Manager / Ghiyath Al-kaed"],
            ["Design", "Designer / (District)", "Designer Manager / (District)", "Program/Projects Manager / Ghiyath Al-kaed", ""],
            ["Fiber Purchasing material", "Purchasing Task Owner / Zeyad Mansour", "Program/Projects Manager / Ghiyath Al-kaed", "", ""],
        ],
        columns=["Stage", "Level 1", "Level 2", "Level 3", "Level 4"],
    )
    st.dataframe(esc, use_container_width=True, hide_index=True)

    st.subheader("2.2 How the Escalation Path Must Operate in Practice")
    op1, op2 = st.columns(2)
    with op1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.write("**Field detection / الرصد الميداني**")
        st.write("Any violation identified during inspection must be logged the same day with district, exact issue text, photo evidence, and owner name.")
        st.write("**First correction window / مهلة المعالجة الأولى**")
        st.write("The assigned site owner must correct routine findings within 24 hours and public-safety findings within the same shift wherever exposure exists.")
        st.markdown("</div>", unsafe_allow_html=True)
    with op2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.write("**Level escalation / انتقال التصعيد**")
        st.write("If the finding remains unresolved after the allowed window, the case must move to the next escalation level without waiting for the next weekly meeting.")
        st.write("**Verification closure / إقفال التحقق**")
        st.write("No item is treated as closed until the Quality Supervisor re-inspects, accepts evidence, and confirms that the same point does not present repeat exposure.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("2.3 Escalation Triggers That Must Be Applied")
    t1, t2 = st.columns(2)
    trigger_left = [
        "Any public-safety exposure such as missing barrier, missing warning lighting, or unsafe open work zone must be escalated immediately on the same day.",
        "Any item not corrected within 24–48 hours must move up one level automatically.",
        "Any repeated finding on the same street, district, or code type within the same recovery cycle must be escalated to Project Manager level.",
    ]
    trigger_right = [
        "Five or more open findings in one district, or a flat / worsening weekly trend, requires management review and a documented action reset.",
        "Any permit, reinstatement, or scope deviation not corrected within the agreed SLA must be escalated through the governance path without delay.",
        "Any unresolved item with potential STC visibility, municipality penalty impact, or client complaint risk must be flagged for senior review.",
    ]
    with t1:
        for i, txt in enumerate(trigger_left, 1):
            st.markdown(f'<div class="trigger-box"><strong>Trigger {i}</strong>{txt}</div>', unsafe_allow_html=True)
    with t2:
        for i, txt in enumerate(trigger_right, 4):
            st.markdown(f'<div class="trigger-box"><strong>Trigger {i}</strong>{txt}</div>', unsafe_allow_html=True)

    st.subheader("2.4 Corrective Actions & Responsible Parties")
    actions = pd.DataFrame(
        [
            ["Signage failures", "Install compliant project boards and execution team / utility branding at each active site before start of work; replace missing permit signage within 24 hours; verify night visibility.", "Field Team Lead", "Quality Supervisor", "Project Manager"],
            ["Site cleanup", "Clear debris, stockpiles, and waste at end of each shift; restore site boundary and housekeeping before demobilization; close punch list same day.", "Field Team Lead", "Quality Supervisor", "Project Manager"],
            ["Incorrect cable / civil installation", "Correct trench reinstatement, asphalt cutting, and scope/permit deviations; stop any activity outside permit until re-approved; rework defective locations within 72 hours.", "Project Manager", "Quality Supervisor", "Field Team Lead"],
            ["Protective cover / traffic safety control failures", "Deploy compliant barriers, reflective warning devices, temporary protection, and traffic safety controls before excavation starts; replace damaged barriers immediately.", "Quality Supervisor", "Field Team Lead", "Project Manager"],
        ],
        columns=["Category", "Corrective Action", "Primary Responsible", "Verification Owner", "Escalation Owner"],
    )
    st.dataframe(actions, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Quality Supervisor Role – Concrete Weekly Duties")
    st.markdown("""
    - Start each day with a district priority route covering active and previously failed sites.
    - Verify physical closure with photo evidence, exact location reference, and code-by-code sign-off.
    - Stop work immediately where permit, barrier, warning-light, or public-safety controls are not in place.
    - Escalate any repeated finding on the same street or district within 24 hours to the Project Manager.
    - Issue a daily log listing closed items, rejected closure claims, and next-day reinspection points.
    """)
    st.markdown("</div>", unsafe_allow_html=True)


def inspection_and_assessment(df: pd.DataFrame):
    st.header("Inspection Protocol / بروتوكول التفتيش")
    i1, i2, i3, i4 = st.columns(4)
    items = [
        ("Daily / يومي", "Protective cover, signage, unsafe public exposure.", "High Risk"),
        ("Twice Weekly / مرتان أسبوعيًا", "Cleanup and restoration progress by district.", "Medium"),
        ("Weekly / أسبوعي", "Trend review, repeated violations, PM escalation.", "Management"),
        ("Re-inspection / إعادة تفتيش", "Within 48 hours for any failed checkpoint.", "Mandatory"),
    ]
    for col, item in zip([i1, i2, i3, i4], items):
        with col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.write(f"**{item[0]}**")
            st.caption(item[1])
            st.info(item[2])
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="mini-note">Required evidence: before/after photo, district, exact violation text, responsible supervisor, and timestamp.</div>', unsafe_allow_html=True)

    st.header("CAP Assessment & Certification")

    # Dynamic anchors from filtered data
    def anchor(cat, n=3):
        subset = df[df["category"] == cat].head(n)
        rows = []
        for _, r in subset.iterrows():
            rows.append(
                {
                    "violation": r["violation_name"],
                    "district": r["district_name"],
                    "loc": f"({r['lon']},{r['lat']})" if pd.notna(r["lat"]) and pd.notna(r["lon"]) else "",
                }
            )
        return rows

    signage_rows = anchor("Signage / اللوحات والإشارات")
    cleanup_rows = anchor("Cleanup / النظافة وإعادة الوضع")
    cable_rows = anchor("Cable Installation / تركيبات الكابلات")
    protection_rows = anchor("Protective Cover / الحماية والتغطية")

    st.subheader("1) Scenario-Based Assessment Questions")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Signage failures",
        "Site cleanup / reinstatement",
        "Incorrect cable installations / exposed technical works",
        "Protective cover / barrier failures",
    ])

    def scenario_cards(rows, prompts):
        cols = st.columns(3)
        for col, row, prompt in zip(cols, rows if rows else [{"violation":"No matched record","district":"-","loc":""}]*3, prompts):
            with col:
                st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
                st.markdown(f"### {prompt['title']}")
                st.markdown(
                    f"""<div class="assessment-anchor">
                    <b>Dataset anchor:</b> {row['violation']}<br>
                    <b>Location:</b> {row['loc']} {row['district']}
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.write(prompt["question"])
                st.markdown(f'<div class="pass-box">{prompt["pass"]}</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    with tab1:
        scenario_cards(signage_rows, [
            {
                "title": "Missing warning lights on diversion",
                "question": "During a night audit, you find a work zone with no warning lights on the full traffic diversion. State the violation, why it matters, and the immediate action you order before leaving site.",
                "pass": "Pass = identifies signage / traffic warning failure, links risk to traffic/public safety, requires immediate lighting installation and same-day escalation if not corrected."
            },
            {
                "title": "Missing mandatory project identification board",
                "question": "A crew is active but the site lacks the board showing project owner, consultant, and execution team. Can the supervisor approve temporary continuation, or must work be paused/escalated?",
                "pass": "Pass = states traceability/compliance risk, requires installation of board before normal continuation or escalation if repeated."
            },
            {
                "title": "No reflective warning sign for pedestrian hazard",
                "question": "You observe an open work zone near pedestrians with no reflective signage or ground fence. What CAP checkpoint failed and what minimum controls must be installed immediately?",
                "pass": "Pass = references traffic/pedestrian protection checkpoint, requires reflective signage plus fencing/barrier controls."
            },
        ])
    with tab2:
        scenario_cards(cleanup_rows, [
            {
                "title": "Excavation not backfilled after work completion",
                "question": "A completed trench remains open and the area has not been reinstated. Explain the violation, required corrective action, and whether same-day closure evidence is mandatory.",
                "pass": "Pass = requires backfilling/reinstatement and photo evidence before closure, escalates if completion exceeds CAP timeline."
            },
            {
                "title": "Poor site cleanliness during and after execution",
                "question": "The site is cluttered with materials and waste after work. What should be recorded in the weekly status report and when would this move from field correction to PM escalation?",
                "pass": "Pass = identifies housekeeping breach, records action owner/date/evidence, escalates if repeated or unresolved beyond allowed timeline."
            },
            {
                "title": "Spoil left near excavation perimeter",
                "question": "Spoil from excavation is left beside the project boundary, creating access obstruction. What response is expected from a certified Quality Supervisor?",
                "pass": "Pass = identifies cleanup/waste control breach, orders immediate removal, documents risk, escalates if crew/resources unavailable."
            },
        ])
    with tab3:
        scenario_cards(cable_rows, [
            {
                "title": "Exposed wiring / lighting extension hazard",
                "question": "You find exposed lighting wires and a fallen lantern inside the active work area. Treat this as a proxy technical installation safety scenario: what is the decision authority and why?",
                "pass": "Pass = treats as safety-critical condition, stops unsafe activity, secures zone, escalates immediately to PM / responsible manager."
            },
            {
                "title": "Damage to public pavement during infrastructure works",
                "question": "After route execution, pavement damage is visible at the handover point. Can the supervisor sign off corrective completion before civil reinstatement is verified?",
                "pass": "Pass = recognizes technical/civil interface failure, withholds approval until reinstatement verified, logs evidence and owner."
            },
            {
                "title": "Ambiguous technical nonconformity with no specialist present",
                "question": "The field team argues the exposed extension is temporary and acceptable. What evidence and escalation steps are required before accepting this explanation?",
                "pass": "Pass = requires risk-based rejection of informal explanation, demands rectification evidence and immediate escalation for unsafe temporary installation."
            },
        ])
    with tab4:
        scenario_cards(protection_rows, [
            {
                "title": "Temporary barriers installed incorrectly",
                "question": "Barrier placement does not comply with approved methods around the site. What corrective actions can the supervisor approve independently, and what would force escalation?",
                "pass": "Pass = can order immediate repositioning/replacement, escalates if materials unavailable, repeated breach, or public hazard remains."
            },
            {
                "title": "Worn / damaged temporary barriers",
                "question": "You find damaged, non-uniform temporary barriers. How should the supervisor classify severity and decide whether to keep work active?",
                "pass": "Pass = classifies as control failure, replaces damaged barriers before continued exposure to public traffic, escalates if safety not restored."
            },
            {
                "title": "Missing ground fence and reflective controls",
                "question": "At a pedestrian crossing, there is neither a ground fence nor reflective control. What is the minimum acceptable closure package before the item can be marked corrected?",
                "pass": "Pass = requires installed fence/barrier + reflective warning + evidence photo; no closure without full control set."
            },
        ])

    st.subheader("2) Practical Field Assessments")
    p1, p2, p3 = st.columns(3)
    district_mix = df["district_name"].value_counts().head(3)
    with p1:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        top_d = district_mix.index[0] if len(district_mix) > 0 else "-"
        top_rows = df[df["district_name"] == top_d]["violation_name"].value_counts().head(4)
        st.markdown(f"### Mock Inspection A - High-volume urban zone")
        st.write(f"**District:** {top_d}")
        st.write("**Focus:** Night-time traffic safety and signage discipline")
        st.write("**Observed mix in dataset:**")
        st.write("\n".join([f"- {c} — {v}" for v, c in top_rows.items()]) if len(top_rows) else "- No records")
        st.markdown('<div class="pass-box">Supervisor must inspect warning lights, temporary barriers, project board, cleanliness, and reinstatement evidence. Zero missed checkpoints.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        mid_d = district_mix.index[1] if len(district_mix) > 1 else "-"
        mid_rows = df[df["district_name"] == mid_d]["violation_name"].value_counts().head(4)
        st.markdown("### Mock Inspection B - Mixed reinstatement and housekeeping")
        st.write(f"**District:** {mid_d}")
        st.write("**Focus:** Barrier setup plus reinstatement after excavation")
        st.write("**Observed mix in dataset:**")
        st.write("\n".join([f"- {c} — {v}" for v, c in mid_rows.items()]) if len(mid_rows) else "- No records")
        st.markdown('<div class="pass-box">Supervisor must classify each breach correctly, assign action owner/date, and trigger escalation where safety controls are incomplete.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with p3:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        low_d = district_mix.index[2] if len(district_mix) > 2 else "-"
        low_rows = df[df["district_name"] == low_d]["violation_name"].value_counts().head(4)
        st.markdown("### Mock Inspection C - Low-volume but complex edge case")
        st.write(f"**District:** {low_d}")
        st.write("**Focus:** Signage + storage outside permitted work area")
        st.write("**Observed mix in dataset:**")
        st.write("\n".join([f"- {c} — {v}" for v, c in low_rows.items()]) if len(low_rows) else "- No records")
        st.markdown('<div class="pass-box">Supervisor must prove judgement under ambiguity: permit compliance, identification board, barriers, and material storage control.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("3) Competency Rubrics for Decision Authority")
    rubric = pd.DataFrame([
        ["Missing warning light / reflective control", "Supervisor may order immediate installation and hold closure", "Public traffic exposure remains, no crew response, repeated breach, or correction not same shift", "Immediate", "PM + Area Lead"],
        ["Missing project identification board", "Supervisor can require same-day installation before normal continuation", "Repeat offense, active work continues without compliance, or permit mismatch", "≤ 1 day", "PM"],
        ["Poor cleanliness / spoil left on site", "Supervisor can order cleanup and verify photo evidence", "Unresolved by agreed deadline, repeated pattern, or access/public complaint", "≤ 3 days", "PM"],
        ["Open trench not reinstated", "Supervisor can reject closure and require reinstatement evidence", "Risk to public/property, no reinstatement resources, or deadline > CAP threshold", "Immediate to ≤ 3 days", "PM / Escalation authority"],
        ["Incorrect barrier placement / damaged barrier", "Supervisor can replace/reposition when resources available", "Any live safety exposure or resource shortage preventing correction", "Immediate", "PM + safety chain"],
        ["Exposed wires / fallen lantern", "No independent approval of continued exposure", "Always escalate after making area safe", "Immediate", "PM / responsible senior authority"],
    ], columns=["Violation Pattern", "Supervisor Can Approve Independently", "Escalation Trigger", "Required Timeline", "Escalate To"])
    st.dataframe(rubric, use_container_width=True, hide_index=True)

    rc1, rc2, rc3 = st.columns([1, 1, 1])
    with rc1:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        st.markdown("### Decision Authority Rubric")
        st.markdown('<div class="pass-box">Score each decision scenario against five tests: correct violation classification, correct risk rating, correct decision authority, correct CAP action, and correct evidence requirement. Passing threshold: <b>90% overall</b> and <b>100% accuracy</b> on safety-critical escalation cases.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with rc2:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        st.markdown("### Required Decision Scenario Bank")
        st.markdown("""
1. Crew requests 48 more hours to install warning lights on a live diversion.  
2. Site is clean, but the mandatory project board is still missing at handover.  
3. Barrier stock is unavailable and pedestrians are already using the walkway.  
4. Backfilling is complete, but there is no photographic evidence and no timestamp.  
5. Permit duration expired, yet field team says extension is under process.  
6. Exposed electrical extension is claimed to be harmless because work is almost done.  
7. Cleanup completed, but the same district shows the same issue for the third week.  
8. A damaged barrier is present in a low-traffic area during daylight hours only.  
9. Public complaint received before supervisor reaches site.  
10. Consultant accepts temporary signage verbally, but no written approval exists.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    with rc3:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        st.markdown("### Authority Rule")
        st.write("A certified Quality Supervisor may close only what is fully corrected, evidenced, and within defined authority. Anything safety-critical, repeated, resource-blocked, permit-related, or beyond the CAP timeline must move up the escalation chain immediately.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("4) Passing Criteria & Remediation Pathways")
    rp1, rp2, rp3 = st.columns([1, 1, 1])
    with rp1:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        st.markdown("### Passing Thresholds")
        pass_df = pd.DataFrame([
            ["Scenario-based questions", "≥ 80% accuracy on violation identification and corrective action"],
            ["Escalation decisions", "100% accuracy on safety-critical escalation calls"],
            ["Field assessment", "Complete checkpoint coverage with zero critical omissions"],
            ["Decision authority rubric", "≥ 90% correct decisions across at least 15 scenarios"],
            ["Documentation quality", "Weekly report complete, evidence-linked, time-bound, and owner-tagged"],
        ], columns=["Area", "Threshold"])
        st.dataframe(pass_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with rp2:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        st.markdown("### Remediation Pathway")
        st.markdown("""
1. **Below threshold on any component:** fail that component and assign targeted remediation.  
2. **Attempt 1:** repeat related module + mentor review + supervised field drill.  
3. **Attempt 2:** reassessment after cooling period with new mock scenario set.  
4. **Maximum cycle:** two re-attempts; then escalate to leadership for role decision.  
5. **Mandatory retraining triggers:** repeated escalation errors, poor evidence quality, missed safety exposure, or poor report discipline.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    with rp3:
        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
        st.markdown("### Assessor Observation Criteria")
        st.markdown("""
- Inspects methodically and in checkpoint order  
- Classifies violations without guessing  
- Links issue to CAP checkpoint and required timeline  
- Documents owner, deadline, evidence, and escalation flag  
- Communicates findings clearly to field team and PM chain
        """)
        st.markdown("</div>", unsafe_allow_html=True)


def register_section(df: pd.DataFrame):
    st.header("Detailed Violation Register / سجل المخالفات التفصيلي")
    show_df = df[["record_id", "district_name", "violation_name", "category", "media_count", "status", "google_maps"]].rename(
        columns={
            "record_id": "ID",
            "district_name": "District / الحي",
            "violation_name": "Violation / المخالفة",
            "category": "Category / الفئة",
            "media_count": "Media",
            "status": "Status / الحالة",
            "google_maps": "Location",
        }
    )
    st.dataframe(show_df, use_container_width=True, hide_index=True, height=520)


def main():
    inject_css()
    df = load_data()
    hero()
    st.markdown('<div class="mini-note"><strong>Data note / ملاحظة البيانات:</strong> The violations file contains 522 imported records. It does not include an explicit closure status field, so the dashboard treats the dataset as the current baseline open population unless you export an updated status file later.</div>', unsafe_allow_html=True)

    filtered = filtered_df(df)
    metric_strip(filtered)
    charts_section(filtered)
    repeated_and_heatmap(filtered)
    governance_section()
    inspection_and_assessment(filtered)
    register_section(filtered)


if __name__ == "__main__":
    main()
