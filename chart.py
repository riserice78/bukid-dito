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
        title="🌱 Your Garden Planting & Harvest Schedule",
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="",
        height=100 + len(df) * 40,
        legend_title="Vegetable"
    )
    st.plotly_chart(fig, width='stretch')


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