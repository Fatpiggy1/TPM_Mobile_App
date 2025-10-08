import streamlit as st
import pandas as pd
from datetime import datetime

# Example Assets table
assets = pd.DataFrame([{"ID":1,"Name":"Press A"},{"ID":2,"Name":"Extruder"}])
st.title("TPM Dashboard")

# Dashboard metrics
st.write(f"Total Assets: {len(assets)}")

# Add PM
st.subheader("Add Preventive Maintenance")
asset_choice = st.selectbox("Select Asset", assets["Name"])
pm_desc = st.text_input("PM Description")
if st.button("Add PM"):
    st.write(f"Added PM for {asset_choice} on {datetime.today().date()}")
