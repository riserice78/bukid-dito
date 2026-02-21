import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


# ── Google Sheets writer ──────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource
def get_sheet():
    spreadsheet_id = st.secrets["gsheets"]["spreadsheet_id"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet("feedback")
    # Write header row if sheet is empty
    if sheet.row_count == 0 or sheet.cell(1, 1).value is None:
        sheet.append_row([
            "timestamp", "rating", "what_worked", "what_to_improve",
            "recommend", "contact", "location", "mode"
        ])
    return sheet

def save_feedback(data: dict):
    sheet = get_sheet()
    sheet.append_row([
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        data["rating"],
        data["what_worked"],
        data["what_to_improve"],
        data["recommend"],
        data["contact"],
        data["location"] or "",
        data["mode"] or "",
    ])

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(page_title="Feedback – Taniman", page_icon="🌱")
st.markdown("""
    <style>
    div[data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)


# ── Language helper (reads from session state if user came from main) ─
def t(english: str, tagalog: str) -> str:
    if st.session_state.get("language") == "Tagalog":
        return tagalog
    return english


# ── Header ────────────────────────────────────────────────────────
st.title("🌱 Taniman")
st.subheader(t("Share your feedback", "Ibahagi ang inyong puna"))
st.markdown(t(
    """
Taniman is a **free tool**, still growing. Your honest feedback — good or bad — directly shapes what we build next.

It takes less than a minute. Thank you! 🙏
    """,
    """
Ang Taniman ay **libreng tool**, patuloy pa itong umuunlad. Ang inyong tapat na puna — mabuti man o hindi — direktang nakakaapekto sa aming mga pagpapabuti.

Mabilis lamang ito. Salamat! 🙏
    """
))

st.divider()

# ── Form ──────────────────────────────────────────────────────────
with st.form("feedback_form", clear_on_submit=True):

    # 1. Overall rating
    rating = st.select_slider(
        t("⭐ Overall, how useful was Taniman?", "⭐ Sa kabuuan, gaano ka-kapaki-pakinabang ang Taniman?"),
        options=[
            t("😞 Not useful",      "😞 Hindi kapaki-pakinabang"),
            t("😐 Somewhat useful", "😐 Medyo kapaki-pakinabang"),
            t("🙂 Useful",          "🙂 Kapaki-pakinabang"),
            t("😄 Very useful",     "😄 Napakakapaki-pakinabang"),
            t("🤩 Excellent!",      "🤩 Napakagaling!"),
        ],
        value=t("🙂 Useful", "🙂 Kapaki-pakinabang"),
    )

    # 2. What worked well
    what_worked = st.text_area(
        t("✅ What worked well?", "✅ Ano ang maganda?"),
        placeholder=t(
            "e.g. The harvest schedule was accurate, easy to use on mobile...",
            "hal. Tumpak ang iskedyul ng ani, madaling gamitin sa telepono..."
        ),
        height=100,
    )

    # 3. What to improve
    what_to_improve = st.text_area(
        t("🔧 What should we improve?", "🔧 Ano ang dapat naming pagbutihin?"),
        placeholder=t(
            "e.g. More vegetables, better advice for container gardening...",
            "hal. Mas maraming gulay, mas magandang payo para sa paso..."
        ),
        height=100,
    )

    # 4. Would they recommend
    recommend = st.radio(
        t("💬 Would you recommend Taniman to other gardeners?", "💬 Irerekomenda ba ninyo ang Taniman sa ibang mga hardinero?"),
        options=[
            t("Yes, definitely!", "Oo, tiyak na!"),
            t("Maybe",            "Marahil"),
            t("No",               "Hindi"),
        ],
        horizontal=True,
    )

    # 5. Optional contact
    contact = st.text_input(
        t(
            "📧 Email (optional — only if you'd like us to follow up)",
            "📧 Email (opsyonal — kung gusto ninyong makipag-ugnayan)"
        ),
        placeholder="you@example.com",
    )

    submitted = st.form_submit_button(
        t("📤 Submit Feedback", "📤 Isumite ang Puna"),
        use_container_width=True
    )

if submitted:
    try:
        save_feedback({
            "rating":          rating,
            "what_worked":     what_worked,
            "what_to_improve": what_to_improve,
            "recommend":       recommend,
            "contact":         contact,
            "location":        st.session_state.get("location"),
            "mode":            st.session_state.get("user_mode"),
        })
        st.success(t(
            "🌱 Thank you! Your feedback helps Taniman grow.",
            "🌱 Salamat! Ang inyong puna ay tumutulong sa Taniman na lumago."
        ))
        st.balloons()
    except Exception as e:
        st.error(t(
            f"Something went wrong saving your feedback. Please try again. ({e})",
            f"May naganap na error. Pakisubukan muli. ({e})"
        ))

# ── Back link ─────────────────────────────────────────────────────
st.divider()
if st.button(t("← Back to Taniman", "← Bumalik sa Taniman"), use_container_width=False):
    st.switch_page("main.py")