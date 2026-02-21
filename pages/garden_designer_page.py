import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont

# ── Emoji map ─────────────────────────────────────────────────────
VEGETABLE_EMOJI = {
    "tomato": "🍅", "carrot": "🥕", "spinach": "🥬", "eggplant": "🍆",
    "pepper": "🫑", "lettuce": "🥗", "cucumber": "🥒", "potato": "🥔",
    "onion": "🧅", "garlic": "🧄", "corn": "🌽", "broccoli": "🥦",
    "cabbage": "🥬", "pumpkin": "🎃", "radish": "🌱", "beans": "🫘",
    "peas": "🌿", "chili": "🌶️", "ginger": "🫚", "sweet potato": "🍠",
    "kangkong": "🥬", "ampalaya": "🌿", "okra": "🌿", "sitaw": "🫘",
    "pechay": "🥬", "kamote": "🍠", "malunggay": "🌿", "talong": "🍆",
    "sibuyas": "🧅", "bawang": "🧄", "luya": "🫚", "sili": "🌶️",
    "patola": "🌿", "upo": "🌿", "kalabasa": "🎃", "sayote": "🌿",
    "bataw": "🫘", "mungo": "🫘", "mais": "🌽", "kamatis": "🍅",
}

TILE_COLORS = [
    "#4a7c59", "#c0392b", "#e67e22", "#8e44ad",
    "#16a085", "#2980b9", "#f39c12", "#6d4c41",
]

def veg_emoji(name: str) -> str:
    name_lower = name.lower().strip()
    # Try exact match first
    if name_lower in VEGETABLE_EMOJI:
        return VEGETABLE_EMOJI[name_lower]
    # Fall back to partial match
    for key, emoji in VEGETABLE_EMOJI.items():
        if key in name_lower:
            return emoji
    return "🌱"

def veg_color(index: int) -> str:
    return TILE_COLORS[index % len(TILE_COLORS)]


# ── Build vegetable list from session state ───────────────────────
def get_vegetables() -> list[dict]:
    research = st.session_state.get("research_output")
    vegs = []

    if research and hasattr(research, "vegetable_recommendations"):
        vegs = [
            {
                "name":   v.vegetable,
                "emoji":  veg_emoji(v.vegetable),
                "color":  veg_color(i),
                "reason": v.reason,
            }
            for i, v in enumerate(research.vegetable_recommendations)
        ]

    # Append any user-added vegetables
    extra = st.session_state.get("extra_vegetables", [])
    for i, name in enumerate(extra):
        vegs.append({
            "name":   name,
            "emoji":  veg_emoji(name),
            "color":  veg_color(len(vegs) + i),
            "reason": "Added by you",
        })

    if not vegs:
        # Fallback demo data
        return [
            {"name": "Tomato",  "emoji": "🍅", "color": "#c0392b", "reason": "Thrives in warm climates"},
            {"name": "Spinach", "emoji": "🥬", "color": "#4a7c59", "reason": "Great for shaded spots"},
            {"name": "Carrot",  "emoji": "🥕", "color": "#e67e22", "reason": "Easy in loose soil"},
        ]

    return vegs



# ── Inject CSS ────────────────────────────────────────────────────
def inject_styles(vegetables: list[dict]):
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

        /* Hide Streamlit sidebar nav */
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }

                
        .garden-title {
            font-family: 'Playfair Display', serif;
            font-size: 2rem; color: #fdf6ec; margin-bottom: 0;
        }
        .garden-title span { color: #8bc34a; }
        .garden-sub {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.85rem; color: rgba(253,246,236,0.45);
            margin-bottom: 20px; font-weight: 300;
        }
        .legend-chip {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 3px 10px; border-radius: 20px;
            font-size: 0.75rem; font-family: 'DM Sans', sans-serif;
            color: white; margin: 2px;
        }
        .grid-label {
            color: rgba(253,246,236,0.35); font-size: 0.7rem;
            letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 12px;
        }
        .counter { color: rgba(253,246,236,0.5); font-size: 0.8rem; }
        .size-display {
            text-align: center; margin: 6px 0;
            color: #fdf6ec; font-weight: 500; font-size: 1rem;
        }

        </style>
    """, unsafe_allow_html=True)


# ── Render a single cell button with inline color ─────────────────
def cell_button(label: str, key: str, color: str | None = None) -> bool:
    """Render a styled plot button. Returns True if clicked."""
    if color:
        r, g, b = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        bg = f"rgba({r},{g},{b},0.75)"
        border = color
        text = "rgba(255,255,255,0.95)"
    else:
        bg = "rgba(61,38,16,0.8)"
        border = "rgba(255,255,255,0.15)"
        text = "rgba(253,246,236,0.3)"

    st.markdown(f"""
        <style>
        div[data-testid="stButton"] > button[kind="secondary"]#btn_{key} {{
            background: {bg} !important;
            border: 2px {"solid" if color else "dashed"} {border} !important;
            color: {text} !important;
            height: 80px !important;
            border-radius: 10px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.82rem !important;
            width: 100% !important;
            white-space: pre-wrap !important;
            line-height: 1.4 !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    return st.button(label, key=key, use_container_width=True)



# ── Render garden grid as PNG ─────────────────────────────────────
def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def render_grid_as_png(garden_grid: dict, rows: int, cols: int) -> bytes:
    CELL = 120       # px per cell
    PADDING = 20     # outer padding
    GAP = 8          # gap between cells
    HEADER = 50      # space for title

    W = PADDING * 2 + cols * CELL + (cols - 1) * GAP
    H = PADDING * 2 + HEADER + rows * CELL + (rows - 1) * GAP

    img = Image.new("RGBA", (W, H), (44, 26, 14, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Title
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        cell_font  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    except Exception:
        title_font = ImageFont.load_default()
        cell_font  = ImageFont.load_default()

    draw.text((PADDING, PADDING), "🌿 My Taniman Layout", fill=(253, 246, 236, 200), font=title_font)

    for r in range(rows):
        for c in range(cols):
            x0 = PADDING + c * (CELL + GAP)
            y0 = PADDING + HEADER + r * (CELL + GAP)
            x1, y1 = x0 + CELL, y0 + CELL

            cell_key = f"{r}_{c}"
            planted_veg = garden_grid.get(cell_key)

            if planted_veg:
                rv, gv, bv = hex_to_rgb(planted_veg["color"])
                fill = (rv, gv, bv, 200)
                outline = (rv, gv, bv, 255)
            else:
                fill = (61, 38, 16, 180)
                outline = (253, 246, 236, 40)

            # Rounded rect via multiple draws (PIL doesn't support radius in older versions)
            draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=fill, outline=outline, width=2)

            if planted_veg:
                short_name = planted_veg["name"].split("(")[0].strip()
                # Wrap long names
                words = short_name.split()
                lines = []
                line = ""
                for word in words:
                    test = f"{line} {word}".strip()
                    bbox = draw.textbbox((0, 0), test, font=cell_font)
                    if bbox[2] - bbox[0] > CELL - 12:
                        if line:
                            lines.append(line)
                        line = word
                    else:
                        line = test
                if line:
                    lines.append(line)

                total_h = len(lines) * 16
                text_y = y0 + (CELL - total_h) // 2
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=cell_font)
                    tw = bbox[2] - bbox[0]
                    draw.text((x0 + (CELL - tw) // 2, text_y), line, fill=(255, 255, 255, 230), font=cell_font)
                    text_y += 16
            else:
                label = f"{r+1},{c+1}"
                bbox = draw.textbbox((0, 0), label, font=cell_font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text(
                    (x0 + (CELL - tw) // 2, y0 + (CELL - th) // 2),
                    label, fill=(253, 246, 236, 60), font=cell_font
                )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Page ──────────────────────────────────────────────────────────
def garden_designer_page():
    st.set_page_config(page_title="🌿 Taniman Designer", page_icon="🌿", layout="wide")

    if not st.session_state.get("research_done"):
        st.warning("Please complete the vegetable research step first.")
        st.page_link("main.py", label="← Back to Home", icon="🏠")
        return

    # ── Session state ─────────────────────────────────────────────
    if "selected_veg" not in st.session_state:
        st.session_state.selected_veg = None
    if "grid_rows" not in st.session_state:
        st.session_state.grid_rows = 4
    if "grid_cols" not in st.session_state:
        st.session_state.grid_cols = 4
    if "garden_grid" not in st.session_state:
        st.session_state.garden_grid = {}  # "row_col" → veg dict

    vegetables = get_vegetables()
    inject_styles(vegetables)

    if not st.session_state.selected_veg:
        st.session_state.selected_veg = vegetables[0]["name"]

    rows = st.session_state.grid_rows
    cols = st.session_state.grid_cols

    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
        <p class="garden-title">🌿 <span> Garden Designer</span></p>
        <p class="garden-sub">Pick a vegetable · Click a plot to plant it · Click a planted plot to clear it</p>
    """, unsafe_allow_html=True)

    # ── 1. Grid size controls ─────────────────────────────────────
    st.markdown("**📐 Garden Size**")
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:nowrap; margin-bottom:8px;">
            <span style="font-size:0.78rem; color:#555; min-width:32px;">Rows</span>
            <span style="font-size:1rem; font-weight:600; min-width:20px; text-align:center;">{rows}</span>
            <span style="font-size:0.78rem; color:#555; margin-left:12px; min-width:52px;">Columns</span>
            <span style="font-size:1rem; font-weight:600; min-width:20px; text-align:center;">{cols}</span>
        </div>
    """, unsafe_allow_html=True)

    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        if st.button("▼ Row", key="row_minus", use_container_width=True):
            if rows > 1:
                st.session_state.garden_grid = {
                    k: v for k, v in st.session_state.garden_grid.items()
                    if int(k.split("_")[0]) < rows - 1
                }
                st.session_state.grid_rows -= 1
                st.rerun()
    with rc2:
        if st.button("▲ Row", key="row_plus", use_container_width=True):
            if rows < 8:
                st.session_state.grid_rows += 1
                st.rerun()
    with rc3:
        if st.button("▼ Col", key="col_minus", use_container_width=True):
            if cols > 1:
                st.session_state.garden_grid = {
                    k: v for k, v in st.session_state.garden_grid.items()
                    if int(k.split("_")[1]) < cols - 1
                }
                st.session_state.grid_cols -= 1
                st.rerun()
    with rc4:
        if st.button("▲ Col", key="col_plus", use_container_width=True):
            if cols < 8:
                st.session_state.grid_cols += 1
                st.rerun()

    st.divider()

    # ── 2. Vegetable toolbar — horizontal buttons ─────────────────
    st.markdown("**🥬🍅🥕 Vegetables**")
    all_vegs = vegetables + [{"name": "__erase__", "emoji": "🧹", "color": None}]
    veg_cols = st.columns(len(all_vegs))
    for i, veg in enumerate(all_vegs):
        with veg_cols[i]:
            is_selected = veg["name"] == st.session_state.selected_veg
            label = f"{'✅' if is_selected else ''}{veg['emoji']}"
            if st.button(label, key=f"sel_{veg['name']}", use_container_width=True,
                         type="primary" if is_selected else "secondary"):
                st.session_state.selected_veg = veg["name"]
                st.rerun()

    # Show selected label as caption
    if st.session_state.selected_veg == "__erase__":
        st.caption("🧹 Eraser — click a planted plot to clear it")
    else:
        sel = next((v for v in vegetables if v["name"] == st.session_state.selected_veg), None)
        if sel:
            st.caption(f"Selected: **{sel['emoji']} {sel['name']}**")

    st.divider()

    # ── 3. Garden grid — full width ───────────────────────────────
    st.markdown(f'<p class="grid-label">Garden Bed · {rows} × {cols}</p>', unsafe_allow_html=True)

    # Target only grid rows (skip size controls row + veggie toolbar row)
    # Grid stHorizontalBlocks start at index 3 (1=size controls, 2=veggie toolbar, 3+=grid)
    st.markdown(f"""
        <style>
        [data-testid="stHorizontalBlock"]{{
            gap: 4px !important;
            flex-wrap: nowrap !important;
            width: 50vw;
        }}
        </style>
    """, unsafe_allow_html=True)

    for r in range(rows):
        grid_cols = st.columns(cols, gap="small")
        for c in range(cols):
            cell_key = f"{r}_{c}"
            planted_veg = st.session_state.garden_grid.get(cell_key)
            with grid_cols[c]:
                if planted_veg:
                    color = planted_veg["color"]
                    rv, gv, bv = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
                    short_name = planted_veg['name'].split('(')[0].strip()
                    st.markdown(f"""
                        <style>
                        div[data-testid="stButton"]:has(button[kind="secondary"][data-testid="baseButton-secondary"]#btn_cell_{cell_key}) button {{
                            background: rgba({rv},{gv},{bv},0.8) !important;
                            border: 2px solid {color} !important;
                            color: white !important;
                        }}
                        </style>
                    """, unsafe_allow_html=True)
                    if st.button(f"{planted_veg['emoji']}\n{short_name}\n✕", key=f"cell_{cell_key}", use_container_width=True):
                        selected = st.session_state.selected_veg
                        if selected == "__erase__" or planted_veg["name"] == selected:
                            st.session_state.garden_grid.pop(cell_key, None)
                        else:
                            veg = next((v for v in vegetables if v["name"] == selected), None)
                            if veg:
                                st.session_state.garden_grid[cell_key] = veg
                        st.rerun()
                else:
                    if st.button(f"＋\n{r+1},{c+1}", key=f"cell_{cell_key}", use_container_width=True):
                        selected = st.session_state.selected_veg
                        if selected and selected != "__erase__":
                            veg = next((v for v in vegetables if v["name"] == selected), None)
                            if veg:
                                st.session_state.garden_grid[cell_key] = veg
                            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear garden", use_container_width=False):
        st.session_state.garden_grid = {}
        st.rerun()


    # ── Export + Continue ─────────────────────────────────────────
    st.divider()
    col_export, col_spacer, col_continue = st.columns([2, 1, 1])

    with col_export:
        if st.session_state.garden_grid:
            png_bytes = render_grid_as_png(
                st.session_state.garden_grid,
                st.session_state.grid_rows,
                st.session_state.grid_cols,
            )
            st.download_button(
                label="📤 Export layout as PNG",
                data=png_bytes,
                file_name="my-taniman-layout.png",
                mime="image/png",
            )

    with col_continue:
        if st.button("Continue to Schedule →", use_container_width=True, type="primary"):
            st.session_state.garden_design_done = True
            st.session_state.garden_layout = st.session_state.garden_grid
            st.session_state.awaiting_confirmation = True
            st.session_state.awaiting_garden_design = False
            st.switch_page("main.py")

if __name__ == "__main__":
    garden_designer_page()