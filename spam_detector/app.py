"""
app.py
------
Streamlit UI for the AI Message Spam, Fake & Scam Detector.

This file contains ONLY presentation logic:
  - Render the page layout
  - Call business-logic modules (detector, advisor, history)
  - Display results and history

No detection logic, no keyword lists, and no file I/O beyond calling
HistoryManager belong here.

Run with:
    streamlit run app.py
"""

import streamlit as st

from detector import MessageDetector
from advisor import SafetyAdvisor
from history import HistoryManager
from exceptions import EmptyMessageError, MessageTooLongError

MAX_MESSAGE_LENGTH: int = 2000

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Message Safety Checker",
    page_icon="🔍",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🔍 Message Safety Checker")
st.markdown(
    """
    Paste any message below to check whether it looks like **spam**, a **fake/phishing message**,
    or a **scam**. This tool uses simple pattern-matching rules — results are indicative only
    and **not guaranteed to be fully accurate**. Always use your own judgement.
    """
)
st.divider()

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
message_input: str = st.text_area(
    label="Paste your message here",
    placeholder="e.g. Congratulations! You have been selected as a winner. Click here to claim your free gift...",
    height=160,
    max_chars=MAX_MESSAGE_LENGTH,
    help=f"Maximum {MAX_MESSAGE_LENGTH} characters.",
)

analyze_clicked: bool = st.button("🔎 Analyze Message", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
if analyze_clicked:
    # --- Input validation ---------------------------------------------------
    try:
        if not message_input or not message_input.strip():
            raise EmptyMessageError()
        if len(message_input) > MAX_MESSAGE_LENGTH:
            raise MessageTooLongError()
    except EmptyMessageError as exc:
        st.warning(f"⚠️ {exc}")
        st.stop()
    except MessageTooLongError as exc:
        st.warning(f"⚠️ {exc}")
        st.stop()

    # --- Run detection ------------------------------------------------------
    detector  = MessageDetector()
    advisor   = SafetyAdvisor()
    history   = HistoryManager()

    result = detector.analyze(message_input)
    result.advice = advisor.get_advice(result.message_type)

    try:
        history.add_entry(result)
    except OSError as exc:
        st.warning(f"⚠️ Could not save to history: {exc}")

    # --- Display result card ------------------------------------------------
    st.divider()
    st.subheader("📋 Analysis Result")

    # Risk-level colour coding
    risk_colour = {"Low": "normal", "Medium": "off", "High": "inverse"}
    risk_icon   = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

    col1, col2 = st.columns(2)
    col1.metric(
        label="Risk Level",
        value=f"{risk_icon.get(result.risk_level, '')} {result.risk_level}",
    )
    col2.metric(
        label="Message Type",
        value=result.message_type,
    )

    # Result banner
    if result.risk_level == "Low":
        st.success("✅ This message appears to be **safe**. No warning signs were detected.")
    elif result.risk_level == "Medium":
        st.warning("⚠️ This message has some **suspicious indicators**. Read carefully before acting.")
    else:
        st.error("🚨 This message shows **strong warning signs**. Do NOT act on it without verifying.")

    # Detected reasons
    if result.reasons:
        st.markdown("**🚩 Detected warning signs:**")
        for reason in result.reasons:
            st.markdown(f"- {reason}")
    else:
        st.markdown("*No warning signs were detected.*")

    # Safety advice
    if result.advice:
        st.info("**💡 Safety advice:**\n\n" + "\n\n".join(f"• {tip}" for tip in result.advice))

    st.caption(f"Analysed at {result.timestamp}")

# ---------------------------------------------------------------------------
# History section
# ---------------------------------------------------------------------------
st.divider()

col_hist, col_clear = st.columns([4, 1])
col_hist.subheader("📂 Previous Results")

history_manager = HistoryManager()
entries = history_manager.get_history()

if col_clear.button("🗑️ Clear History", use_container_width=True):
    try:
        history_manager.clear_history()
        st.success("History cleared.")
        st.rerun()
    except OSError as exc:
        st.warning(f"⚠️ Could not clear history: {exc}")

if not entries:
    st.info("No previous analyses yet. Analyse a message above to get started.")
else:
    risk_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
    for entry in entries:
        icon = risk_icon.get(entry.risk_level, "⚪")
        label = f"{icon} {entry.risk_level} — {entry.message_type}  |  {entry.timestamp}"
        with st.expander(label):
            st.markdown(f"**Message preview:** {entry.message_preview!r}")
            st.markdown(f"**Risk level:** {entry.risk_level}")
            st.markdown(f"**Message type:** {entry.message_type}")
            st.markdown(f"**Analysed at:** {entry.timestamp}")
