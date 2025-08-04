import streamlit as st
import pandas as pd
from pathlib import Path

# ---------- Config ----------
st.set_page_config(page_title="📚 My Book Library", layout="wide")
st.title("📚 My Book Library")

# ---------- Load Excel ----------
EXCEL_FILE = "Book_Database_With_Samples_And_Format.xlsx"
COVER_FOLDER = "covers"

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE)

df = load_data()

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.header("🔍 Filter Books")

    book_name = st.text_input("Book Name")
    original_name = st.text_input("Original Language Name")
    author = st.text_input("Author")
    publisher = st.text_input("Publisher")
    min_price = st.number_input("Min Price", min_value=0, value=0)
    max_price = st.number_input("Max Price", min_value=0, value=10000)
    format_choice = st.multiselect("Format", df["Format"].dropna().unique())
    genre_choice = st.multiselect("Genre", df["Genre"].dropna().unique())
    fiction_choice = st.multiselect("Fiction / Non-Fiction", df["Fiction / Non-Fiction"].dropna().unique())

# ---------- Filter Logic ----------
filtered_df = df.copy()

if book_name:
    filtered_df = filtered_df[filtered_df["Book Name"].str.contains(book_name, case=False, na=False)]
if original_name:
    filtered_df = filtered_df[filtered_df["Book Name (Original Language)"].str.contains(original_name, case=False, na=False)]
if author:
    filtered_df = filtered_df[filtered_df["Author"].str.contains(author, case=False, na=False)]
if publisher:
    filtered_df = filtered_df[filtered_df["Publisher"].str.contains(publisher, case=False, na=False)]

filtered_df = filtered_df[(filtered_df["Price"] >= min_price) & (filtered_df["Price"] <= max_price)]

if format_choice:
    filtered_df = filtered_df[filtered_df["Format"].isin(format_choice)]
if genre_choice:
    filtered_df = filtered_df[filtered_df["Genre"].isin(genre_choice)]
if fiction_choice:
    filtered_df = filtered_df[filtered_df["Fiction / Non-Fiction"].isin(fiction_choice)]

# ---------- Display Helper ----------
def display_image(path, caption):
    if Path(path).is_file():
        st.image(path, caption=caption, width=150)
    else:
        st.markdown(f"**{caption}:** ❌ Not Found")

# ---------- Display Results ----------
if filtered_df.empty:
    st.warning("No books found with selected criteria.")
else:
    for _, row in filtered_df.iterrows():
        with st.container():
            cols = st.columns([1, 2, 2])

            # Front Cover
            front_img = Path(COVER_FOLDER) / str(row['Front Cover']) if pd.notna(row['Front Cover']) else None
            display_image(front_img, "Front Cover")

            # Book Info
            cols[1].markdown(f"### {row['Book Name']}")
            cols[1].markdown(f"**Original Name:** {row['Book Name (Original Language)']}")
            cols[1].markdown(f"**Author:** {row['Author']}")
            cols[1].markdown(f"**Publisher:** {row['Publisher']}")
            cols[1].markdown(f"**Price:** ₹{row['Price']}")
            cols[1].markdown(f"**Format:** {row['Format']}")
            cols[1].markdown(f"**Fiction / Non-Fiction:** {row['Fiction / Non-Fiction']}")
            cols[1].markdown(f"**Genre:** {row['Genre']}")

            # Back Cover
            back_img = Path(COVER_FOLDER) / str(row['Back Cover']) if pd.notna(row['Back Cover']) else None
            display_image(back_img, "Back Cover")

            st.markdown("---")
