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
# ---- BACKGROUND ----
# =====================
def set_background(
    image_path,
    overlay_light="rgba(255,255,255,0.60)",
    overlay_dark="rgba(0,0,0,0.45)"
):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient({overlay_light}, {overlay_light}),
                    url("data:image/png;base64,{b64}");
                background-size: cover;
                background-attachment: fixed;
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
    if "ISBN" not in df.columns:
        df["ISBN"] = ""
    return df

df = load_data("Book_Database.xlsx")

df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
df["ISBN"] = df["ISBN"].astype(str).str.replace(r"[^0-9Xx]", "", regex=True)

# =====================
# ---- HEADER ----
# =====================
st.markdown("<h1 style='text-align:center;'>📚 Saswata’s Library</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Simple. Clean. Personal.</p>", unsafe_allow_html=True)
st.write("---")

# =====================
# ---- FILTERS ----
# =====================
with st.expander("🔍 Search & Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    book_name = c1.text_input("Book Name")
    author = c2.text_input("Author")
    genre = c3.text_input("Genre")

# =====================
# ---- SORTING ----
# =====================
sort_by, order = st.columns([3, 1])

sort_col = sort_by.selectbox(
    "Sort by",
    ["Book Name", "Author", "Price"]
)

sort_order = order.radio(
    "Order",
    ["Ascending", "Descending"],
    horizontal=True
)

# =====================
# ---- APPLY FILTERS ----
# =====================
filtered_df = df.copy()

def contains(series, value):
    return series.astype(str).str.contains(value, case=False, na=False)

if book_name:
    filtered_df = filtered_df[contains(filtered_df["Book Name"], book_name)]
if author:
    filtered_df = filtered_df[contains(filtered_df["Author"], author)]
if genre:
    filtered_df = filtered_df[contains(filtered_df["Genre"], genre)]

filtered_df = filtered_df.sort_values(
    sort_col,
    ascending=(sort_order == "Ascending")
)

# =====================
# ---- COVER DISPLAY (GOOGLE BOOKS ONLY)
# =====================
def show_cover(col, isbn):
    if not isbn:
        col.markdown("**No Cover**")
        return

    google_thumb = (
        "https://books.google.com/books/content"
        f"?vid=ISBN{isbn}&printsec=frontcover&img=1&zoom=0"
    )

    col.markdown(
        f"""
        <img src="{google_thumb}"
             width="120"
             style="display:block; margin:auto;" />
        """,
        unsafe_allow_html=True
    )

# =====================
# ---- DISPLAY BOOKS ----
# =====================
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")

for _, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([3, 2, 1])

        # Book info
        cols[0].markdown(f"**📕 Title:** {row['Book Name']}")
        cols[0].markdown(f"**✍️ Author:** {row['Author']}")
        cols[0].markdown(f"**🏷 Genre:** {row['Genre']}")
        cols[0].markdown(f"**🏢 Publisher:** {row['Publisher']}")

        cols[1].markdown(f"**📦 Format:** {row['Format']}")
        cols[1].markdown(f"**💰 Price:** ₹{int(row['Price'])}")

        # Cover
        show_cover(cols[2], row["ISBN"])

    st.markdown("---")
