import streamlit as st
import pandas as pd
import base64
import os

# =====================
# CONFIG
# =====================
st.set_page_config(
    page_title="Saswata's Library",
    layout="wide"
)

# =====================
# BACKGROUND
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
# LOAD DATA
# =====================
@st.cache_data
def load_data(path):
    return pd.read_excel(path).fillna("")

df = load_data("Book_Database.xlsx")

# =====================
# NORMALIZE ISBN COLUMN
# =====================
isbn_column = None
for col in df.columns:
    clean = col.strip().lower().replace("-", "").replace(" ", "")
    if clean in ["isbn", "isbn13", "isbn10"]:
        isbn_column = col
        break

if isbn_column:
    df["ISBN"] = (
        df[isbn_column]
        .astype(str)
        .str.replace(r"[^0-9Xx]", "", regex=True)
    )
else:
    df["ISBN"] = ""

# =====================
# NORMALIZE PRICE
# =====================
df["Price"] = pd.to_numeric(df.get("Price", 0), errors="coerce").fillna(0)

# =====================
# HEADER
# =====================
st.markdown("<h1 style='text-align:center;'>📚 Saswata's Library</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Personal Book Collection</p>", unsafe_allow_html=True)
st.write("---")

# =====================
# FILTERS
# =====================
with st.expander("🔍 Search & Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    title_q = c1.text_input("Book Name")
    author_q = c2.text_input("Author")
    genre_q = c3.text_input("Genre")

# =====================
# SORTING
# =====================
valid_sort_columns = [c for c in ["Book Name", "Author", "Price"] if c in df.columns]

s1, s2 = st.columns([3, 1])
sort_by = s1.selectbox("Sort by", valid_sort_columns)
sort_order = s2.radio("Order", ["Ascending", "Descending"], horizontal=True)

# =====================
# APPLY FILTERS
# =====================
filtered_df = df.copy()

def contains(series, value):
    return series.astype(str).str.contains(value, case=False, na=False)

if title_q and "Book Name" in filtered_df.columns:
    filtered_df = filtered_df[contains(filtered_df["Book Name"], title_q)]

if author_q and "Author" in filtered_df.columns:
    filtered_df = filtered_df[contains(filtered_df["Author"], author_q)]

if genre_q and "Genre" in filtered_df.columns:
    filtered_df = filtered_df[contains(filtered_df["Genre"], genre_q)]

filtered_df = filtered_df.sort_values(
    sort_by,
    ascending=(sort_order == "Ascending")
)

# =====================
# COVER HANDLING (BASE64)
# =====================
def get_cover_base64(isbn):
    paths = []
    if isbn:
        paths += [f"covers/{isbn}.png", f"covers/{isbn}.jpg"]
    paths.append("covers/no_cover.png")

    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()

    return None

# =====================
# CARD STYLES
# =====================
st.markdown(
    """
    <style>
    .book-card {
        background: white;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        height: 100%;
    }
    .cover-box {
        height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 10px;
        background: #f5f5f5;
    }
    .title {
        font-weight: 700;
        margin-top: 10px;
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
# DISPLAY GRID
# =====================
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")

if filtered_df.empty:
    st.info("No books match your filters.")
else:
    cols_per_row = 4
    rows = [filtered_df[i:i + cols_per_row] for i in range(0, len(filtered_df), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, book) in zip(cols, row.iterrows()):
            with col:
                st.markdown('<div class="book-card">', unsafe_allow_html=True)

                cover_b64 = get_cover_base64(book.get("ISBN", ""))

                st.markdown(
                    f"""
                    <div class="cover-box">
                        <img src="data:image/png;base64,{cover_b64}"
                             style="max-height:220px; max-width:100%; object-fit:contain;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(f'<div class="title">📕 {book.get("Book Name","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">✍️ {book.get("Author","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">🏷 {book.get("Genre","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">🏢 {book.get("Publisher","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">📦 {book.get("Format","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">💰 ₹{int(book["Price"])}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
