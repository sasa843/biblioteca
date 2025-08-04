import streamlit as st
import pandas as pd

# Load your Excel file
df = pd.read_excel("Book_Database_With_Samples_And_Format.xlsx")

# Page setup
st.set_page_config(page_title="📚 My Book Library")
st.title("📚 My Book Library")

# Search input
search = st.text_input("🔍 Search by Book Name or Author:")

# Filter the DataFrame based on search
if search:
    filtered_df = df[df['Book Name'].str.contains(search, case=False, na=False) |
                     df['Author'].str.contains(search, case=False, na=False)]
else:
    filtered_df = df

# Optional: Genre filter
genre = st.selectbox("🎯 Filter by Genre (optional):", ["All"] + sorted(df["Genre"].dropna().unique().tolist()))
if genre != "All":
    filtered_df = filtered_df[filtered_df["Genre"] == genre]

# Display the filtered DataFrame
st.dataframe(filtered_df)

# Show genre distribution (optional)
if st.checkbox("📊 Show genre stats"):
    st.bar_chart(df["Genre"].value_counts())
