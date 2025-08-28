import streamlit as st
import pandas as pd
import base64
import os

# =====================
# ---- CONFIG ----
# =====================
st.set_page_config(page_title="Saswata’s Library", layout="wide")

# =====================
# ---- THEME-AWARE BACKGROUND ----
# =====================
def set_background(image_path, overlay_light='rgba(255,255,255,0.60)', overlay_dark='rgba(0,0,0,0.45)'):
    """
    Adds a background image with a semi-transparent overlay.
    Overlay adapts to Streamlit theme (light/dark) without forcing text colors.
    """
    # Detect theme type on recent Streamlit versions; fall back to 'light'
    theme_type = "light"
    try:
        theme_type = getattr(getattr(st, "context", None), "theme", {}).get("type", "light")
    except Exception:
        pass

    overlay = overlay_dark if theme_type == "dark" else overlay_light

    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
              :root {{
                --app-bg: url("data:image/png;base64,{b64}");
              }}
              /* Only control background; don't force text color */
              .stApp {{
                background-image:
                  linear-gradient({overlay}, {overlay}),
                  var(--app-bg);
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
              }}
              /* Titles/subtitles inherit theme text colors */
              .app-title, .app-subtitle {{
                color: inherit;
              }}
              /* Subtle divider spacing */
              .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
              }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Set background (optional image)
set_background("assets/background.jpg")

# =====================
# ---- LOAD DATA ----
# =====================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path).fillna("")
    # Ensure required columns exist; add if missing to avoid KeyError
    required = [
        "Book Name", "Author", "Genre", "Publisher",
        "Fiction / Non-Fiction", "Format", "Price",
        "Front Cover", "Back Cover"
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    return df

df = load_data("Book_Database.xlsx")

# =====================
# ---- HEADER ----
# =====================
st.markdown("<h1 class='app-title' style='text-align:center;'>📚 Saswata’s Library</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle' style='text-align:center;'>A Clean, Cinematic, Modern Book Catalog</p>", unsafe_allow_html=True)
st.write("---")

# =====================
# ---- FILTERS ----
# =====================
with st.expander("🔍 Search & Filters", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    book_name = col1.text_input("Book Name")
    author = col2.text_input("Author")
    genre = col3.text_input("Genre")
    publisher = col4.text_input("Publisher")

    # Drop duplicates and empty strings for clean selectors
    fiction_vals = sorted({v for v in df["Fiction / Non-Fiction"].astype(str).tolist() if v.strip()})
    format_vals = sorted({v for v in df["Format"].astype(str).tolist() if v.strip()})

    fiction_type = st.selectbox("Fiction or Non-Fiction", ["All"] + fiction_vals, index=0)
    format_type = st.selectbox("Format", ["All"] + format_vals, index=0)

# =====================
# ---- APPLY FILTERS ----
# =====================
filtered_df = df.copy()

def contains_ci(series: pd.Series, text: str) -> pd.Series:
    # Case-insensitive substring with NA safety
    return series.astype(str).str.contains(text, case=False, na=False)

if book_name.strip():
    filtered_df = filtered_df[contains_ci(filtered_df["Book Name"], book_name.strip())]

if author.strip():
    filtered_df = filtered_df[contains_ci(filtered_df["Author"], author.strip())]

if genre.strip():
    filtered_df = filtered_df[contains_ci(filtered_df["Genre"], genre.strip())]

if publisher.strip():
    filtered_df = filtered_df[contains_ci(filtered_df["Publisher"], publisher.strip())]

if fiction_type != "All":
    filtered_df = filtered_df[filtered_df["Fiction / Non-Fiction"].astype(str) == fiction_type]

if format_type != "All":
    filtered_df = filtered_df[filtered_df["Format"].astype(str) == format_type]

# =====================
# ---- DISPLAY RESULTS ----
# =====================
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")

def show_image(col, image_path: str, label: str):
    """
    Display cover images with a fallback placeholder if available.
    Does not break on empty/missing paths.
    """
    placeholder = "assets/no_cover.png"
    img_path = image_path.strip() if image_path else ""
    if img_path and os.path.exists(img_path):
        col.image(img_path, width=120, caption=label)
    elif os.path.exists(placeholder):
        col.image(placeholder, width=120, caption=f"{label} (Not Available)")
    else:
        col.markdown(f"**{label}:** _Not Available_")

# Render each book as a neat row
for _, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([2, 2, 2, 2])

        # Book Info
        cols[0].markdown(f"**📕 Title:** {row['Book Name']}")
        cols[0].markdown(f"**✍️ Author:** {row['Author']}")
        cols[0].markdown(f"**🏷 Genre:** {row['Genre']}")
        cols[0].markdown(f"**🏢 Publisher:** {row['Publisher']}")

        # Details
        cols[1].markdown(f"**📚 Type:** {row['Fiction / Non-Fiction']}")
        cols[1].markdown(f"**💰 Price:** ₹{row['Price']}")
        cols[1].markdown(f"**📦 Format:** {row['Format']}")

        # Covers (relative to a 'covers/' folder)
        front = str(row.get("Front Cover", "")).strip()
        back = str(row.get("Back Cover", "")).strip()
        show_image(cols[2], f"covers/{front}" if front else "", "Front Cover")
        show_image(cols[3], f"covers/{back}" if back else "", "Back Cover")

    st.markdown("---")
