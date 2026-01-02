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
def set_background(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient(rgba(255,255,255,0.6), rgba(255,255,255,0.6)),
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
    return pd.read_excel(path).fillna("")

df = load_data("Book_Database.xlsx")

df["Price"] = pd.to_numeric(df.get("Price", 0), errors="coerce").fillna(0)

# =====================
# ---- HEADER ----
# =====================
st.markdown("<h1 style='text-align:center;'>📚 Saswata’s Library</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>A simple, visual book catalog</p>", unsafe_allow_html=True)
st.write("---")

# =====================
# ---- FILTERS ----
# =====================
with st.expander("🔍 Search & Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    title_q = c1.text_input("Book Name")
    author_q = c2.text_input("Author")
    genre_q = c3.text_input("Genre")

# =====================
# ---- SORTING ----
# =====================
s1, s2 = st.columns([3, 1])

sort_by = s1.selectbox(
    "Sort by",
    ["Book Name", "Author", "Price"]
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

def contains(series, val):
    return series.astype(str).str.contains(val, case=False, na=False)

if title_q:
    filtered_df = filtered_df[contains(filtered_df["Book Name"], title_q)]
if author_q:
    filtered_df = filtered_df[contains(filtered_df["Author"], author_q)]
if genre_q:
    filtered_df = filtered_df[contains(filtered_df["Genre"], genre_q)]

filtered_df = filtered_df.sort_values(
    sort_by,
    ascending=(sort_order == "Ascending")
)

# =====================
# ---- CARD STYLES ----
# =====================
st.markdown(
    """
    <style>
    .book-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .cover-box {
        height: 180px;
        border-radius: 8px;
        background: #f2f2f2;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #999;
        font-size: 14px;
        margin-bottom: 12px;
    }
    .title {
        font-weight: 700;
        margin-bottom: 6px;
    }
    .meta {
        font-size: 14px;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================
# ---- DISPLAY GRID ----
# =====================
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")

cols_per_row = 4
rows = [filtered_df[i:i+cols_per_row] for i in range(0, len(filtered_df), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for col, (_, book) in zip(cols, row.iterrows()):
        with col:
            st.markdown(
                f"""
                <div class="book-card">
                    <div class="cover-box">
                        No Cover
                    </div>
                    <div class="title">📕 {book['Book Name']}</div>
                    <div class="meta">✍️ {book['Author']}</div>
                    <div class="meta">🏷 {book['Genre']}</div>
                    <div class="meta">🏢 {book['Publisher']}</div>
                    <div class="meta">📦 {book['Format']}</div>
                    <div class="meta">💰 ₹{int(book['Price'])}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
