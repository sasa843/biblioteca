import streamlit as st
import pandas as pd
import base64
import os

# ---- CONFIG ----
st.set_page_config(page_title="Saswata’s Library", layout="wide")

# ---- BACKGROUND IMAGE ----
def set_background(image_path):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background("assets/background.jpg")  # Change path if needed

# ---- LOAD DATA ----
@st.cache_data
def load_data(path):
    return pd.read_excel(path).fillna("")

df = load_data("Book_Database.xlsx")

# ---- HEADER ----
st.markdown("<h1 style='text-align: center;'>📚 Saswata’s Library</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>A Clean, Cinematic, Modern Book Catalog</p>", unsafe_allow_html=True)
st.write("---")

# ---- FILTERS ----
with st.expander("🔍 Search & Filters", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    book_name = col1.text_input("Book Name")
    author = col2.text_input("Author")
    genre = col3.text_input("Genre")
    publisher = col4.text_input("Publisher")

    fiction_type = st.selectbox("Fiction or Non-Fiction", ["All"] + sorted(df["Fiction / Non-Fiction"].unique()))
    format_type = st.selectbox("Format", ["All"] + sorted(df["Format"].unique()))

# ---- FILTERING ----
filtered_df = df.copy()

if book_name:
    filtered_df = filtered_df[filtered_df["Book Name"].str.contains(book_name, case=False)]

if author:
    filtered_df = filtered_df[filtered_df["Author"].str.contains(author, case=False)]

if genre:
    filtered_df = filtered_df[filtered_df["Genre"].str.contains(genre, case=False)]

if publisher:
    filtered_df = filtered_df[filtered_df["Publisher"].str.contains(publisher, case=False)]

if fiction_type != "All":
    filtered_df = filtered_df[filtered_df["Fiction / Non-Fiction"] == fiction_type]

if format_type != "All":
    filtered_df = filtered_df[filtered_df["Format"] == format_type]

# ---- DISPLAY TABLE ----
st.write(f"### 📖 Found {len(filtered_df)} Book(s)")
for idx, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([2, 2, 2, 2])

        # Basic Info
        cols[0].markdown(f"**📕 Title:** {row['Book Name']}")
        cols[0].markdown(f"**✍️ Author:** {row['Author']}")
        cols[0].markdown(f"**🏷 Genre:** {row['Genre']}")
        cols[0].markdown(f"**🏢 Publisher:** {row['Publisher']}")

        # Details
        cols[1].markdown(f"**📚 Type:** {row['Fiction / Non-Fiction']}")
        cols[1].markdown(f"**💰 Price:** ₹{row['Price']}")
        cols[1].markdown(f"**📦 Format:** {row['Format']}")
        #cols[1].markdown(f"**🗒️ Notes:** {row['Note']}")

        # Covers (if exists)
        def show_image(col, image_path, label):
            if os.path.exists(image_path):
                col.image(image_path, width=120, caption=label)
            else:
                col.markdown(f"**{label}:** _Not Available_")

        front = row.get("Front Cover", "").strip()
        back = row.get("Back Cover", "").strip()
        show_image(cols[2], f"covers/{front}", "Front Cover")
        show_image(cols[3], f"covers/{back}", "Back Cover")

    st.markdown("---")
