"""Streamlit web interface for contract analysis application."""
import streamlit as st
import os, sys, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from analyzer import ContractAnalyzer
from report_generator import generate_report

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Lexis — Contract Analyzer", page_icon="⚖",
                   layout="wide", initial_sidebar_state="collapsed")

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("analysis", None), ("analyzer", None), ("last_file", None),
    ("negotiations", None), ("chat_messages", []), ("gen_neg", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── History helpers ───────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_to_history(filename, summary, risk):
    history = load_history()
    history.insert(0, {
        "filename": filename,
        "date": datetime.now().strftime("%d %b %Y"),
        "type": summary.get("tipus_contracte", "—"),
        "score": risk.get("puntuacio", 0),
        "rec": risk.get("recomanacio", "—"),
    })
    history = history[:20]  # keep last 20
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #0c0c0c; color: #e8e4dc; }

.block-container { padding: 3rem 3rem 4rem 3rem; max-width: 1300px; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] * { visibility: visible !important; display: block !important; opacity: 1 !important; }

/* Nav */
.nav { display:flex; justify-content:space-between; align-items:center;
       padding-bottom:2.5rem; border-bottom:1px solid #1e1e1e; margin-bottom:3.5rem; }
.nav-logo { font-family:'DM Serif Display',serif; font-size:1.4rem; color:#e8e4dc; letter-spacing:-0.5px; }
.nav-logo span { color:#9b8f7a; font-style:italic; }
.nav-tag { font-size:0.72rem; font-weight:500; letter-spacing:2px; text-transform:uppercase; color:#4a4a4a; }

/* Hero */
.hero { margin-bottom:4rem; }
.hero-eyebrow { font-size:0.72rem; font-weight:500; letter-spacing:3px; text-transform:uppercase;
                color:#4a4a4a; margin-bottom:1.5rem; }
.hero-title { font-family:'DM Serif Display',serif; font-size:clamp(2.6rem,5vw,4rem);
              font-weight:400; line-height:1.1; color:#e8e4dc; letter-spacing:-1px; margin-bottom:1.5rem; }
.hero-title em { color:#9b8f7a; font-style:italic; }
.hero-subtitle { font-size:1rem; font-weight:300; color:#5a5a5a; max-width:400px; line-height:1.7; }

/* Upload */
[data-testid="stFileUploaderDropzone"] { background:#0c0c0c !important; border:1px dashed #2a2a2a !important; border-radius:2px !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color:#9b8f7a !important; }
.upload-label { font-size:0.72rem; font-weight:500; letter-spacing:2px; text-transform:uppercase; color:#4a4a4a; margin-bottom:0.75rem; }

/* Dividers */
.section-divider { border:none; border-top:1px solid #1e1e1e; margin:3.5rem 0; }

/* Labels */
.section-label { font-size:0.82rem; font-weight:500; letter-spacing:2.5px;
                 text-transform:uppercase; color:#6a6a6a; margin-bottom:2rem; }

/* Score */
.score-block { padding:2rem 0; border-top:1px solid #1e1e1e; border-bottom:1px solid #1e1e1e; }
.score-number { font-family:'DM Serif Display',serif; font-size:5.5rem; line-height:1; font-weight:400; letter-spacing:-3px; }
.score-denom { font-size:1.4rem; color:#3a3a3a; }
.score-caption { font-size:0.72rem; letter-spacing:2px; text-transform:uppercase; color:#3a3a3a; margin-top:0.5rem; }

/* Verdict */
.verdict { font-family:'DM Serif Display',serif; font-size:1.8rem; font-weight:400;
           font-style:italic; margin-bottom:0.75rem; }
.verdict-just { font-size:0.88rem; font-weight:300; color:#5a5a5a; line-height:1.7; }

/* Info blocks */
.info-label { font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#6a6a6a; margin-bottom:0.4rem; }
.info-value { font-size:0.95rem; font-weight:400; color:#e8e4dc; line-height:1.5; }
.info-block { padding:1.5rem 0; border-bottom:1px solid #1e1e1e; }

/* Flags */
.flag { padding:1.75rem 0; border-bottom:1px solid #1e1e1e; }
.flag-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem; gap:1rem; }
.flag-name { font-size:0.95rem; font-weight:500; color:#e8e4dc; line-height:1.4; }
.flag-risk-high   { font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#c0a882; white-space:nowrap; }
.flag-risk-medium { font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#8a8a8a; white-space:nowrap; }
.flag-risk-low    { font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#5a5a5a; white-space:nowrap; }
.flag-desc { font-size:0.85rem; font-weight:300; color:#5a5a5a; line-height:1.65; margin-bottom:0.6rem; }
.flag-benchmark { font-size:0.82rem; color:#9b8f7a; line-height:1.5; margin-bottom:0.6rem;
                  padding-left:1rem; border-left:1px solid #2a2a2a; }
.flag-fragment { font-size:0.8rem; font-style:italic; color:#3a3a3a;
                 padding-left:1rem; border-left:1px solid #2a2a2a; line-height:1.6; }

/* Negotiation */
.neg-box { margin-top:1rem; padding:1rem 1.25rem; background:#0f0f0f;
           border:1px solid #1e1e1e; border-radius:2px; }
.neg-label { font-size:0.68rem; font-weight:500; letter-spacing:2px; text-transform:uppercase;
             color:#9b8f7a; margin-bottom:0.5rem; }
.neg-text { font-size:0.88rem; font-weight:300; color:#c8c4bc; line-height:1.7; }

/* Summary list */
.sum-item-lbl { font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#6a6a6a; margin-bottom:0.4rem; }
.sum-item-val { font-size:0.92rem; font-weight:400; color:#e8e4dc; line-height:1.55; }
.sum-item { padding:1.25rem 0; border-bottom:1px solid #1a1a1a; }

/* Chat */
.chat-msg-user { text-align:right; margin:0.75rem 0; }
.chat-msg-user p { display:inline-block; background:#1a1f2a; border:1px solid #2d3561; border-radius:2px;
                    padding:0.6rem 1rem; font-size:0.88rem; color:#e8e4dc; max-width:75%; text-align:left; }
.chat-msg-ai { text-align:left; margin:0.75rem 0; }
.chat-msg-ai p { display:inline-block; background:#111; border:1px solid #1e1e1e; border-radius:2px;
                  padding:0.6rem 1rem; font-size:0.88rem; color:#c8c4bc; line-height:1.65; max-width:85%; }

/* History sidebar */
.hist-item { padding:0.9rem 0; border-bottom:1px solid #1e1e1e; }
.hist-name { font-size:0.82rem; font-weight:500; color:#e8e4dc; margin-bottom:0.25rem;
             white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.hist-meta { font-size:0.72rem; color:#5a5a5a; }
.hist-score { font-size:0.72rem; font-weight:500; color:#9b8f7a; }

/* Progress */
.stProgress > div > div > div > div { background:#9b8f7a !important; }
.stProgress > div > div > div { background:#1a1a1a !important; }

/* Buttons */
.stButton > button { background:#0f0f0f; border:1px solid #2a2a2a; color:#9b8f7a;
    font-size:0.75rem; letter-spacing:1.5px; text-transform:uppercase;
    padding:0.5rem 1.25rem; border-radius:2px; font-family:'DM Sans',sans-serif; }
.stButton > button:hover { border-color:#9b8f7a; background:#111; }

/* Sidebar */
[data-testid="stSidebar"] { background:#080808; border-right:1px solid #1a1a1a; }
[data-testid="stSidebar"] .block-container { padding:2rem 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ── History (inline, after nav) ───────────────────────────────────────────────
history = load_history()


# ── Nav ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav">
    <div class="nav-logo">Lexis <span>AI</span></div>
    <div class="nav-tag">Contract Intelligence</div>
</div>
""", unsafe_allow_html=True)


# ── Hero + Upload ─────────────────────────────────────────────────────────────
col_hero, col_upload = st.columns([1, 1], gap="large")

with col_hero:
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Legal Document Analysis</div>
        <div class="hero-title">Review contracts<br>with <em>precision.</em></div>
        <div class="hero-subtitle">
            Risk detection, industry benchmarks, negotiation suggestions
            and contextual Q&A — for legal professionals and enterprises.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_upload:
    st.markdown('<div class="upload-label">Upload document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload a PDF contract", type=["pdf"],
                                label_visibility="collapsed")
    st.markdown("""
    <div style="margin-top:1.5rem;">
        <div style="font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;color:#2a2a2a;margin-bottom:0.5rem;">Supported format</div>
        <div style="font-size:0.82rem;color:#3a3a3a;font-weight:300;">PDF · Any language · Max 50 MB</div>
    </div>
    """, unsafe_allow_html=True)


# ── Analysis ──────────────────────────────────────────────────────────────────
if uploaded:
    # Run analysis only when a new file is uploaded
    if uploaded.name != st.session_state.last_file:
        tmp_path = os.path.join(os.path.dirname(__file__), "contracts", "_tmp_upload.pdf")
        with open(tmp_path, "wb") as f:
            f.write(uploaded.read())

        with st.spinner(""):
            progress = st.progress(0, text="Loading and indexing document...")
            analyzer = ContractAnalyzer(tmp_path)
            progress.progress(20, text="Detecting document language...")
            progress.progress(35, text="Generating executive summary...")
            summary = analyzer.executive_summary()
            progress.progress(60, text="Identifying risk clauses...")
            flags = analyzer.detect_red_flags()
            progress.progress(85, text="Calculating overall risk score...")
            risk = analyzer.risk_score()
            progress.progress(100, text="Analysis complete.")
            progress.empty()

        os.remove(tmp_path)

        st.session_state.analyzer   = analyzer
        st.session_state.last_file  = uploaded.name
        st.session_state.analysis   = {"summary": summary, "flags": flags, "risk": risk}
        st.session_state.negotiations = None
        st.session_state.chat_messages = []
        st.session_state.gen_neg    = False

        save_to_history(uploaded.name, summary, risk)

    # Pull from session state
    summary = st.session_state.analysis["summary"]
    flags   = st.session_state.analysis["flags"]
    risk    = st.session_state.analysis["risk"]
    analyzer = st.session_state.analyzer

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Action bar ────────────────────────────────────────────────────────────
    action_col, _, neg_col = st.columns([2, 1, 2])

    with action_col:
        if st.button("Export PDF report"):
            negs = st.session_state.negotiations or []
            pdf_buf = generate_report(
                uploaded.name, summary, flags, risk, negotiations=negs
            )
            st.download_button(
                label="Download report",
                data=pdf_buf,
                file_name=f"lexis_report_{uploaded.name.replace('.pdf','')}.pdf",
                mime="application/pdf",
            )

    with neg_col:
        if not st.session_state.negotiations:
            if st.button("Generate negotiation suggestions"):
                with st.spinner("Generating suggestions..."):
                    source_flags = flags if flags else analyzer.find_negotiable_clauses()
                    st.session_state.negotiations = analyzer.suggest_negotiations(source_flags)
                    if not flags:
                        st.session_state.analysis["flags"] = source_flags
                st.rerun()
        else:
            st.markdown('<div style="font-size:0.75rem;color:#9b8f7a;letter-spacing:1px;padding-top:0.5rem;">✓ Negotiation suggestions ready</div>',
                        unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Overview row ──────────────────────────────────────────────────────────
    c_score, c_verdict, c_info = st.columns([1, 2, 2], gap="large")

    score = risk.get("puntuacio", 0)
    score_color = "#c0a882" if score >= 7 else "#e8e4dc"

    with c_score:
        st.markdown(f"""
        <div class="section-label">Risk Score</div>
        <div class="score-block">
            <div class="score-number" style="color:{score_color};">{score}<span class="score-denom">/10</span></div>
            <div class="score-caption">Overall risk level</div>
        </div>
        """, unsafe_allow_html=True)

    with c_verdict:
        rec = risk.get("recomanacio", "").capitalize()
        st.markdown(f"""
        <div class="section-label">Recommendation</div>
        <div class="score-block">
            <div class="verdict">{rec}</div>
            <div class="verdict-just">{risk.get("justificacio", "")}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_info:
        tipus    = summary.get("tipus_contracte", "—").capitalize()
        durada   = summary.get("durada", "Not specified")
        parts    = " · ".join(summary.get("parts_involucrades", [])) or "—"
        st.markdown(f"""
        <div class="section-label">Contract Details</div>
        <div class="info-block"><div class="info-label">Type</div><div class="info-value">{tipus}</div></div>
        <div class="info-block"><div class="info-label">Duration</div><div class="info-value">{durada}</div></div>
        <div class="info-block"><div class="info-label">Parties</div><div class="info-value">{parts}</div></div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Risk clauses + Summary ────────────────────────────────────────────────
    c_flags, c_gap, c_summary = st.columns([5, 1, 3])

    with c_flags:
        st.markdown(f'<div class="section-label">Risk Clauses &nbsp;({len(flags)} found)</div>',
                    unsafe_allow_html=True)

        if not flags:
            st.markdown('<div class="flag"><div class="flag-desc">No risk clauses identified.</div></div>',
                        unsafe_allow_html=True)
        else:
            neg_map = {}
            if st.session_state.negotiations:
                for n in st.session_state.negotiations:
                    neg_map[n.get("titol", "")] = n.get("proposta", "")

            for flag in flags:
                risc = flag.get("risc", "low").lower()
                if "high" in risc or "alt" in risc:
                    rc, rl = "flag-risk-high",   "High risk"
                elif "med" in risc or "mitj" in risc:
                    rc, rl = "flag-risk-medium", "Medium risk"
                else:
                    rc, rl = "flag-risk-low",    "Low risk"

                fragment_html  = f'<div class="flag-fragment">"{flag["fragment"]}"</div>' if flag.get("fragment") else ""
                benchmark_html = f'<div class="flag-benchmark">{flag["benchmark"]}</div>'  if flag.get("benchmark") else ""
                suggestion     = neg_map.get(flag.get("titol", ""))
                neg_html = f"""
                <div class="neg-box">
                    <div class="neg-label">Suggested reformulation</div>
                    <div class="neg-text">{suggestion}</div>
                </div>""" if suggestion else ""

                st.markdown(f"""
                <div class="flag">
                    <div class="flag-header">
                        <div class="flag-name">{flag.get("titol","")}</div>
                        <div class="{rc}">{rl}</div>
                    </div>
                    <div class="flag-desc">{flag.get("descripcio","")}</div>
                    {benchmark_html}
                    {fragment_html}
                    {neg_html}
                </div>
                """, unsafe_allow_html=True)

    with c_summary:
        punts      = summary.get("punts_clau", [])
        obligacions = summary.get("obligacions_principals", [])

        if punts:
            st.markdown('<div class="section-label">Key Points</div>', unsafe_allow_html=True)
            for i, p in enumerate(punts):
                st.markdown(f"""
                <div class="sum-item">
                    <div class="sum-item-lbl">{str(i+1).zfill(2)}</div>
                    <div class="sum-item-val">{p}</div>
                </div>
                """, unsafe_allow_html=True)

        if obligacions:
            st.markdown('<div class="section-label" style="margin-top:2.5rem;">Main Obligations</div>',
                        unsafe_allow_html=True)
            for i, o in enumerate(obligacions):
                st.markdown(f"""
                <div class="sum-item">
                    <div class="sum-item-lbl">{str(i+1).zfill(2)}</div>
                    <div class="sum-item-val">{o}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── History ───────────────────────────────────────────────────────────────
    if history:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        with st.expander(f"Contract history  ({len(history)} analyzed)"):
            for h in history:
                score = h.get("score", 0)
                score_col = "#c0a882" if score >= 7 else "#8a8a8a" if score >= 4 else "#5a5a5a"
                st.markdown(f"""
                <div class="hist-item">
                    <div class="hist-name">{h.get("filename","—")}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
                        <span class="hist-meta">{h.get("date","")}</span>
                        <span class="hist-score" style="color:{score_col};">{score}/10 · {h.get("rec","")}</span>
                    </div>
                    <div class="hist-meta" style="margin-top:2px;">{h.get("type","")}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Chat ──────────────────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Ask the contract</div>', unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-msg-user"><p>{msg["content"]}</p></div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-msg-ai"><p>{msg["content"]}</p></div>',
                        unsafe_allow_html=True)

    question = st.chat_input("Ask anything about this contract...")
    if question:
        st.session_state.chat_messages.append({"role": "user", "content": question})
        with st.spinner(""):
            answer = analyzer.chat(question)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        st.rerun()

else:
    st.markdown("""
    <hr class="section-divider">
    <div style="padding:6rem 0;text-align:center;">
        <div style="font-size:0.82rem;letter-spacing:3px;text-transform:uppercase;color:#2a2a2a;">
            Awaiting document
        </div>
    </div>
    """, unsafe_allow_html=True)
