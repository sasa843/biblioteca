import streamlit as st
import pandas as pd
from pathlib import Path

# Load Excel file
df = pd.read_excel("Book_Database_With_Samples_And_Format.xlsx")

# Page config
st.set_page_config(page_title="📚 My Book Library", layout="wide")
st.title("📚 My Book Library")

# Search and Filter
search = st.text_input("🔍 Search by Book Name or Author:")
genres = ["All"] + sorted(df["Genre"].dropna().unique().tolist())
genre_filter = st.selectbox("🎯 Filter by Genre (optional):", genres)

# Filter logic
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df['Book Name'].str.contains(search, case=False, na=False) |
        filtered_df['Author'].str.contains(search, case=False, na=False)
    ]
if genre_filter != "All":
    filtered_df = filtered_df[filtered_df["Genre"] == genre_filter]

# Display results as cards
for _, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([1, 2, 2])
        
        # Column 1: Cover image
        front_img_path = f"covers/{row['Front Cover']}" if pd.notna(row['Front Cover']) else None
        if front_img_path and Path(front_img_path).is_file():
            cols[0].image(front_img_path, use_column_width=True, caption="Front Cover")
        else:
            cols[0].write("❌ No Image")
        
        # Column 2: Info
        cols[1].markdown(f"### {row['Book Name']}")
        cols[1].markdown(f"**Author:** {row['Author']}")
        cols[1].markdown(f"**Publisher:** {row['Publisher']}")
        cols[1].markdown(f"**Price:** ₹{row['Price']}")
        cols[1].markdown(f"**Format:** {row['Format']}")
        cols[1].markdown(f"**Fiction:** {row['Fiction / Non-Fiction']}")
        cols[1].markdown(f"**Genre:** {row['Genre']}")
        
        # Column 3: Back cover if exists
        back_img_path = f"covers/{row['Back Cover']}" if pd.notna(row['Back Cover']) else None
        if back_img_path and Path(back_img_path).is_file():
            cols[2].image(back_img_path, use_column_width=True, caption="Back Cover")
        else:
            cols[2].write("📘 No Back Cover")
        
        st.markdown("---")
