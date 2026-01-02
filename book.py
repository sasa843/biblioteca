import streamlit as st
import pandas as pd
import base64
import os
import requests

# =====================
# ---- CONFIG ----
# =====================
st.set_page_config(
    page_title="Saswata’s Library",
    layout="wide"
)

# =====================
# ---- THEME-AWARE BACKGROUND ----
# =====================
def set_background(image_path,
                   overlay_light='rgba(255,255,255,0.60)',
                   overlay_dark='rgba(0,0,0,0.45)'):

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
            .stApp {{
                background-image:
                    linear-gradient({overlay}, {overlay}),
                    url("data:image/png;base64,{b64}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}

            .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

set_background("assets/background.jpg")

# =====================
# ---- LOAD DATA ----
# =====================
@st.cache_data
def load_data(path):
    df = pd.read_excel(path).fillna("")

    required = [
        "Book Name",
        "Book Name (Original Language)",
        "Author",
        "Publisher",
        "Price",
        "Fiction / Non-Fiction",
        "Genre",
        "Format",
        "ISBN",
        "Front Cover",
        "Back Cover"
    ]

    for col in required:
        if col not in df.columns:
            df[col] = ""

    return df

df = load_data("Book_Database.xlsx")

# Normalize price
df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)

# Clean ISBN (remove hyphens, spaces, text)
df["ISBN"] = (
    df["ISBN"]
    .astype(str)
    .str.replace(r"[^0-9Xx]", "", regex=True)
)

# =====================
# ---- HEADER ----
# =====================
st.markdown("<h1 style='text-align:center;'>📚 Saswata’s Library</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>A Clean, Cinematic, Modern Book Catalog</p>", unsafe_allow_html=True)
st.write("---")

# =====================
# ---- FILTERS ----
# =====================
with st.expander("🔍 Search & Filters", expanded=True):
    c1, c2, c3, c4 = st.columns(4)

    book_name = c1.text_input("Book Name")
    author = c2.text_input("Author")
    genre = c3.text_input("Genre")
    publisher = c4.text_input("Publisher")

    fiction_vals = sorted({v for v in df["Fiction / Non-Fiction"].astype(str) if v})
    format_vals = sorted({v for v in df["Format"].astype(str) if v})

    fiction_type = st.selectbox("Fiction / Non-Fiction", ["All"] + fiction_vals)
    format_type = st.selectbox("Format", ["All"] + format_vals)

    min_price = int(df["Price"].min())
    max_price = int(df["Price"].max())

    price_range = st.slider(
        "💰 Price Range (₹)",
        min_price,
        max_price,
        (min_price, max_price)
    )

# =====================
# ---- SORTING ----
# =====================
st.write("### 🔀 Sort Options")

s1, s2 = st.columns([3, 1])

sort_by = s1.selectbox(
    "Sort by",
    ["Book Name", "Author", "Genre", "Price"]
)

sort_order = s2.radio(
    "Order",
    ["Ascending", "Descending"],
    horizontal=True
)

# =====================
# ---- APPLY FILTERS ----
# =====================
filtered_df = df.copy()

def contains_ci(series, text):
    return series.astype(str).str.contains(text, case=False, na=False)

if book_name:
    filtered_df = filtered_df[contains_ci(filtered_df["Book Name"], book_name)]

if author:
    filtered_df = filtered_df[contains_ci(filtered_df["Author"], author)]

if genre:
    filtered_df = filtered_df[contains_ci(filtered_df["Genre"], genre)]

if publisher:
    filtered_df = filtered_df[contains_ci(filtered_df["Publisher"], publisher)]

if fiction_type != "All":
    filtered_df = filtered_df[filtered_df["Fiction / Non-Fiction"] == fiction_type]

if format_type != "All":
    filtered_df = filtered_df[filtered_df["Format"] == format_type]

filtered_df = filtered_df[
    filtered_df["Price"].between(price_range[0], price_range[1])
]

filtered_df = filtered_df.sort_values(
    by=sort_by,
    ascending=(sort_order == "Ascending")
)

# =====================
# ---- ISBN COVER LOOKUP ----
# =====================
@st.cache_data(show_spinner=False)
def get_cover_from_isbn(isbn):
    if not isbn:
        return None
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and len(r.content) > 1000:
            return url
    except Exception:
        pass
    return None

def show_image(col, local_path, label, isbn):
    placeholder = "assets/no_cover.png"

    if local_path and os.path.exists(local_path):
        col.image(local_path, width=120, caption=label)
        return

    isbn_cover = get_cover_from_isbn(isbn)
    if isbn_cover:
        col.image(isbn_cover, width=120, caption=f"{label} (ISBN)")
        return

    if os.path.exists(placeholder):
        col.image(placeholder, width=120, caption=f"{label} (Not Available)")
    else:
        col.markdown(f"**{label}:** _Not Available_")

# =====================
# ---- DISPLAY RESULTS ----
# =====================
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")

for _, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([2, 2, 2, 2])

        # --- Book info ---
        cols[0].markdown(f"**📕 Title:** {row['Book Name']}")

        orig = str(row.get("Book Name (Original Language)", "")).strip()
        if orig and orig != row["Book Name"]:
            cols[0].markdown(f"**🌍 Original:** {orig}")

        cols[0].markdown(f"**✍️ Author:** {row['Author']}")
        cols[0].markdown(f"**🏷 Genre:** {row['Genre']}")
        cols[0].markdown(f"**🏢 Publisher:** {row['Publisher']}")

        # --- Details ---
        cols[1].markdown(f"**📚 Type:** {row['Fiction / Non-Fiction']}")
        cols[1].markdown(f"**📦 Format:** {row['Format']}")
        cols[1].markdown(f"**💰 Price:** ₹{int(row['Price'])}")

        isbn = str(row.get("ISBN", "")).strip()

        front = str(row.get("Front Cover", "")).strip()
        back = str(row.get("Back Cover", "")).strip()

        if front.lower() == "insert image":
            front = ""
        if back.lower() == "insert image":
            back = ""

        show_image(cols[2], f"covers/{front}" if front else "", "Front Cover", isbn)
        show_image(cols[3], f"covers/{back}" if back else "", "Back Cover", isbn)

    st.markdown("---")
