import streamlit as st
import pandas as pd
import os

# --------- PAGE SETUP ---------
st.set_page_config(page_title="Saswata’s Library", layout="wide")

st.markdown("""
    <style>
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: -30px;
    }
    .title-text {
        font-family: 'Georgia', serif;
        font-size: 40px;
        color: #3a3a3a;
    }
    .subtitle {
        font-size: 16px;
        color: #777;
    }
    .book-card {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
        background-color: #fff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='title-container'><div><h1 class='title-text'>📚 Saswata’s Library</h1><p class='subtitle'>A Clean & Cinematic Modern Book Library</p></div></div>", unsafe_allow_html=True)

# --------- LOAD DATA ---------
EXCEL_PATH = "Book_Database.xlsx"
COVER_FOLDER = "covers"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(EXCEL_PATH)

# Fill NaNs to avoid key errors
df.fillna("", inplace=True)

# --------- SEARCH & FILTER ---------
st.divider()
st.subheader("🔍 Search & Filter Books")

col1, col2, col3, col4 = st.columns(4)

name_query = col1.text_input("Book Name or Author")
genre_filter = col2.selectbox("Filter by Genre", ["All"] + sorted(df['Genre'].unique()))
format_filter = col3.selectbox("Format", ["All"] + sorted(df['Format'].unique()))
fiction_filter = col4.selectbox("Fiction / Non-Fiction", ["All"] + sorted(df['Fiction / Non-Fiction'].unique()))

# Filter logic
filtered_df = df.copy()

if name_query:
    name_query_lower = name_query.lower()
    filtered_df = filtered_df[
        filtered_df['Book Name'].str.lower().str.contains(name_query_lower) |
        filtered_df['Author'].str.lower().str.contains(name_query_lower)
    ]

if genre_filter != "All":
    filtered_df = filtered_df[filtered_df['Genre'] == genre_filter]

if format_filter != "All":
    filtered_df = filtered_df[filtered_df['Format'] == format_filter]

if fiction_filter != "All":
    filtered_df = filtered_df[filtered_df['Fiction / Non-Fiction'] == fiction_filter]

# --------- DISPLAY BOOKS ---------
st.divider()
st.subheader("📘 Book Listings")

if filtered_df.empty:
    st.warning("No books found with the current filters.")
else:
    for i, row in filtered_df.iterrows():
        with st.container():
            cols = st.columns([1, 3])
            # Front cover image
            cover_path = os.path.join(COVER_FOLDER, str(row['Front Cover']))
            if row['Front Cover'] and os.path.exists(cover_path):
                cols[0].image(cover_path, width=150)
            else:
                cols[0].image("https://via.placeholder.com/150x220?text=No+Cover", width=150)

            # Book details
            with cols[1]:
                st.markdown(f"### {row['Book Name']}")
                st.markdown(f"**Original Name:** {row.get('Book Name (Original Language)', 'N/A')}")
                st.markdown(f"**Author:** {row['Author']} &nbsp;&nbsp; | &nbsp;&nbsp; **Publisher:** {row['Publisher']}")
                st.markdown(f"**Genre:** {row['Genre']} | **Format:** {row['Format']} | **Price:** ₹{row['Price']}")
                st.markdown(f"**Fiction / Non-Fiction:** {row['Fiction / Non-Fiction']}")
                if row['Back Cover']:
                    back_path = os.path.join(COVER_FOLDER, str(row['Back Cover']))
                    if os.path.exists(back_path):
                        st.markdown(f"🖼️ *Back cover available*")

# Optional genre count
if st.checkbox("📊 Show Genre Stats"):
    genre_stats = df['Genre'].value_counts()
    st.bar_chart(genre_stats)
