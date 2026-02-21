import plotly.express as px
import pandas as pd
import streamlit as st
from bukid.models.models import VegetableScheduleOutput, VegetablePreparationOutput, VegetableResearchOutput, ReplantingOutput
from datetime import date


HARVEST_TRACKER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');
.tracker-card {
    background: #f0f7e6;
    border: 1px solid #c5e1a5;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-family: 'DM Sans', sans-serif;
}
.tracker-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
.tracker-veg {
    font-size: 1rem;
    font-weight: 500;
    color: #2e5c0e;
}
.tracker-dates {
    display: flex;
    gap: 16px;
    font-size: 0.8rem;
    color: #4a6741;
}
.tracker-date-item strong {
    color: #558b2f;
    display: block;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.tracker-countdown {
    font-size: 0.78rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    white-space: nowrap;
}
.countdown-soon  { background: #fff8e1; color: #f57f17; border: 1px solid #ffe082; }
.countdown-ready { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.countdown-later { background: #f1f8e9; color: #558b2f; border: 1px solid #c5e1a5; }
</style>
"""

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

def month_to_date(month: int, day: int = 1) -> str:
    year = date.today().year
    return f"{year}-{month:02d}-{day:02d}"

def render_schedule_cards(output: VegetableScheduleOutput):
    st.subheader("🌱 Planting & Harvest Schedule")
    for v in output.vegetable_schedule:
        with st.expander(f"🥬 {v.vegetable}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🌱 Plant**")
                st.markdown(f"{MONTH_NAMES[v.plant_start_month]} → {MONTH_NAMES[v.plant_end_month]}")
            with col2:
                st.markdown("**🌾 Harvest**")
                st.markdown(f"{MONTH_NAMES[v.harvest_start_month]} → {MONTH_NAMES[v.harvest_end_month]}")

            st.markdown(f"**🌿 Companion Plant:** {v.companion_plant}")
            #st.markdown(f"**💡 Why it thrives:** {v.reason}")

def render_gantt(output: VegetableScheduleOutput):
    rows = []
    for v in output.vegetable_schedule:
        rows.append({
            "Vegetable": v.vegetable,
            "Task": "🌱 Plant",
            "Start": month_to_date(v.plant_start_month),
            "End": month_to_date(v.plant_end_month, 28),
            #"Notes": v.reason
        })
        rows.append({
            "Vegetable": v.vegetable,
            "Task": "🌾 Harvest",
            "Start": month_to_date(v.harvest_start_month),
            "End": month_to_date(v.harvest_end_month, 28),
            "Notes": f"Companion: {v.companion_plant}"
        })

    df = pd.DataFrame(rows)
    df["Label"] = df["Vegetable"] + " — " + df["Task"]

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Label",
        color="Vegetable",
        hover_data=["Notes"],
        title="🌱 Planting & Harvest Schedule",
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="",
        height=100 + len(df) * 50,  # More height per row for touch targets
        margin=dict(l=10, r=10, t=40, b=40),  # Tighter margins
        legend=dict(
            orientation="h",        # 👈 horizontal legend at bottom
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        font=dict(size=11),         # Slightly smaller font
        xaxis=dict(
            tickformat="%b",        # 👈 show only month abbreviation e.g. "Jan"
            tickangle=-45           # 👈 angled ticks so they don't overlap
        )
    )

    # Make bars thicker for touch
    fig.update_traces(width=0.6)

    st.plotly_chart(fig, width='stretch', config={
        "displayModeBar": False,    # 👈 hide the plotly toolbar on mobile
        "scrollZoom": False
    })


def render_schedule_mobile_friendly(output: VegetableScheduleOutput):
    # Always show cards first
    render_schedule_cards(output)

    # Gantt chart behind an expander
    with st.expander("📊 View as Gantt Chart", expanded=False):
        render_gantt(output)


def render_summary_table(output: VegetableScheduleOutput):
    """Show a summary table"""
    rows = [{
        "Vegetable": v.vegetable,
        "Plant": f"{MONTH_NAMES[v.plant_start_month]} → {MONTH_NAMES[v.plant_end_month]}",
        "Harvest": f"{MONTH_NAMES[v.harvest_start_month]} → {MONTH_NAMES[v.harvest_end_month]}",
        #"Price Range": f"{v.vegetable_price_currency} {v.vegetable_price.low} – {v.vegetable_price.high}/kg",
        "Companion Plant": v.companion_plant,
        #"Why it thrives": v.reason
    } for v in output.vegetable_schedule]

    st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


def render_preparation_cards(output: VegetablePreparationOutput):
    st.subheader("🌱 Planting Preparation Guide")

    if output.notes:
        st.info(output.notes)

    for v in output.vegetable_preparation:
        with st.expander(f"🥬 {v.vegetable}", expanded=False):
            # Scraps row
            if v.can_grow_from_scraps:
                st.markdown("**♻️ Can grow from food scraps?** ✅ Yes")
                st.markdown(f"**How:** {v.scraps_how}")
            else:
                st.markdown("**♻️ Can grow from food scraps?** ❌ No")

            # Lead time
            st.markdown(f"**📅 Start preparation:** {v.prep_lead_time}")

            # Special tips
            st.markdown(f"**💡 Special tips:** {v.special_tips}")


def render_research_cards(output: VegetableResearchOutput):
    st.subheader("🥬 Recommended Vegetables")

    if output.summary:
        st.info(output.summary)

    for v in output.vegetable_recommendations:
        with st.expander(f"🌱 {v.vegetable}", expanded=False):
            st.markdown(f"**💡 Why it suits you:** {v.reason}")
            if v.pot_size:
                st.markdown(f"**🪴 Recommended pot size:** {v.pot_size}")



# Days from seed to first harvest (min, max) for common vegetables
DAYS_TO_HARVEST = {
    "amaranth":         (50,  75),
    "ampalaya":         (60,  75),
    "basil":            (25,  35),
    "bitter gourd":     (60,  75),
    "bitter melon":     (60,  75),
    "bottle gourd":     (55,  65),
    "broccoli":         (80, 100),
    "cabbage":          (70,  90),
    "kangkong":         (21,  30),
    "water spinach":    (21,  30),
    "carrot":           (70,  80),
    "cauliflower":      (80, 100),
    "celery":           (85, 120),
    "chili":            (70,  90),
    "chili pepper":     (70,  90),
    "chinese cabbage":  (50,  70),
    "pechay":           (30,  45),
    "bokchoy":          (30,  45),
    "bok choy":         (30,  45),
    "cilantro":         (21,  28),
    "coriander":        (21,  28),
    "corn":             (60,  90),
    "cucumber":         (50,  70),
    "eggplant":         (70,  85),
    "talong":           (70,  85),
    "garlic":           (90, 120),
    "ginger":           (180, 240),
    "green bean":       (50,  65),
    "sitaw":            (50,  65),
    "string bean":      (50,  65),
    "lettuce":          (30,  60),
    "malunggay":        (60,  90),
    "moringa":          (60,  90),
    "mongo":            (55,  65),
    "mung bean":        (55,  65),
    "mustard":          (30,  40),
    "mustasa":          (30,  40),
    "okra":             (55,  65),
    "onion":            (90, 120),
    "patola":           (60,  75),
    "luffa":            (60,  75),
    "pepper":           (70,  90),
    "potato":           (70, 120),
    "pumpkin":          (75, 100),
    "kalabasa":         (75, 100),
    "radish":           (25,  35),
    "labanos":          (25,  35),
    "saluyot":          (30,  45),
    "jute":             (30,  45),
    "spinach":          (37,  45),
    "squash":           (50,  65),
    "sweet potato":     (90, 120),
    "kamote":           (90, 120),
    "tomato":           (60,  85),
    "kamatis":          (60,  85),
    "turnip":           (45,  60),
    "upo":              (55,  65),
    "white gourd":      (55,  65),
    "winged bean":      (60,  75),
    "sigarilyas":       (60,  75),
    "zucchini":         (45,  55),
}

def get_days_to_harvest(vegetable_name: str) -> tuple[int, int]:
    """Return (min_days, max_days) for a vegetable, falling back to a sensible default."""
    key = vegetable_name.strip().lower()
    if key in DAYS_TO_HARVEST:
        return DAYS_TO_HARVEST[key]
    # Try partial match
    for k, v in DAYS_TO_HARVEST.items():
        if k in key or key in k:
            return v
    return (60, 90)  # generic fallback


def render_harvest_tracker(schedule_output: VegetableScheduleOutput, planted_dates: dict):
    from datetime import date, timedelta

    st.subheader("🌾 Harvest Tracker")
    st.markdown(HARVEST_TRACKER_CSS, unsafe_allow_html=True)

    today = date.today()

    for v in schedule_output.vegetable_schedule:
        planted = planted_dates.get(v.vegetable)
        if not planted:
            continue

        min_days, max_days = get_days_to_harvest(v.vegetable)
        harvest_date_early = planted + timedelta(days=min_days)
        harvest_date_late  = planted + timedelta(days=max_days)

        days_left = (harvest_date_early - today).days

        if days_left <= 0 and today <= harvest_date_late:
            countdown_class = "countdown-ready"
            countdown_text  = "🌾 Ready to harvest!"
        elif today > harvest_date_late:
            countdown_class = "countdown-ready"
            countdown_text  = "🌾 Past harvest window"
        elif days_left <= 14:
            countdown_class = "countdown-soon"
            countdown_text  = f"⏳ {days_left} days to go"
        else:
            countdown_class = "countdown-later"
            countdown_text  = f"{days_left} days to go"

        harvest_range = (
            f"{harvest_date_early.strftime('%b %d')} – {harvest_date_late.strftime('%b %d, %Y')}"
        )
        cycle_note = f"{min_days}–{max_days} days from seed"

        HARVEST_HTML = f"""<div class="tracker-card">
            <div class="tracker-row">
                <span class="tracker-veg">🌱 {v.vegetable}</span>
                <span class="tracker-countdown {countdown_class}">{countdown_text}</span>
            </div>
            <div class="tracker-dates" style="margin-top:8px">
                <div class="tracker-date-item">
                    <strong>Planted</strong>
                    {planted.strftime("%b %d, %Y")}
                </div>
                <div class="tracker-date-item">
                    <strong>Expected Harvest</strong>
                    {harvest_range}
                </div>
                <div class="tracker-date-item">
                    <strong>Crop Cycle</strong>
                    {cycle_note}
                </div>
            </div>
        </div>"""

        st.markdown(HARVEST_HTML, unsafe_allow_html=True)


def render_replanting_cards(output: ReplantingOutput):
    st.subheader(f"♻️ What to Plant After {output.harvested_vegetable}")

    if output.soil_rest_advice:
        st.info(f"🌍 **Soil advice:** {output.soil_rest_advice}")

    for rec in output.recommendations:
        with st.expander(f"🌱 {rec.vegetable}", expanded=False):
            st.markdown(f"**♻️ Why after {output.harvested_vegetable}:** {rec.reason}")
            st.markdown(f"**📅 When to plant:** {rec.best_time_to_plant}")
            st.markdown(f"**💡 Tip:** {rec.tip}")