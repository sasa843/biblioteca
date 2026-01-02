import streamlit as st
import pandas as pd
import base64
import os

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
def set_background(
    image_path,
    overlay_light="rgba(255,255,255,0.60)",
    overlay_dark="rgba(0,0,0,0.45)"
):
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

df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
df["ISBN"] = df["ISBN"].astype(str).str.replace(r"[^0-9Xx]", "", regex=True)

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

    price_range = st.slider("💰 Price Range (₹)", min_price, max_price, (min_price, max_price))

# =====================
# ---- SORTING (FIXED)
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

filtered_df = filtered_df[filtered_df["Price"].between(price_range[0], price_range[1])]
filtered_df = filtered_df.sort_values(sort_by, ascending=(sort_order == "Ascending"))

# =====================
# ---- IMAGE DISPLAY (HTML FALLBACK)
# =====================
def show_image(col, local_path, label, isbn):
    if local_path and os.path.exists(local_path):
        col.image(local_path, width=120, caption=label)
        return

    if not isbn:
        col.image("assets/no_cover.png", width=120, caption="Not Available")
        return

    openlib = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    google = f"https://books.google.com/books/content?vid=ISBN{isbn}&printsec=frontcover&img=1&zoom=1"

    col.markdown(
        f"""
        <img src="{openlib}" width="120"
             onerror="this.onerror=null;this.src='{google}';" />
        <div style="font-size:12px;text-align:center;">{label}</div>
        """,
        unsafe_allow_html=True
    )

# =====================
# ---- DISPLAY RESULTS ----
# =====================
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")

for _, row in filtered_df.iterrows():
    cols = st.columns([2, 2, 2, 2])

    cols[0].markdown(f"**📕 Title:** {row['Book Name']}")
    cols[0].markdown(f"**✍️ Author:** {row['Author']}")
    cols[0].markdown(f"**🏷 Genre:** {row['Genre']}")
    cols[0].markdown(f"**🏢 Publisher:** {row['Publisher']}")

    cols[1].markdown(f"**📚 Type:** {row['Fiction / Non-Fiction']}")
    cols[1].markdown(f"**📦 Format:** {row['Format']}")
    cols[1].markdown(f"**💰 Price:** ₹{int(row['Price'])}")

    show_image(cols[2], "", "Front Cover", row["ISBN"])
    show_image(cols[3], "", "Back Cover", row["ISBN"])

    st.markdown("---")
