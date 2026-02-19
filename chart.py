import plotly.express as px
import pandas as pd
import streamlit as st
from bukid.models.models import VegetableScheduleOutput
from datetime import date

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
            st.markdown(f"**💡 Why it thrives:** {v.reason}")

def render_gantt(output: VegetableScheduleOutput):
    rows = []
    for v in output.vegetable_schedule:
        rows.append({
            "Vegetable": v.vegetable,
            "Task": "🌱 Plant",
            "Start": month_to_date(v.plant_start_month),
            "End": month_to_date(v.plant_end_month, 28),
            "Notes": v.reason
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


def render_price_table(output: VegetableScheduleOutput):
    """Show a summary table with market prices."""
    rows = [{
        "Vegetable": v.vegetable,
        "Plant": f"{MONTH_NAMES[v.plant_start_month]} → {MONTH_NAMES[v.plant_end_month]}",
        "Harvest": f"{MONTH_NAMES[v.harvest_start_month]} → {MONTH_NAMES[v.harvest_end_month]}",
        "Price Range": f"{v.vegetable_price_currency} {v.vegetable_price.low} – {v.vegetable_price.high}/kg",
        "Companion Plant": v.companion_plant,
        "Why it thrives": v.reason
    } for v in output.vegetable_schedule]

    st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)