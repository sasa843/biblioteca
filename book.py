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
                    linear-gradient(rgba(255, 248, 229, 0.78), rgba(255, 253, 242, 0.78)),
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
# NORMALIZE FICTION COLUMN
# =====================
fiction_column = None
for col in df.columns:
    clean = col.strip().lower().replace("-", "").replace(" ", "").replace("/", "")
    if clean in ["fictionnonfiction", "fictionornonfiction", "fictionnonfictiontype"]:
        fiction_column = col
        break

if fiction_column:
    df["FictionType"] = df[fiction_column].astype(str).fillna("")
else:
    df["FictionType"] = ""

# =====================
# HEADER
# =====================
st.markdown("<h1 class='app-title'>📚 Saswata's Library</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Personal Book Collection</p>", unsafe_allow_html=True)
st.write("---")

# =====================
# FILTERS
# =====================
with st.expander("🔍 Search & Filters", expanded=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    title_q = c1.text_input("Book Name")
    author_q = c2.text_input("Author")
    genre_q = c3.text_input("Genre")
    language_q = c4.text_input("Language")
    fiction_q = c5.text_input("Fiction / Non-Fiction")

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

if language_q and "Language" in filtered_df.columns:
    filtered_df = filtered_df[contains(filtered_df["Language"], language_q)]

if fiction_q and "FictionType" in filtered_df.columns:
    filtered_df = filtered_df[contains(filtered_df["FictionType"], fiction_q)]

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
    :root {
        --ink: #1f2a37;
        --muted: #475467;
        --accent: #9a3412;
        --card-bg: rgba(255, 255, 255, 0.92);
        --card-border: rgba(190, 160, 110, 0.35);
    }
    .stApp, .stMarkdown, .stText, p, label, span, div {
        color: var(--ink);
    }
    .block-container {
        padding-top: 1.1rem;
    }
    .app-title {
        text-align: center;
        color: #0f172a;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        text-align: center;
        color: var(--muted);
        font-size: 1rem;
        margin-top: 0;
        margin-bottom: 0.6rem;
    }
    .result-count {
        color: #111827;
        font-size: 2rem;
        font-weight: 800;
        margin: 0.2rem 0 1rem 0;
    }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(190, 160, 110, 0.35);
        border-radius: 14px;
        backdrop-filter: blur(6px);
    }
    .book-card {
        background: var(--card-bg);
        border-radius: 14px;
        padding: 0;
        overflow: hidden;
        border: 1px solid var(--card-border);
        box-shadow: 0 8px 24px rgba(59, 42, 18, 0.14);
        height: 100%;
    }
    .cover-box {
        height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 0;
        background: linear-gradient(160deg, #eef2f7, #e2e8f0);
    }
    .book-info {
        padding: 12px 14px 14px 14px;
    }
    .title {
        font-weight: 700;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 6px;
    }
    .meta {
        font-size: 14px;
        color: var(--muted);
        margin-bottom: 4px;
    }
    .book-card .meta:last-child {
        color: var(--accent);
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================
# DISPLAY GRID
# =====================
st.markdown(f"<div class='result-count'>📖 Found {len(filtered_df)} Book(s)</div>", unsafe_allow_html=True)

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

                st.markdown('<div class="book-info">', unsafe_allow_html=True)
                st.markdown(f'<div class="title">📕 {book.get("Book Name","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">✍️ {book.get("Author","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">🏷 {book.get("Genre","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">📚 {book.get("FictionType","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">🌐 {book.get("Language","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">🏢 {book.get("Publisher","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">📦 {book.get("Format","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">💰 ₹{int(book["Price"])}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
