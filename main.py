import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
from datetime import datetime
from bukid.crew import run_research, run_schedule, run_qa, run_preparation
from chart import render_schedule_mobile_friendly, render_price_table
from bukid.models.models import VegetableScheduleOutput

#from dotenv import load_dotenv
#load_dotenv()


#os.environ["MODEL"] = st.secrets.get("MODEL", "")
#os.environ["ANTHROPIC_API_KEY"] = st.secrets.get("ANTHROPIC_API_KEY", "")


from dotenv import load_dotenv
# Loads .env locally, does nothing on Streamlit Cloud
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

try:
    # On Streamlit Cloud, load from st.secrets
    if "MODEL" in st.secrets:
        os.environ["MODEL"] = st.secrets["MODEL"]

    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

except Exception:
    pass 

def get_user_location():
    if "location" not in st.session_state:
        st.session_state.location = None

    if not st.session_state.location:
        with st.form("location_form"):
            st.subheader("Where is your garden located?")
            location = st.text_input("📍 Enter your city or region (e.g. Manila, Philippines)")
            submitted = st.form_submit_button("Start")

            if submitted and location.strip():
                st.session_state.location = location.strip()
                st.rerun()
            elif submitted:
                st.warning("Please enter your location to continue.")
        st.stop()

    st.success(f"📍 Garden location: {st.session_state.location}")

def get_user_language():
    if "language" not in st.session_state:
        st.session_state.language = None

    if not st.session_state.language:
        st.subheader("Please select your preferred language / Piliin ang iyong wika")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇺🇸 English", use_container_width=True):
                st.session_state.language = "English"
                st.rerun()
        with col2:
            if st.button("🇵🇭 Tagalog", use_container_width=True):
                st.session_state.language = "Tagalog"
                st.rerun()
        st.stop()

def get_planting_medium():
    if "planting_medium" not in st.session_state:
        st.session_state.planting_medium = None

    if not st.session_state.planting_medium:
        st.subheader("How will you be planting? / Paano mo itatanim?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌍 Ground / Diretso sa lupa", use_container_width=True):
                st.session_state.planting_medium = "in-ground"
                st.rerun()
        with col2:
            if st.button("🪴 Pots / Paso", use_container_width=True):
                st.session_state.planting_medium = "pots"
                st.rerun()
        st.stop()

def t(english: str, tagalog: str) -> str:
    """Return the correct language string based on user preference."""
    if st.session_state.get("language") == "Tagalog":
        return tagalog
    return english


# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="🌱 Home Gardening Assistant", page_icon="🌱")
st.title("🌱 Home Gardening Assistant")
st.caption("Your AI-powered gardening crew!")


# ── Step 1: Get User Details ──────────────────────────────────────
get_user_location()
get_user_language()
get_planting_medium()

crew_inputs = {
    'location': st.session_state.location,
    'previous_year': str(datetime.now().year - 2),
    'language': st.session_state.language,
    'planting_medium': st.session_state.planting_medium  # 👈 add here
}




# ── Step 2: Initialize session state ─────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "research_done" not in st.session_state:
    st.session_state.research_done = False
if "vegetables" not in st.session_state:
    st.session_state.vegetables = None
if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False
if "awaiting_feedback" not in st.session_state:
    st.session_state.awaiting_feedback = False
if "schedule_output" not in st.session_state:
    st.session_state.schedule_output = None
if "schedule_shown" not in st.session_state:
    st.session_state.schedule_shown = False
if "awaiting_preparation" not in st.session_state:
    st.session_state.awaiting_preparation = False
if "preparation_done" not in st.session_state:
    st.session_state.preparation_done = False
if "preparation_output" not in st.session_state:
    st.session_state.preparation_output = None


# ── Step 3: Display chat history ──────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Step 3b: Re-render chart if it exists ─────────────────────
#if st.session_state.get("schedule_output"):
#    schedule = st.session_state.schedule_output
#    st.markdown(f"📝 {schedule.notes}")
#    st.markdown(f"*Generated by {schedule.generated_by} on {schedule.timestamp}*")
#    render_schedule_mobile_friendly(schedule)
#    render_price_table(schedule)

if st.session_state.get("schedule_output"):
    render_schedule_mobile_friendly(st.session_state.schedule_output)
    render_price_table(st.session_state.schedule_output)

    #if not st.session_state.schedule_shown:
    st.session_state.schedule_shown = True  # 👈 mark as shown
        #st.rerun()




# ── Step 4: Run Agent 1 automatically on first load ──────────
if not st.session_state.research_done:
    with st.chat_message("assistant"):
        with st.spinner(t("Finding the best vegetables for your area...", "Hinahanap ang pinakamainam na mga gulay para sa inyong lugar...")):
            result = run_research(crew_inputs)

        st.session_state.vegetables = result
        st.session_state.research_done = True

        follow_up = t(
            "\n\n---\n💬 **Are you happy with these vegetables? You can also add any vegetables you'd like to include!**",
            "\n\n---\n💬 **Okay na ba kayo sa mga gulay na ito? Maaari din kayong magdagdag ng mga gulay na gusto ninyo!**"
        )
        full_message = result + follow_up
        st.markdown(full_message)
        st.session_state.awaiting_feedback = True

    st.session_state.messages.append({"role": "assistant", "content": full_message})
    st.rerun()

# ── Step 4b: Handle vegetable feedback ───────────────────────
if st.session_state.get("awaiting_feedback"):

    # Add vegetables text input
    st.markdown(t(
        "**Want to add any vegetables to the list?**",
        "**Gusto ba ninyong magdagdag ng mga gulay sa listahan?**"
    ))

    with st.form("add_vegetables_form", clear_on_submit=True):
        vegetable_input = st.text_input(t(
            "Type a vegetable to add (optional)",
            "Mag-type ng gulay na idadagdag (opsyonal)"
        ))
        col1, col2 = st.columns(2)
        with col1:
            add_clicked = st.form_submit_button(
                t("➕ Add Vegetable", "➕ Magdagdag ng Gulay"),
                use_container_width=True
            )
        with col2:
            done_clicked = st.form_submit_button(
                t("✅ Done, I'm happy with the list!", "✅ Okay na ang listahan!"),
                use_container_width=True
            )

    if add_clicked and vegetable_input.strip():
        st.session_state.vegetables += f"\n\nAdditional vegetables requested by user: {vegetable_input.strip()}"
        msg = t(
            f"Got it! I've added **{vegetable_input.strip()}** to your list. 🌱 Any more to add, or click done to continue!",
            f"Sige! Idinagdag ko na ang **{vegetable_input.strip()}** sa inyong listahan. 🌱 May idadagdag pa ba, o pindutin ang done para magpatuloy!"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()

    elif add_clicked and not vegetable_input.strip():
        st.warning(t(
            "Please type a vegetable name first.",
            "Mangyaring mag-type muna ng pangalan ng gulay."
        ))

    if done_clicked:
        st.session_state.awaiting_feedback = False
        msg = t(
            "Great! **Would you like me to create a planting schedule for these vegetables?**",
            "Magaling! **Gusto ba ninyong gumawa ng iskedyul ng pagtatanim para sa mga gulay na ito?**"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.awaiting_confirmation = True
        st.rerun()

    st.stop()

# ── Step 5: Handle user reply ─────────────────────────────────
if st.session_state.awaiting_confirmation:
    st.markdown(t(
        "**Would you like me to create a planting schedule?**",
        "**Gusto ba ninyong gumawa ng iskedyul ng pagtatanim?**"
    ))

    col1, col2 = st.columns(2)
    with col1:
        yes_clicked = st.button(
            t("✅ Yes, create my schedule!", "✅ Oo, gumawa ng iskedyul!"),
            use_container_width=True,
            key="schedule_yes"
        )
    with col2:
        no_clicked = st.button(
            t("❌ No, thanks", "❌ Hindi, salamat"),
            use_container_width=True,
            key="schedule_no"
        )

    if yes_clicked:
        st.session_state.awaiting_confirmation = False
        with st.chat_message("assistant"):
            with st.spinner(t("Creating your planting schedule...", "Ginagawa ang inyong iskedyul ng pagtatanim...")):
                schedule = run_schedule(crew_inputs, st.session_state.vegetables)
            st.session_state.schedule_output = schedule

        st.session_state.messages.append({"role": "assistant", "content": t(
            "📊 Here's your planting schedule!",
            "📊 Narito ang inyong iskedyul ng pagtatanim!"
        )})
        st.rerun()

    if no_clicked:
        st.session_state.awaiting_confirmation = False
        #st.session_state.preparation_done = True
        st.session_state.schedule_shown = True
        msg = t(
            "No problem! Would you still like advice on how to prepare for planting? 🌱",
            "Okay lang! Gusto ba ninyong malaman kung paano maghanda para sa pagtatanim? 🌱"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()

    st.stop()

# ── Step 5b: Ask if user wants preparation advice ─────────────
if st.session_state.schedule_shown and not st.session_state.preparation_done and not st.session_state.awaiting_preparation:
    msg = t(
        "🌱 **Would you like advice on how to prepare for planting?** I can help with growing from food scraps and soil preparation!",
        "🌱 **Gusto ba ninyong malaman kung paano maghanda para sa pagtatanim?** Matutulungan ko kayo sa pagpapalaki mula sa tira-tirang pagkain at paghahanda ng lupa!"
    )
    with st.chat_message("assistant"):
        st.markdown(msg)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.session_state.awaiting_preparation = True
    #st.rerun()

if st.session_state.get("awaiting_preparation") and not st.session_state.preparation_done:
    col1, col2 = st.columns(2)
    with col1:
        yes_clicked = st.button(
            t("✅ Yes, help me prepare!", "✅ Oo, tulungan mo ako!"),
            use_container_width=True,
            key="prep_yes"
        )
    with col2:
        no_clicked = st.button(
            t("❌ No, thanks", "❌ Hindi, salamat"),
            use_container_width=True,
            key="prep_no"
        )

    if yes_clicked:
        st.session_state.awaiting_confirmation = False
        st.session_state.awaiting_preparation = False
        with st.chat_message("assistant"):
            with st.spinner(t(
                "Getting preparation advice...",
                "Hinahanap ang mga payo sa paghahanda..."
            )):
                preparation = run_preparation(crew_inputs, st.session_state.vegetables)
            st.session_state.preparation_output = preparation
            st.markdown(preparation)

        st.session_state.preparation_done = True
        st.session_state.messages.append({"role": "assistant", "content": preparation})
        st.rerun()

    if no_clicked:
        st.session_state.awaiting_preparation = False
        st.session_state.preparation_done = True
        st.session_state.schedule_shown = True
        msg = t(
            "No problem! Feel free to ask me anything else about your garden. 🌿",
            "Okay lang! Huwag mag-atubiling magtanong tungkol sa inyong hardin. 🌿"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()

    st.stop()  # 👈 only stops if neither button was clicked yet

# ── Step 5c: Re-render preparation advice if it exists ────────
#if st.session_state.get("preparation_output"):
#    with st.expander(t("🌱 Preparation Advice", "🌱 Mga Payo sa Paghahanda"), expanded=False):
#        st.markdown(st.session_state.preparation_output)



# ── Step 6: Open chat after flow is complete ──────────────────
if st.session_state.research_done and not st.session_state.awaiting_confirmation and st.session_state.preparation_done:
 
    if prompt := st.chat_input(t(
        "Ask me anything about your garden...",
        "Magtanong tungkol sa inyong hardin..."
    )):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t("Thinking...", "Nag-iisip...")):
                result = run_qa(crew_inputs, prompt)  # 👈 pass the actual question
            st.markdown(result)

        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()