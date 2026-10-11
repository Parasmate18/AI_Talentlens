"""
AI Resume Screening - recruitment dashboard (UI only).

All analysis is done by the backend (miniproject.py):
    job = analyze_job()
    parsed_resume, result = analyze_resume_file(uploaded_file, job)

Run with:  streamlit run streamlit_app.py
"""

import html as _html
import time
import traceback

import streamlit as st

try:
    from miniproject import analyze_job, analyze_resume_file
    BACKEND_READY = True
except ImportError:
    try:  # fallback for the older module name
        from resume_analyzer import analyze_job, analyze_resume_file
        BACKEND_READY = True
    except ImportError:
        BACKEND_READY = False


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = ["Dashboard", "Resume Screening", "Candidates", "Job Description", "Settings"]


# =========================================================
# STYLES
# =========================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root{
  --bg:#0b1120; --panel:rgba(255,255,255,.04); --panel-2:rgba(255,255,255,.07);
  --border:rgba(148,163,184,.16); --text:#e6eaf6; --muted:#94a3b8;
  --accent:#6366f1; --accent-2:#3b82f6;
  --strong:#34d399; --good:#60a5fa; --mid:#fbbf24; --low:#f87171;
}
html, body, .stApp, [class*="css"]{font-family:'Inter',system-ui,sans-serif;}
.stApp{
  background:
    radial-gradient(1100px 520px at 88% -8%, rgba(99,102,241,.18), transparent 60%),
    radial-gradient(900px 480px at -8% 8%, rgba(59,130,246,.11), transparent 55%),
    var(--bg);
  color:var(--text);
}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu, footer{visibility:hidden;}
.block-container{padding-top:2rem; padding-bottom:3rem; max-width:1240px;}
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3{color:var(--text);}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"]{background:rgba(10,15,30,.96); border-right:1px solid var(--border);}
section[data-testid="stSidebar"] .block-container{padding-top:1.4rem;}
.brand{display:flex; align-items:center; gap:.7rem; margin-bottom:1.4rem;}
.brand-logo{width:36px; height:36px; border-radius:10px; display:grid; place-items:center; color:#fff;
  background:linear-gradient(135deg,var(--accent),var(--accent-2)); box-shadow:0 6px 18px rgba(99,102,241,.4);}
.brand-name{font-weight:600; font-size:.98rem; line-height:1.15;}
.brand-sub{font-size:.72rem; color:var(--muted);}
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:.2rem;}
section[data-testid="stSidebar"] div[role="radiogroup"] label{
  padding:.55rem .8rem; border-radius:10px; width:100%; border:1px solid transparent; cursor:pointer;}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child{display:none;}
section[data-testid="stSidebar"] div[role="radiogroup"] label p{color:var(--muted); font-size:.9rem; font-weight:500;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:var(--panel);}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
  background:rgba(99,102,241,.16); border-color:rgba(129,140,248,.35);}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p{color:#fff;}
.sys-card{background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:.9rem 1rem; margin-top:1.4rem;}
.sys-row{display:flex; justify-content:space-between; align-items:center; font-size:.82rem; padding:.2rem 0;}
.sys-row span:first-child{color:var(--muted);}
.sidebar-foot{margin-top:2rem; font-size:.74rem; color:var(--muted); text-align:center;}

/* ---------- header ---------- */
.topbar{display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap; margin-bottom:1.6rem;}
.topbar h1{font-size:1.75rem; font-weight:700; letter-spacing:-.02em; margin:0; padding:0;}
.topbar p{margin:.2rem 0 0; color:var(--muted); font-size:.95rem;}
.pill{display:inline-flex; align-items:center; gap:.45rem; padding:.38rem .8rem; border-radius:999px; font-size:.8rem;
  background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.3); color:#6ee7b7;}
.dot{width:7px; height:7px; border-radius:50%; background:var(--strong); display:inline-block;}
.dot.warn{background:var(--low);}

/* ---------- cards ---------- */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--panel); border:1px solid var(--border) !important; border-radius:18px;
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 10px 30px rgba(0,0,0,.22);}
.card-title{font-size:1.1rem; font-weight:600; margin:0;}
.card-sub{color:var(--muted); font-size:.88rem; margin:.15rem 0 1rem;}
.sec{margin:2rem 0 .9rem;}
.sec h3{font-size:1.15rem; font-weight:600; margin:0; padding:0; letter-spacing:-.01em;}
.sec p{margin:.15rem 0 0; color:var(--muted); font-size:.86rem;}

/* ---------- KPI ---------- */
.kpi{background:var(--panel); border:1px solid var(--border); border-radius:16px; padding:1.1rem 1.2rem;
  backdrop-filter:blur(14px); box-shadow:0 10px 30px rgba(0,0,0,.2); height:100%;}
.kpi-top{display:flex; justify-content:space-between; align-items:center; color:var(--muted); font-size:.8rem; font-weight:500;}
.kpi-icon{width:32px; height:32px; border-radius:9px; display:grid; place-items:center; color:#a5b4fc; background:rgba(99,102,241,.14);}
.kpi-value{font-size:1.85rem; font-weight:700; letter-spacing:-.02em; margin:.7rem 0 .25rem;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.kpi-sub{font-size:.8rem; color:var(--muted);}
.kpi-sub b{font-weight:600;}
.t-strong{color:var(--strong);} .t-good{color:var(--good);} .t-mid{color:var(--mid);} .t-low{color:var(--low);}

/* ---------- badges / chips ---------- */
.badge{display:inline-block; padding:.2rem .6rem; border-radius:999px; font-size:.75rem; font-weight:600; white-space:nowrap;}
.badge.strong{background:rgba(52,211,153,.13); color:#6ee7b7;}
.badge.good{background:rgba(96,165,250,.13); color:#93c5fd;}
.badge.mid{background:rgba(251,191,36,.13); color:#fcd34d;}
.badge.low{background:rgba(248,113,113,.13); color:#fca5a5;}
.chips{display:flex; flex-wrap:wrap; gap:.4rem; margin-top:.4rem;}
.chip{padding:.22rem .6rem; border-radius:8px; font-size:.78rem; background:var(--panel-2); border:1px solid var(--border); color:#cbd5e1;}
.chip.ok{background:rgba(52,211,153,.09); border-color:rgba(52,211,153,.25); color:#a7f3d0;}
.chip.miss{background:rgba(248,113,113,.09); border-color:rgba(248,113,113,.25); color:#fecaca;}
.lbl{font-size:.78rem; color:var(--muted); font-weight:500; margin-top:.9rem;}

/* ---------- table ---------- */
.tbl-wrap{overflow-x:auto; border:1px solid var(--border); border-radius:16px; background:var(--panel); backdrop-filter:blur(14px);}
.tbl{width:100%; border-collapse:collapse; min-width:680px;}
.tbl th{text-align:left; font-size:.78rem; font-weight:500; color:var(--muted); padding:.8rem 1rem; border-bottom:1px solid var(--border);}
.tbl td{padding:.85rem 1rem; font-size:.9rem; border-bottom:1px solid rgba(148,163,184,.08); vertical-align:middle;}
.tbl tr:last-child td{border-bottom:none;}
.tbl tbody tr:hover td{background:rgba(255,255,255,.025);}
.rank{width:26px; height:26px; border-radius:8px; display:inline-grid; place-items:center; font-size:.8rem; font-weight:600; background:var(--panel-2);}
.cand-name{font-weight:600;} .cand-file{font-size:.76rem; color:var(--muted);}
.bar-row{display:flex; align-items:center; gap:.6rem; min-width:150px;}
.bar{flex:1; height:6px; border-radius:99px; background:rgba(148,163,184,.15); overflow:hidden;}
.bar > i{display:block; height:100%; border-radius:99px; background:linear-gradient(90deg,var(--accent),var(--accent-2));}
.bar > i.strong{background:var(--strong);} .bar > i.good{background:var(--good);}
.bar > i.mid{background:var(--mid);} .bar > i.low{background:var(--low);}
.bar-val{font-weight:600; font-size:.88rem; min-width:48px; text-align:right;}

/* ---------- candidate card ---------- */
.cc{background:var(--panel); border:1px solid var(--border); border-radius:18px; padding:1.3rem 1.4rem; margin-bottom:1rem;
  backdrop-filter:blur(14px); box-shadow:0 10px 30px rgba(0,0,0,.22);}
.cc.attn{border-left:3px solid var(--low);}
.cc-head{display:flex; justify-content:space-between; align-items:center; gap:1rem;}
.cc-name{font-size:1.2rem; font-weight:600; letter-spacing:-.01em; margin:.35rem 0 .1rem;}
.cc-rank{font-size:.78rem; color:#a5b4fc; font-weight:600;}
.verdict{margin-top:1rem; padding:.8rem 1rem; border-radius:12px; font-size:.9rem; line-height:1.55; color:#dbe2f2;
  background:rgba(99,102,241,.08); border:1px solid rgba(129,140,248,.2);}
.ring{--c:#60a5fa; --p:0; width:84px; height:84px; border-radius:50%; display:grid; place-items:center; position:relative; flex-shrink:0;
  background:conic-gradient(var(--c) calc(var(--p) * 1%), rgba(148,163,184,.16) 0);}
.ring::before{content:""; position:absolute; inset:7px; border-radius:50%; background:#10172b;}
.ring span{position:relative; font-weight:700; font-size:1.05rem;}
.ring.strong{--c:#34d399;} .ring.good{--c:#60a5fa;} .ring.mid{--c:#fbbf24;} .ring.low{--c:#f87171;}

/* ---------- detail ---------- */
.info-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:.8rem;}
.info{background:var(--panel-2); border:1px solid var(--border); border-radius:12px; padding:.7rem .9rem;}
.info small{display:block; color:var(--muted); font-size:.74rem; margin-bottom:.15rem;}
.info b{font-weight:600; font-size:.92rem; word-break:break-word;}
.item{padding:.7rem 0; border-bottom:1px solid rgba(148,163,184,.1);}
.item:last-child{border-bottom:none;}
.item b{font-weight:600;} .item .muted, .muted{color:var(--muted); font-size:.84rem;}

/* ---------- empty / error ---------- */
.empty{text-align:center; padding:3.2rem 1rem 2rem;}
.empty-icon{width:84px; height:84px; margin:0 auto 1.4rem; border-radius:24px; display:grid; place-items:center; color:#a5b4fc;
  background:linear-gradient(135deg,rgba(99,102,241,.2),rgba(59,130,246,.1)); border:1px solid rgba(129,140,248,.3);}
.empty h2{font-size:1.5rem; font-weight:700; margin:0 0 .4rem; letter-spacing:-.01em;}
.empty p{color:var(--muted); max-width:420px; margin:0 auto;}
.err{background:rgba(248,113,113,.08); border:1px solid rgba(248,113,113,.28); border-radius:12px; padding:.8rem 1rem; margin:.6rem 0 .3rem;}
.err b{color:#fecaca;} .err span{display:block; color:#cbd5e1; font-size:.86rem; margin-top:.15rem;}
.filerow{display:flex; justify-content:space-between; gap:1rem; padding:.55rem .8rem; border-radius:10px; font-size:.88rem;
  background:var(--panel-2); border:1px solid var(--border); margin-bottom:.4rem;}
.filerow .n{font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
.filerow .m{color:var(--muted); font-size:.8rem; white-space:nowrap;}
.count{display:inline-block; padding:.2rem .65rem; border-radius:999px; font-size:.78rem; font-weight:600;
  background:rgba(99,102,241,.16); color:#c7d2fe; margin-bottom:.6rem;}
.foot{text-align:center; color:var(--muted); font-size:.78rem; margin-top:3rem; padding-top:1.2rem; border-top:1px solid var(--border);}

/* ---------- streamlit widgets ---------- */
[data-testid="stFileUploaderDropzone"]{
  background:rgba(99,102,241,.06); border:1.5px dashed rgba(129,140,248,.45); border-radius:14px; padding:1.6rem;}
[data-testid="stFileUploaderDropzone"] *{color:var(--muted) !important;}
[data-testid="stFileUploaderDropzone"] button{border:1px solid var(--border); background:var(--panel-2); color:var(--text) !important;}
[data-testid="stFileUploaderDropzone"] button *{color:var(--text) !important;}
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"]{display:none;}
[data-testid="stFileUploader"] section + div{display:none;}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,var(--accent),var(--accent-2)); border:none; color:#fff; font-weight:600;
  border-radius:12px; padding:.7rem 1rem; box-shadow:0 8px 22px rgba(99,102,241,.35);}
.stButton > button[kind="primary"]:hover{filter:brightness(1.08);}
.stButton > button[kind="primary"]:disabled{opacity:.45; box-shadow:none;}
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"]{
  background:var(--panel-2); border:1px solid var(--border); color:var(--text); border-radius:12px;}
div[data-baseweb="select"] > div{background:var(--panel-2); border-color:var(--border); color:var(--text);}
div[data-baseweb="select"] *{color:var(--text);}
div[data-testid="stExpander"]{background:var(--panel); border:1px solid var(--border); border-radius:14px;}
div[data-testid="stExpander"] summary p{color:var(--text); font-weight:500;}
div[data-testid="stProgress"] > div > div{background:rgba(148,163,184,.15);}
div[data-testid="stProgress"] > div > div > div{background:linear-gradient(90deg,var(--accent),var(--accent-2));}
[data-testid="stNumberInput"] input{background:var(--panel-2); color:var(--text);}

@media (max-width: 760px){
  .block-container{padding-left:1rem; padding-right:1rem;}
  .topbar h1{font-size:1.4rem;}
  .kpi-value{font-size:1.5rem;}
  .cc{padding:1rem;}
}
</style>
"""


# =========================================================
# SMALL HELPERS
# =========================================================
ICONS = {
    "file": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    "upload": '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/>',
}


def icon(name, size=18):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'
    )


def esc(value):
    return _html.escape(str(value))


def flat(markup):
    """Collapse indented HTML so Markdown never treats it as a code block."""
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())


def h(markup):
    st.markdown(flat(markup), unsafe_allow_html=True)


def to_dict(obj):
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    return dict(vars(obj)) if hasattr(obj, "__dict__") else {}


def pick(data, *keys):
    """First non-empty value among several possible key names."""
    for key in keys:
        value = data.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value if str(v).strip()]
    if isinstance(value, dict):
        return [f"{k}: {v}" for k, v in value.items()]
    text = str(value)
    return [p.strip() for p in text.split(",") if p.strip()] if "," in text else [text]


def band(score):
    if score >= 80:
        return "Strong Match", "strong"
    if score >= 60:
        return "Good Match", "good"
    if score >= 40:
        return "Moderate Match", "mid"
    return "Low Match", "low"


def fmt_size(num_bytes):
    if not num_bytes:
        return ""
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.0f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def fmt_experience(value):
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Met" if value else "Not met"
    text = str(value)
    return text if len(text) <= 28 else text[:27] + "…"


def chips(items, kind="", limit=14):
    items = as_list(items)
    if not items:
        return '<span class="muted">None listed</span>'
    shown = "".join(f'<span class="chip {kind}">{esc(i)}</span>' for i in items[:limit])
    if len(items) > limit:
        shown += f'<span class="chip">+{len(items) - limit} more</span>'
    return f'<div class="chips">{shown}</div>'


def section(title, subtitle=""):
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    h(f'<div class="sec"><h3>{esc(title)}</h3>{sub}</div>')


def go_to(page):
    st.session_state["nav_target"] = page
    st.rerun()


def friendly_hint(filename, exc):
    msg = str(exc).lower()
    if "rate" in msg or "429" in msg:
        return "The AI service is rate-limiting requests. Wait a moment and try again."
    if "api key" in msg or "api_key" in msg or "auth" in msg or "401" in msg:
        return "Check that your Groq API key is set correctly."
    if filename.lower().endswith(".pdf") or "pdf" in msg:
        return "Please make sure the PDF contains selectable text."
    return "Try uploading the file again or use a different format."


# =========================================================
# STATE
# =========================================================
def init_state():
    st.session_state.setdefault("results", [])
    st.session_state.setdefault("errors", [])
    st.session_state.setdefault("job", None)
    st.session_state.setdefault("uploader_key", 0)
    st.session_state.setdefault("delay", 2)
    st.session_state.setdefault("nav", "Dashboard")


# =========================================================
# LAYOUT: SIDEBAR / HEADER / FOOTER
# =========================================================
def render_sidebar():
    with st.sidebar:
        h(f"""
        <div class="brand">
          <div class="brand-logo">{icon("target", 20)}</div>
          <div><div class="brand-name">AI Resume Screening</div><div class="brand-sub">Recruitment Platform</div></div>
        </div>
        """)

        if "nav_target" in st.session_state:
            st.session_state["nav"] = st.session_state.pop("nav_target")
        page = st.radio("Navigation", PAGES, key="nav", label_visibility="collapsed")

        backend = ("Ready", "") if BACKEND_READY else ("Unavailable", "warn")
        h(f"""
        <div class="sys-card">
          <div class="sys-row"><span>AI Engine</span><span><i class="dot {backend[1]}"></i> {"Connected" if BACKEND_READY else "Offline"}</span></div>
          <div class="sys-row"><span>Backend</span><span><i class="dot {backend[1]}"></i> {backend[0]}</span></div>
        </div>
        <div class="sidebar-foot">Powered by Groq AI</div>
        """)
    return page


def render_header():
    h("""
    <div class="topbar">
      <div>
        <h1>AI Resume Screening</h1>
        <p>Intelligent candidate matching powered by AI</p>
      </div>
      <span class="pill"><i class="dot"></i> AI Engine Ready</span>
    </div>
    """)


def render_footer():
    h('<div class="foot">AI Resume Screening System • Intelligent Candidate Analysis</div>')


# =========================================================
# COMPONENTS
# =========================================================
def kpi_card(label, value, sub, icon_name, tone=""):
    h(f"""
    <div class="kpi">
      <div class="kpi-top"><span>{esc(label)}</span><span class="kpi-icon">{icon(icon_name, 16)}</span></div>
      <div class="kpi-value">{esc(value)}</div>
      <div class="kpi-sub {tone}">{sub}</div>
    </div>
    """)


def render_kpis():
    results = st.session_state["results"]
    failed = len(st.session_state["errors"])
    cols = st.columns(4)

    if not results:
        with cols[0]:
            kpi_card("Resumes analyzed", "—", "Awaiting analysis", "file")
        with cols[1]:
            kpi_card("Best match", "—", "Awaiting analysis", "target")
        with cols[2]:
            kpi_card("Average score", "—", "Awaiting analysis", "chart")
        with cols[3]:
            kpi_card("Top candidate", "—", "Awaiting analysis", "user")
        return

    best = results[0]
    average = sum(r["score"] for r in results) / len(results)
    best_band, best_tone = band(best["score"])
    avg_band, avg_tone = band(average)

    with cols[0]:
        sub = f"{failed} could not be processed" if failed else "All resumes processed"
        kpi_card("Resumes analyzed", len(results), sub, "file")
    with cols[1]:
        kpi_card("Best match", f"{best['score']:.1f}%", f"<b>{best_band}</b>", "target", f"t-{best_tone}")
    with cols[2]:
        kpi_card("Average score", f"{average:.1f}%", f"<b>{avg_band}</b>", "chart", f"t-{avg_tone}")
    with cols[3]:
        kpi_card("Top candidate", best["name"], f"{best['score']:.1f}% match", "user")


def render_errors():
    for err in st.session_state["errors"]:
        h(f'<div class="err"><b>{esc(err["title"])}</b><span>{esc(err["file"])} — {esc(err["hint"])}</span></div>')
        with st.expander(f"Technical Details • {err['file']}"):
            st.code(err["trace"], language="text")


def render_empty_state(show_button=True):
    h(f"""
    <div class="empty">
      <div class="empty-icon">{icon("upload", 34)}</div>
      <h2>Ready to screen candidates?</h2>
      <p>Upload resumes to begin AI-powered candidate matching.</p>
    </div>
    """)
    if show_button:
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            if st.button("Upload resumes", type="primary", use_container_width=True):
                go_to("Resume Screening")


def render_ranking_table(results):
    rows = ""
    for i, r in enumerate(results, start=1):
        label, tone = band(r["score"])
        d = r["details"]
        matching = as_list(pick(d, "matching_skills", "matching skills", "matched_skills"))
        missing = as_list(pick(d, "missing_important_skills", "missing skills", "missing_skills"))
        total = len(matching) + len(missing)
        if total:
            pct = len(matching) / total * 100
            skills = (
                f'<div class="bar-row"><div class="bar"><i style="width:{pct:.0f}%"></i></div>'
                f'<span class="muted">{len(matching)}/{total}</span></div>'
            )
        else:
            skills = '<span class="muted">—</span>'
        exp = fmt_experience(pick(d, "experience_requirement_met", "experience requirement"))
        width = min(max(r["score"], 0), 100)
        rows += f"""
        <tr>
          <td><span class="rank">{i}</span></td>
          <td><div class="cand-name">{esc(r["name"])}</div><div class="cand-file">{esc(r["file"])}</div></td>
          <td><div class="bar-row"><div class="bar"><i class="{tone}" style="width:{width:.0f}%"></i></div>
              <span class="bar-val">{r["score"]:.1f}%</span></div></td>
          <td>{esc(exp)}</td>
          <td>{skills}</td>
          <td><span class="badge {tone}">{label}</span></td>
        </tr>"""
    h(f"""
    <div class="tbl-wrap"><table class="tbl">
      <thead><tr><th>Rank</th><th>Candidate</th><th>Match Score</th><th>Experience</th><th>Skills Match</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    """)


def render_candidate_card(candidate, rank=None, attention=False):
    d = candidate["details"]
    label, tone = band(candidate["score"])
    matching = pick(d, "matching_skills", "matching skills", "matched_skills")
    missing = pick(d, "missing_important_skills", "missing skills", "missing_skills")
    experience = pick(d, "experience_requirement_met", "experience requirement")
    verdict = pick(d, "final_verdict", "verdict")
    pct = min(max(candidate["score"], 0), 100)

    rank_html = f'<div class="cc-rank">Rank #{rank}</div>' if rank else '<div class="cc-rank">Needs review</div>'
    exp_html = (
        f'<div class="lbl">Experience requirement</div><div style="margin-top:.2rem">{esc(experience)}</div>'
        if experience is not None else ""
    )
    verdict_html = f'<div class="verdict">{esc(verdict)}</div>' if verdict else ""

    h(f"""
    <div class="cc {"attn" if attention else ""}">
      <div class="cc-head">
        <div>
          {rank_html}
          <div class="cc-name">{esc(candidate["name"])}</div>
          <div class="muted">{esc(candidate["file"])}</div>
          <div style="margin-top:.5rem"><span class="badge {tone}">{label}</span></div>
        </div>
        <div class="ring {tone}" style="--p:{pct:.0f}"><span>{candidate["score"]:.0f}%</span></div>
      </div>
      <div class="lbl">Matching skills</div>{chips(matching, "ok")}
      <div class="lbl">Missing skills</div>{chips(missing, "miss")}
      {exp_html}
      {verdict_html}
    </div>
    """)


def render_items(value):
    """Render a list of strings / dicts (education, projects, certifications)."""
    items = value if isinstance(value, (list, tuple)) else ([value] if value else [])
    if not items:
        h('<span class="muted">Not found in resume</span>')
        return
    out = ""
    for item in items:
        if isinstance(item, dict):
            values = [(k, v) for k, v in item.items() if v not in (None, "", [])]
            if not values:
                continue
            title = esc(values[0][1])
            rest = "<br>".join(
                f'{esc(k.replace("_", " ").title())}: {esc(", ".join(map(str, v)) if isinstance(v, list) else v)}'
                for k, v in values[1:]
            )
            out += f'<div class="item"><b>{title}</b><div class="muted">{rest}</div></div>'
        else:
            out += f'<div class="item">{esc(item)}</div>'
    h(out or '<span class="muted">Not found in resume</span>')


def render_experience(items):
    if not items:
        h('<span class="muted">Not found in resume</span>')
        return
    out = ""
    for item in items if isinstance(items, list) else [items]:
        e = to_dict(item) if not isinstance(item, str) else {}
        if not e:
            out += f'<div class="item">{esc(item)}</div>'
            continue
        role = pick(e, "role", "title", "position") or "—"
        company = pick(e, "company", "organization", "employer") or ""
        duration = pick(e, "duration", "period", "dates") or ""
        used = pick(e, "skills_used", "skills", "technologies")
        out += (
            f'<div class="item"><b>{esc(role)}</b>'
            f'{" at " + esc(company) if company else ""}'
            f'<div class="muted">{esc(duration)}</div>{chips(used) if used else ""}</div>'
        )
    h(out)


def render_candidate_detail(candidate):
    resume = candidate["resume"]
    d = candidate["details"]
    label, tone = band(candidate["score"])

    exp_value = pick(resume, "total_experience", "years_of_experience", "total_years_experience", "experience_years")
    if exp_value is None and isinstance(resume.get("experience"), list) and resume["experience"]:
        exp_value = f"{len(resume['experience'])} role(s)"

    with st.container(border=True):
        h(f'<p class="card-title">{esc(candidate["name"])}</p><p class="card-sub">{esc(candidate["file"])}</p>')

        with st.expander("Candidate information", expanded=True):
            cells = [
                ("Name", candidate["name"]),
                ("Email", pick(resume, "email")),
                ("Phone", pick(resume, "phone", "phone_number")),
                ("Experience", exp_value),
            ]
            h('<div class="info-grid">' + "".join(
                f"<div class='info'><small>{k}</small><b>{esc(v) if v else '—'}</b></div>" for k, v in cells
            ) + "</div>")

        with st.expander("AI evaluation", expanded=True):
            matching = pick(d, "matching_skills", "matching skills", "matched_skills")
            missing = pick(d, "missing_important_skills", "missing skills", "missing_skills")
            experience = pick(d, "experience_requirement_met", "experience requirement")
            verdict = pick(d, "final_verdict", "verdict")
            h(f"""
            <div class="cc-head">
              <div><div class="lbl" style="margin-top:0">Match score</div>
              <div class="cc-name">{candidate["score"]:.1f}%</div><span class="badge {tone}">{label}</span></div>
              <div class="ring {tone}" style="--p:{min(max(candidate['score'], 0), 100):.0f}"><span>{candidate["score"]:.0f}%</span></div>
            </div>
            <div class="lbl">Matching skills</div>{chips(matching, "ok")}
            <div class="lbl">Missing skills</div>{chips(missing, "miss")}
            {f'<div class="lbl">Experience requirement</div><div style="margin-top:.2rem">{esc(experience)}</div>' if experience is not None else ""}
            {f'<div class="verdict">{esc(verdict)}</div>' if verdict else ""}
            """)
            with st.expander("Full analysis (JSON)"):
                st.json(d)

        with st.expander("Skills detected"):
            skills = pick(resume, "skills")
            h(chips(skills) if skills else '<span class="muted">Not found in resume</span>')
        with st.expander("Work experience"):
            render_experience(resume.get("experience"))
        with st.expander("Education"):
            render_items(resume.get("education"))
        with st.expander("Projects"):
            render_items(resume.get("projects"))
        with st.expander("Certifications"):
            render_items(resume.get("certifications"))


def render_charts(results):
    if len(results) < 2:
        return
    section("Insights", "Based on the candidates analyzed in this session")
    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            h('<p class="card-title">Top candidates comparison</p><p class="card-sub">Match score by candidate</p>')
            rows = ""
            for r in results[:6]:
                _, tone = band(r["score"])
                rows += (
                    f'<div style="margin-bottom:.8rem"><div style="display:flex;justify-content:space-between;font-size:.84rem;'
                    f'margin-bottom:.3rem"><span>{esc(r["name"])}</span><b>{r["score"]:.1f}%</b></div>'
                    f'<div class="bar"><i class="{tone}" style="width:{min(max(r["score"], 0), 100):.0f}%"></i></div></div>'
                )
            h(rows)

    with right:
        with st.container(border=True):
            h('<p class="card-title">Score distribution</p><p class="card-sub">Candidates per match band</p>')
            counts = {"Strong Match": 0, "Good Match": 0, "Moderate Match": 0, "Low Match": 0}
            tones = {}
            for r in results:
                label, tone = band(r["score"])
                counts[label] += 1
                tones[label] = tone
            rows = ""
            for label, tone in [("Strong Match", "strong"), ("Good Match", "good"), ("Moderate Match", "mid"), ("Low Match", "low")]:
                width = counts[label] / len(results) * 100
                rows += (
                    f'<div style="margin-bottom:.8rem"><div style="display:flex;justify-content:space-between;font-size:.84rem;'
                    f'margin-bottom:.3rem"><span>{label}</span><b>{counts[label]}</b></div>'
                    f'<div class="bar"><i class="{tone}" style="width:{width:.0f}%"></i></div></div>'
                )
            h(rows)


# =========================================================
# ANALYSIS
# =========================================================
def run_analysis(files):
    st.session_state["errors"] = []
    results = []
    total = len(files)
    progress = st.progress(0.0)
    status = st.empty()

    try:
        status.markdown(flat('<span class="muted">Analyzing job description…</span>'), unsafe_allow_html=True)
        job = analyze_job()
        st.session_state["job"] = job
    except Exception as exc:
        st.session_state["errors"].append({
            "file": "Job description",
            "title": "Unable to analyze the job description.",
            "hint": friendly_hint("", exc),
            "trace": traceback.format_exc(),
        })
        progress.empty()
        status.empty()
        return False

    for index, uploaded_file in enumerate(files):
        status.markdown(
            flat(f'<span class="muted">Processing <b>{esc(uploaded_file.name)}</b> ({index + 1} of {total})</span>'),
            unsafe_allow_html=True,
        )
        try:
            parsed_resume, result = analyze_resume_file(uploaded_file, job)
            resume = to_dict(parsed_resume)
            results.append({
                "name": resume.get("name") or getattr(parsed_resume, "name", None) or uploaded_file.name,
                "file": uploaded_file.name,
                "size": getattr(uploaded_file, "size", None),
                "score": float(result.score),
                "details": to_dict(result.details),
                "resume": resume,
            })
        except Exception as exc:
            st.session_state["errors"].append({
                "file": uploaded_file.name,
                "title": "Unable to process this resume.",
                "hint": friendly_hint(uploaded_file.name, exc),
                "trace": traceback.format_exc(),
            })

        progress.progress((index + 1) / total)

        # Helps avoid Groq rate-limit issues.
        if index < total - 1:
            time.sleep(st.session_state["delay"])

    results.sort(key=lambda c: c["score"], reverse=True)
    st.session_state["results"] = results
    status.empty()
    progress.empty()
    return bool(results)


# =========================================================
# PAGES
# =========================================================
def page_dashboard():
    render_kpis()
    render_errors()
    results = st.session_state["results"]

    if not results:
        with st.container(border=True):
            render_empty_state()
        return

    section("Candidate ranking", "Sorted by match score")
    render_ranking_table(results)
    render_charts(results)


def page_screening():
    with st.container(border=True):
        h(f"""
        <p class="card-title">Upload Candidate Resumes</p>
        <p class="card-sub">Upload PDF or DOCX resumes for AI-powered screening</p>
        """)

        files = st.file_uploader(
            "Resumes",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"uploader_{st.session_state['uploader_key']}",
        )

        if files:
            h(f'<span class="count">{len(files)} file{"s" if len(files) != 1 else ""} selected</span>')
            rows = "".join(
                f'<div class="filerow"><span class="n">{esc(f.name)}</span>'
                f'<span class="m">{esc(f.name.rsplit(".", 1)[-1].upper())} • {fmt_size(getattr(f, "size", 0))}</span></div>'
                for f in files
            )
            h(rows)

        btn_col, clear_col = st.columns([4, 1])
        with btn_col:
            analyze = st.button("Analyze Candidates", type="primary", use_container_width=True, disabled=not files)
        with clear_col:
            if st.button("Clear files", use_container_width=True, disabled=not files):
                st.session_state["uploader_key"] += 1
                st.rerun()

        if not files:
            h('<p class="muted" style="margin-top:.6rem">Select at least one resume to start the analysis.</p>')

    if analyze and files:
        with st.container(border=True):
            ok = run_analysis(files)
        if ok:
            go_to("Candidates")

    render_errors()


def page_candidates():
    results = st.session_state["results"]
    render_errors()

    if not results:
        with st.container(border=True):
            render_empty_state()
        return

    section("Top Candidates", "Best matches for this role")
    cols = st.columns(2 if len(results) > 1 else 1)
    for i, candidate in enumerate(results[:2]):
        with cols[i]:
            render_candidate_card(candidate, rank=i + 1)

    lowest = results[2:][-2:][::-1]
    if lowest:
        section("Candidates Requiring Attention", "Lowest matches against the job requirements")
        cols = st.columns(len(lowest))
        for i, candidate in enumerate(lowest):
            with cols[i]:
                render_candidate_card(candidate, attention=True)

    section("Candidate Profile", "Select a candidate to see the full breakdown")
    labels = [f"{i + 1}. {r['name']}  ({r['score']:.1f}%)" for i, r in enumerate(results)]
    choice = st.selectbox("Candidate", labels, label_visibility="collapsed")
    render_candidate_detail(results[labels.index(choice)])


def page_job():
    job = st.session_state["job"]

    if job is None:
        with st.container(border=True):
            h("""
            <p class="card-title">Job Description</p>
            <p class="card-sub">The job description is analyzed when you screen candidates. You can also load it now.</p>
            """)
            if st.button("Load job description", type="primary"):
                try:
                    with st.spinner("Analyzing job description…"):
                        st.session_state["job"] = analyze_job()
                    st.rerun()
                except Exception as exc:
                    st.session_state["errors"] = [{
                        "file": "Job description",
                        "title": "Unable to analyze the job description.",
                        "hint": friendly_hint("", exc),
                        "trace": traceback.format_exc(),
                    }]
                    render_errors()
        return

    data = to_dict(job)
    fields = [
        ("Role", pick(data, "role", "job_title", "title"), False),
        ("Minimum experience", pick(data, "minimum_experience", "min_experience", "experience_required", "years_of_experience", "experience"), False),
        ("Education", pick(data, "education", "education_requirements"), False),
        ("Required skills", pick(data, "required_skills", "must_have_skills", "skills"), True),
        ("Preferred skills", pick(data, "preferred_skills", "nice_to_have_skills"), True),
        ("Responsibilities", pick(data, "responsibilities", "duties"), True),
    ]

    with st.container(border=True):
        h('<p class="card-title">Job Description</p><p class="card-sub">Requirements extracted for candidate matching</p>')
        for label, value, is_list in fields:
            if value is None:
                continue
            h(f'<div class="lbl" style="margin-top:.2rem">{label}</div>')
            if is_list and label != "Responsibilities":
                h(chips(value))
            elif is_list:
                h("".join(f'<div class="item">{esc(x)}</div>' for x in as_list(value)))
            else:
                h(f'<div style="margin:.15rem 0 .6rem">{esc(value)}</div>')

        raw = pick(data, "description", "job_description", "raw_text")
        if raw:
            with st.expander("Original description"):
                st.write(raw)
        with st.expander("Full job analysis (JSON)", expanded=not any(v for _, v, _ in fields)):
            st.json(data)


def page_settings():
    with st.container(border=True):
        h('<p class="card-title">Settings</p><p class="card-sub">Control how candidates are processed</p>')
        st.session_state["delay"] = st.number_input(
            "Delay between resumes (seconds)",
            min_value=0, max_value=30, value=int(st.session_state["delay"]),
            help="A short pause between files helps avoid Groq rate limits.",
        )
        if st.button("Clear all results", disabled=not st.session_state["results"]):
            st.session_state["results"] = []
            st.session_state["errors"] = []
            st.session_state["job"] = None
            st.rerun()


# =========================================================
# APP
# =========================================================
def main():
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()
    page = render_sidebar()
    render_header()

    if not BACKEND_READY:
        st.error("Backend not found. Make sure `miniproject.py` is in the same folder as this file.")
        st.stop()

    {
        "Dashboard": page_dashboard,
        "Resume Screening": page_screening,
        "Candidates": page_candidates,
        "Job Description": page_job,
        "Settings": page_settings,
    }[page]()

    render_footer()


main()
