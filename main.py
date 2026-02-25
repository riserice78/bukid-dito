import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
from datetime import datetime, date
from bukid.crew import run_research, run_schedule, run_qa, run_preparation, run_replanting
from chart import (
    render_schedule_mobile_friendly, render_summary_table,
    render_preparation_cards, render_research_cards,
    render_harvest_tracker, render_replanting_cards,
)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


import streamlit.components.v1 as components


def inject_ga(measurement_id):
    st.markdown(f"""
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{measurement_id}');
        </script>
    """, unsafe_allow_html=True)
st.set_page_config(page_title="Taniman", page_icon="🌱")
inject_ga("G-WB15NHP8VN")  # ✅ call it here


try:
    if "MODEL" in st.secrets:
        os.environ["MODEL"] = st.secrets["MODEL"]
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass


# ── Helpers ───────────────────────────────────────────────────────
def t(english: str, tagalog: str) -> str:
    if st.session_state.get("language") == "Tagalog":
        return tagalog
    return english


# ── Page config ───────────────────────────────────────────────────
#st.set_page_config(page_title="Taniman", page_icon="🌱")
#st.markdown("""
#    <style>
#    div[data-testid="stSidebarNav"] { display: none !important; }
#    section[data-testid="stSidebar"] { display: none !important; }
#    </style>
#""", unsafe_allow_html=True)
st.title("🌱 Taniman 🌱")
st.caption("Your AI-powered gardening crew!")


# ══════════════════════════════════════════════════════════════════
# STEP 1: Location
# ══════════════════════════════════════════════════════════════════
if "location" not in st.session_state:
    st.session_state.location = None

if not st.session_state.location:
    with st.form("location_form"):
        st.subheader("Where is your garden located?")
        location = st.text_input("📍 Enter your city or region (e.g. Manila, Philippines)")
        if st.form_submit_button("Start"):
            if location.strip():
                st.session_state.location = location.strip()
                st.rerun()
            else:
                st.warning("Please enter your location to continue.")
    st.stop()

st.success(f"📍 Garden location: {st.session_state.location}")


# ══════════════════════════════════════════════════════════════════
# STEP 2: Language
# ══════════════════════════════════════════════════════════════════
if "language" not in st.session_state:
    st.session_state.language = None

if not st.session_state.language:
    st.subheader("Please select your preferred language / Piliin ang iyong wika")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇺🇸 English", use_container_width=True, key="lang_en"):
            st.session_state.language = "English"
            st.rerun()
    with col2:
        if st.button("🇵🇭 Tagalog", use_container_width=True, key="lang_tl"):
            st.session_state.language = "Tagalog"
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════
# STEP 3: Planning vs Already Planted
# ══════════════════════════════════════════════════════════════════
if "user_mode" not in st.session_state:
    st.session_state.user_mode = None  # "planning" or "planted"

if not st.session_state.user_mode:
    st.subheader(t(
        "What brings you here today?",
        "Ano ang inyong layunin ngayon?"
    ))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            t("🌱 I'm planning my garden", "🌱 Nagpaplano ako ng aking hardin"),
            use_container_width=True, key="mode_planning"
        ):
            st.session_state.user_mode = "planning"
            st.rerun()
    with col2:
        if st.button(
            t("🌾 I've already planted", "🌾 Nagtanim na ako"),
            use_container_width=True, key="mode_planted"
        ):
            st.session_state.user_mode = "planted"
            st.rerun()
    st.stop()


# ── crew_inputs (available after location + language confirmed) ───
crew_inputs = {
    "location": st.session_state.location,
    "previous_year": str(datetime.now().year - 1),
    "language": st.session_state.language,
    "planting_medium": st.session_state.get("planting_medium", "pots"),
}


# ── Session state init ────────────────────────────────────────────
defaults = {
    "messages": [],
    "planting_medium": None,
    "research_done": False,
    "research_output": None,
    "vegetables": None,
    "extra_vegetables": [],
    "awaiting_feedback": False,
    "awaiting_garden_design": False,
    "garden_design_done": False,
    "awaiting_confirmation": False,
    "schedule_output": None,
    "schedule_shown": False,
    "awaiting_preparation": False,
    "preparation_done": False,
    "preparation_output": None,
    "tracker_shown": False,
    "planted_dates": {},
    "awaiting_tracker": False,
    "harvested_vegetable": None,
    "replanting_output": None,
    "awaiting_replanting": False,
    "awaiting_replanting_direct": False,
    "already_planted_flow_done": False,
    "awaiting_already_planted_choice": False,
    "planted_greeted": False,
    "awaiting_planted_vegetables": False,
    "planted_vegetables_input": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Chat history replay ───────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["content"] == "__SCHEDULE_CHART__":
            render_schedule_mobile_friendly(st.session_state.schedule_output)
            render_summary_table(st.session_state.schedule_output)
            st.session_state.schedule_shown = True
        elif message["content"] == "__PREPARATION_CARDS__":
            render_preparation_cards(st.session_state.preparation_output)
        elif message["content"] == "__RESEARCH_CARDS__":
            render_research_cards(st.session_state.research_output)
        elif message["content"] == "__HARVEST_TRACKER__":
            if st.session_state.schedule_output and st.session_state.planted_dates:
                render_harvest_tracker(st.session_state.schedule_output, st.session_state.planted_dates)
        elif message["content"] == "__REPLANTING_CARDS__":
            if st.session_state.replanting_output:
                render_replanting_cards(st.session_state.replanting_output)
        else:
            st.markdown(message["content"])


# ── Feedback link ─────────────────────────────────────────────────
st.divider()
st.caption(t(
    "🌱 Taniman is free and still growing. [Share your feedback →](./feedback)",
    "🌱 Ang Taniman ay libre at patuloy umuunlad. [Ibahagi ang inyong puna →](./feedback)"
))

# ══════════════════════════════════════════════════════════════════
# BRANCH A: PLANNING MODE
# ══════════════════════════════════════════════════════════════════
if st.session_state.user_mode == "planning":

    # ── A1: Planting medium ───────────────────────────────────────
    if not st.session_state.planting_medium:
        st.subheader(t(
            "How will you be planting?",
            "Paano mo itatanim?"
        ))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌍 Ground / Diretso sa lupa", use_container_width=True, key="med_ground"):
                st.session_state.planting_medium = "in-ground"
                crew_inputs["planting_medium"] = "in-ground"
                st.rerun()
        with col2:
            if st.button("🪴 Pots / Paso", use_container_width=True, key="med_pots"):
                st.session_state.planting_medium = "pots"
                crew_inputs["planting_medium"] = "pots"
                st.rerun()
        st.stop()

    # Keep crew_inputs in sync
    crew_inputs["planting_medium"] = st.session_state.planting_medium

    # ── A2: Research ──────────────────────────────────────────────
    if not st.session_state.research_done:
        with st.chat_message("assistant"):
            with st.spinner(t(
                "Finding the best vegetables for your area...",
                "Hinahanap ang pinakamainam na mga gulay para sa inyong lugar..."
            )):
                result = run_research(crew_inputs)
            st.session_state.research_output = result
            st.session_state.vegetables = "\n".join(
                [v.vegetable for v in result.vegetable_recommendations]
            )
            st.session_state.research_done = True
            st.session_state.awaiting_feedback = True

        follow_up = t(
            "\n\n---\n💬 **Are you happy with these vegetables? You can also add any vegetables you'd like to include!**",
            "\n\n---\n💬 **Okay na ba kayo sa mga gulay na ito? Maaari din kayong magdagdag ng mga gulay na gusto ninyo!**"
        )
        st.session_state.messages.append({"role": "assistant", "content": "__RESEARCH_CARDS__"})
        st.session_state.messages.append({"role": "assistant", "content": follow_up})
        st.rerun()

    # ── A3: Vegetable feedback ────────────────────────────────────
    if st.session_state.awaiting_feedback:
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
                add_clicked = st.form_submit_button(t("➕ Add Vegetable", "➕ Magdagdag ng Gulay"), use_container_width=True)
            with col2:
                done_clicked = st.form_submit_button(t("✅ Done, I'm happy with the list!", "✅ Okay na ang listahan!"), use_container_width=True)

        if add_clicked and vegetable_input.strip():
            new_veg = vegetable_input.strip()
            st.session_state.vegetables += f"\n\nAdditional vegetables requested by user: {new_veg}"
            st.session_state.extra_vegetables.append(new_veg)
            msg = t(
                f"Got it! I've added **{new_veg}** to your list. 🌱 Any more to add, or click done to continue!",
                f"Sige! Idinagdag ko na ang **{new_veg}** sa inyong listahan. 🌱 May idadagdag pa ba, o pindutin ang done para magpatuloy!"
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()
        elif add_clicked:
            st.warning(t("Please type a vegetable name first.", "Mangyaring mag-type muna ng pangalan ng gulay."))

        if done_clicked:
            st.session_state.awaiting_feedback = False
            msg = t(
                "Great! 🌿 **Would you like to design your garden layout first?**",
                "Magaling! 🌿 **Gusto ba ninyong mag-disenyo ng inyong hardin bago gumawa ng iskedyul?**"
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.awaiting_garden_design = True
            st.rerun()
        st.stop()

    # ── A4: Garden designer ───────────────────────────────────────
    if st.session_state.awaiting_garden_design and not st.session_state.garden_design_done:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("🌿 Yes, design my garden!", "🌿 Oo, mag-disenyo ng hardin!"), use_container_width=True, key="design_yes"):
                st.session_state.awaiting_garden_design = False
                st.switch_page("pages/garden_designer_page.py")
        with col2:
            if st.button(t("⏭ Skip, go to schedule", "⏭ Laktawan, pumunta sa iskedyul"), use_container_width=True, key="design_no"):
                st.session_state.awaiting_garden_design = False
                st.session_state.garden_design_done = True
                msg = t(
                    "No problem! **Would you like me to create a planting schedule for these vegetables?**",
                    "Okay lang! **Gusto ba ninyong gumawa ng iskedyul ng pagtatanim para sa mga gulay na ito?**"
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.session_state.awaiting_confirmation = True
                st.rerun()
        st.stop()

    # ── A5: Schedule confirmation ─────────────────────────────────
    if st.session_state.awaiting_confirmation and st.session_state.garden_design_done:
        st.markdown(t(
            "**Would you like me to create a planting schedule?**",
            "**Gusto ba ninyong gumawa ng iskedyul ng pagtatanim?**"
        ))
        col1, col2 = st.columns(2)
        with col1:
            yes_clicked = st.button(t("✅ Yes, create my schedule!", "✅ Oo, gumawa ng iskedyul!"), use_container_width=True, key="schedule_yes")
        with col2:
            no_clicked = st.button(t("❌ No, thanks", "❌ Hindi, salamat"), use_container_width=True, key="schedule_no")

        if yes_clicked:
            st.session_state.awaiting_confirmation = False
            with st.chat_message("assistant"):
                with st.spinner(t("Creating your planting schedule...", "Ginagawa ang inyong iskedyul ng pagtatanim...")):
                    schedule = run_schedule(crew_inputs, st.session_state.vegetables)
                st.session_state.schedule_output = schedule
            st.session_state.messages.append({"role": "assistant", "content": "__SCHEDULE_CHART__"})
            st.session_state.messages.append({"role": "assistant", "content": t(
                "📊 Here's your planting schedule!",
                "📊 Narito ang inyong iskedyul ng pagtatanim!"
            )})
            st.rerun()

        if no_clicked:
            st.session_state.awaiting_confirmation = False
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

    # ── A6: Preparation advice ────────────────────────────────────
    if st.session_state.schedule_shown and not st.session_state.preparation_done and not st.session_state.awaiting_preparation:
        msg = t(
            "🌱 **Would you like advice on how to prepare for planting?**",
            "🌱 **Gusto ba ninyong malaman kung paano maghanda para sa pagtatanim?**"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.awaiting_preparation = True

    if st.session_state.awaiting_preparation and not st.session_state.preparation_done:
        col1, col2 = st.columns(2)
        with col1:
            yes_prep = st.button(t("✅ Yes, help me prepare!", "✅ Oo, tulungan mo ako!"), use_container_width=True, key="prep_yes")
        with col2:
            no_prep = st.button(t("❌ No, thanks", "❌ Hindi, salamat"), use_container_width=True, key="prep_no")

        if yes_prep:
            st.session_state.awaiting_preparation = False
            with st.chat_message("assistant"):
                with st.spinner(t("Getting preparation advice...", "Hinahanap ang mga payo sa paghahanda...")):
                    preparation = run_preparation(crew_inputs, st.session_state.vegetables)
            st.session_state.preparation_output = preparation
            st.session_state.preparation_done = True
            st.session_state.messages.append({"role": "assistant", "content": "__PREPARATION_CARDS__"})
            st.rerun()

        if no_prep:
            st.session_state.awaiting_preparation = False
            st.session_state.preparation_done = True
            msg = t(
                "No problem! Feel free to ask me anything else about your garden. 🌿",
                "Okay lang! Huwag mag-atubiling magtanong tungkol sa inyong hardin. 🌿"
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()
        st.stop()


# ══════════════════════════════════════════════════════════════════
# BRANCH B: ALREADY PLANTED MODE
# ══════════════════════════════════════════════════════════════════
elif st.session_state.user_mode == "planted":

    # ── B1: Ask what they need ────────────────────────────────────
    if not st.session_state.planted_greeted and not st.session_state.get("awaiting_replanting_direct"):
        msg = t(
            "Welcome back, gardener! 🌾 What would you like help with today?",
            "Maligayang pagbabalik, hardinero! 🌾 Ano ang maitutulong ko sa inyo ngayon?"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.planted_greeted = True
        st.session_state.awaiting_already_planted_choice = True
        st.rerun()

    if st.session_state.awaiting_already_planted_choice and not st.session_state.already_planted_flow_done:
        col1, col2, col3 = st.columns(3)
        with col1:
            harvest_clicked = st.button(
                t("🌾 See harvest schedule", "🌾 Tingnan ang iskedyul ng ani"),
                use_container_width=True, key="ap_harvest"
            )
        with col2:
            replant_clicked = st.button(
                t("♻️ Replanting advice", "♻️ Payo sa pagtatanim muli"),
                use_container_width=True, key="ap_replant"
            )
        with col3:
            qa_clicked = st.button(
                t("💬 Ask a question", "💬 Magtanong"),
                use_container_width=True, key="ap_qa"
            )

        # ── B2a: Harvest schedule ─────────────────────────────────
        if harvest_clicked:
            st.session_state.awaiting_already_planted_choice = False
            if not st.session_state.planting_medium:
                st.session_state.planting_medium = "in-ground"
                crew_inputs["planting_medium"] = "in-ground"
            msg = t(
                "Let's build your harvest schedule! What vegetables have you planted?",
                "Gumawa tayo ng iskedyul ng ani! Ano-anong mga gulay ang inyong naitanim?"
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.awaiting_planted_vegetables = True
            st.rerun()

        # ── B2b: Replanting advice ────────────────────────────────
        if replant_clicked:
            st.session_state.awaiting_already_planted_choice = False
            if not st.session_state.planting_medium:
                st.session_state.planting_medium = "in-ground"
                crew_inputs["planting_medium"] = "in-ground"

            msg = t(
                "Sure! Which vegetable did you just harvest?",
                "Sige! Aling gulay ang inyong kakaani?"
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.awaiting_replanting_direct = True
            st.rerun()

        # ── B2c: Ask a question ───────────────────────────────────
        if qa_clicked:
            st.session_state.awaiting_already_planted_choice = False
            st.session_state.already_planted_flow_done = True
            if not st.session_state.planting_medium:
                st.session_state.planting_medium = "in-ground"
                crew_inputs["planting_medium"] = "in-ground"
            msg = t(
                "Of course! What would you like to know about your garden? 🌿",
                "Sige! Ano ang gusto ninyong malaman tungkol sa inyong hardin? 🌿"
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()

        st.stop()

    # ── B2b form: collect harvested vegetable (outside choice block) ──
    if st.session_state.get("awaiting_replanting_direct"):
        with st.form("replanting_direct_form"):
            harvested = st.text_input(t(
                "Enter the vegetable you harvested",
                "Ilagay ang gulay na inyong naani"
            ))
            if st.form_submit_button(t("🌱 Get suggestions", "🌱 Kumuha ng mungkahi")):
                if harvested.strip():
                    st.session_state.awaiting_replanting_direct = False
                    st.session_state.harvested_vegetable = harvested.strip()
                    with st.chat_message("assistant"):
                        with st.spinner(t("Finding the best crops to plant next...", "Hinahanap ang pinakamainam na susunod na itatanim...")):
                            replanting = run_replanting(crew_inputs, harvested.strip())
                        st.session_state.replanting_output = replanting
                    st.session_state.messages.append({"role": "assistant", "content": "__REPLANTING_CARDS__"})
                    st.session_state.already_planted_flow_done = True
                    st.rerun()
                else:
                    st.warning(t("Please enter a vegetable.", "Mangyaring maglagay ng gulay."))
        st.stop()

    # ── B2a form: collect vegetable list (outside choice block) ──
    if st.session_state.get("awaiting_planted_vegetables"):
        with st.form("planted_vegetables_form"):
            veg_input = st.text_area(t(
                "List the vegetables you have planted (one per line or comma-separated)",
                "Ilista ang mga gulay na inyong naitanim (isa bawat linya o pinaghiwalay ng kuwit)"
            ))
            if st.form_submit_button(t("✅ Continue", "✅ Magpatuloy")):
                if veg_input.strip():
                    st.session_state.awaiting_planted_vegetables = False
                    st.session_state.vegetables = veg_input.strip()
                    st.session_state.research_done = True
                    st.session_state.garden_design_done = True
                    st.session_state.awaiting_confirmation = True
                    user_msg = veg_input.strip()
                    st.session_state.messages.append({"role": "user", "content": user_msg})
                    st.rerun()
                else:
                    st.warning(t("Please enter at least one vegetable.", "Mangyaring maglagay ng kahit isang gulay."))
        st.stop()

    # ── B3: Harvest schedule flow (reuses planning schedule step) ─
    if st.session_state.awaiting_confirmation and st.session_state.garden_design_done and not st.session_state.schedule_output:
        st.markdown(t(
            "**Would you like me to generate a harvest schedule based on your planted vegetables?**",
            "**Gusto ba ninyong gumawa ng iskedyul ng ani batay sa inyong mga natanim?**"
        ))
        col1, col2 = st.columns(2)
        with col1:
            yes_sched = st.button(t("✅ Yes please!", "✅ Oo, sige!"), use_container_width=True, key="ap_sched_yes")
        with col2:
            no_sched = st.button(t("❌ Skip", "❌ Laktawan"), use_container_width=True, key="ap_sched_no")

        if yes_sched:
            st.session_state.awaiting_confirmation = False
            with st.chat_message("assistant"):
                with st.spinner(t("Creating your harvest schedule...", "Ginagawa ang inyong iskedyul ng ani...")):
                    schedule = run_schedule(crew_inputs, st.session_state.vegetables)
                st.session_state.schedule_output = schedule
                st.session_state.schedule_shown = True
            st.session_state.messages.append({"role": "assistant", "content": "__SCHEDULE_CHART__"})
            st.session_state.messages.append({"role": "assistant", "content": t(
                "📊 Here's your harvest schedule! Now let's log when you planted each vegetable.",
                "📊 Narito ang inyong iskedyul ng ani! Itala natin kung kailan ninyo naitanim ang bawat gulay."
            )})
            st.rerun()

        if no_sched:
            st.session_state.awaiting_confirmation = False
            st.session_state.already_planted_flow_done = True
            st.rerun()
        st.stop()

    # ── B4: Log planting dates → tracker ─────────────────────────
    if st.session_state.schedule_output and not st.session_state.tracker_shown and not st.session_state.awaiting_tracker:
        st.session_state.awaiting_tracker = True

    if st.session_state.awaiting_tracker and not st.session_state.tracker_shown:
        schedule = st.session_state.schedule_output
        msg = t("When did you plant each vegetable?", "Kailan ninyo itinatanim ang bawat gulay?")
        with st.chat_message("assistant"):
            st.markdown(msg)
            with st.form("planting_dates_form"):
                dates = {}
                for v in schedule.vegetable_schedule:
                    dates[v.vegetable] = st.date_input(
                        f"📅 {v.vegetable}",
                        value=date.today(),
                        key=f"date_{v.vegetable}"
                    )
                if st.form_submit_button(t("💾 Save planting dates", "💾 I-save ang mga petsa")):
                    st.session_state.planted_dates = dates
                    st.session_state.tracker_shown = True
                    st.session_state.awaiting_tracker = False
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.session_state.messages.append({"role": "assistant", "content": "__HARVEST_TRACKER__"})
                    st.rerun()
        st.stop()

    # ── B5: Replanting prompt after tracker ───────────────────────
    if st.session_state.tracker_shown and not st.session_state.awaiting_replanting and not st.session_state.replanting_output and not st.session_state.already_planted_flow_done:
        msg = t(
            "🔄 **Is your harvest done?** I can suggest what to plant next!",
            "🔄 **Tapos na ba ang pag-ani?** Maaari akong magmungkahi ng susunod na itatanim!"
        )
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.awaiting_replanting = True

    if st.session_state.awaiting_replanting and not st.session_state.replanting_output:
        schedule = st.session_state.schedule_output
        veg_names = [v.vegetable for v in schedule.vegetable_schedule] if schedule else []
        with st.form("replanting_form"):
            harvested = st.selectbox(
                t("Which vegetable did you harvest?", "Aling gulay ang inyong naani?"),
                options=veg_names
            )
            if st.form_submit_button(t("🌱 Get replanting suggestions", "🌱 Kumuha ng mungkahi")):
                st.session_state.awaiting_replanting = False
                st.session_state.harvested_vegetable = harvested
                st.session_state.already_planted_flow_done = True
                with st.chat_message("assistant"):
                    with st.spinner(t("Finding the best crops to plant next...", "Hinahanap ang pinakamainam na susunod na itatanim...")):
                        replanting = run_replanting(crew_inputs, harvested)
                    st.session_state.replanting_output = replanting
                st.session_state.messages.append({"role": "assistant", "content": "__REPLANTING_CARDS__"})
                st.rerun()

        col1, col2 = st.columns(2)
        with col2:
            if st.button(t("⏭ Skip", "⏭ Laktawan"), use_container_width=True, key="skip_replant"):
                st.session_state.awaiting_replanting = False
                st.session_state.already_planted_flow_done = True
                st.rerun()
        st.stop()


# ══════════════════════════════════════════════════════════════════
# STEP 6: Open chat — available at end of both branches
# ══════════════════════════════════════════════════════════════════
planning_done = (
    st.session_state.user_mode == "planning"
    and st.session_state.preparation_done
    and not st.session_state.awaiting_confirmation
)
planted_done = (
    st.session_state.user_mode == "planted"
    and st.session_state.already_planted_flow_done
)

if planning_done or planted_done:
    if prompt := st.chat_input(t(
        "Ask me anything about your garden...",
        "Magtanong tungkol sa inyong hardin..."
    )):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(t("Thinking...", "Nag-iisip...")):
                result = run_qa(crew_inputs, prompt)
            st.markdown(result)
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()