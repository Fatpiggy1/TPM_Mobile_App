import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "tpm.db"

# --- Database setup ---
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
tables_and_columns = {
    "Assets": [("asset_id", "INTEGER PRIMARY KEY"), ("name", "TEXT"), ("type", "TEXT"), ("location", "TEXT")],
    "PMs": [("pm_id", "INTEGER PRIMARY KEY"), ("asset_id", "INTEGER"), ("description", "TEXT"), ("due_date", "TEXT")],
    "WorkOrders": [("wo_id", "INTEGER PRIMARY KEY"), ("asset_id", "INTEGER"), ("description", "TEXT"), ("due_date", "TEXT")],
    "OperatorChecks": [("oc_id", "INTEGER PRIMARY KEY"), ("asset_id", "INTEGER"), ("description", "TEXT"), ("due_date", "TEXT")],
    "Breakdowns": [("bd_id", "INTEGER PRIMARY KEY"), ("asset_id", "INTEGER"), ("description", "TEXT"), ("due_date", "TEXT")]
}

for table, cols in tables_and_columns.items():
    columns_sql = ", ".join([" ".join(col) for col in cols])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns_sql})")
conn.commit()

# --- Sample data ---
def populate_sample_data():
    cursor.execute("SELECT COUNT(*) FROM Assets")
    if cursor.fetchone()[0] == 0:
        sample_assets = [
            (1, "Machine A", "Extruder", "Line 1"),
            (2, "Machine B", "Conveyor", "Line 2")
        ]
        cursor.executemany("INSERT INTO Assets VALUES (?, ?, ?, ?)", sample_assets)
        today = datetime.today().strftime("%Y-%m-%d")
        sample_pms = [
            (1, 1, "Lubricate bearings", today),
            (2, 2, "Check belt tension", today)
        ]
        cursor.executemany("INSERT INTO PMs VALUES (?, ?, ?, ?)", sample_pms)
        conn.commit()

populate_sample_data()

# --- Helper functions ---
def load_table(table):
    return pd.read_sql_query(f"SELECT * FROM {table}", conn)

def delete_row(table, row_id_name, row_id_value):
    cursor.execute(f"DELETE FROM {table} WHERE {row_id_name} = ?", (row_id_value,))
    conn.commit()

# --- Streamlit UI ---
st.set_page_config(page_title="📱 TPM Mobile Dashboard", layout="wide")
st.title("📱 TPM Mobile Dashboard")

tabs = ["Assets", "PMs", "Work Orders", "Operator Checks", "Breakdowns"]
page = st.sidebar.selectbox("Select function", tabs)

if page == "Assets":
    st.header("Assets")
    df = load_table("Assets")
    for i, row in df.iterrows():
        cols = st.columns([1, 2, 2, 2, 1])
        cols[0].write(row["asset_id"])
        cols[1].write(row["name"])
        cols[2].write(row["type"])
        cols[3].write(row["location"])
        if cols[4].button("Delete", key=f"delete_asset_{row['asset_id']}"):
            delete_row("Assets", "asset_id", row["asset_id"])
            st.experimental_rerun()

    st.subheader("Add Asset")
    with st.form("add_asset_form"):
        asset_id = st.text_input("Asset ID")
        name = st.text_input("Name")
        type_ = st.text_input("Type")
        location = st.text_input("Location")
        submitted = st.form_submit_button("Add Asset")
        if submitted:
            if not asset_id.isdigit():
                st.error("Asset ID must be a number!")
            else:
                cursor.execute("INSERT INTO Assets VALUES (?, ?, ?, ?)",
                               (int(asset_id), name, type_, location))
                conn.commit()
                st.success("Asset added!")
                st.experimental_rerun()

elif page == "PMs":
    st.header("Preventive Maintenance")
    df = load_table("PMs")
    today = datetime.today().strftime("%Y-%m-%d")
    for i, row in df.iterrows():
        due = row["due_date"]
        if due < today:
            color = "red"
        elif due == today:
            color = "orange"
        else:
            color = "green"
        cols = st.columns([1, 2, 3, 2, 1])
        cols[0].write(row["pm_id"])
        cols[1].write(row["asset_id"])
        cols[2].write(row["description"])
        cols[3].markdown(f"<span style='color:{color}'>{due}</span>", unsafe_allow_html=True)
        if cols[4].button("Delete", key=f"delete_pm_{row['pm_id']}"):
            delete_row("PMs", "pm_id", row["pm_id"])
            st.experimental_rerun()

    st.subheader("Add PM")
    with st.form("add_pm_form"):
        pm_id = st.text_input("PM ID")
        asset_id = st.text_input("Asset ID")
        description = st.text_input("Description")
        due_date = st.date_input("Due Date")
        submitted = st.form_submit_button("Add PM")
        if submitted:
            if not pm_id.isdigit() or not asset_id.isdigit():
                st.error("IDs must be numbers!")
            else:
                cursor.execute("INSERT INTO PMs VALUES (?, ?, ?, ?)",
                               (int(pm_id), int(asset_id), description, due_date.strftime("%Y-%m-%d")))
                conn.commit()
                st.success("PM added!")
                st.experimental_rerun()

# Repeat similar structure for Work Orders, Operator Checks, Breakdowns
# For brevity, they follow the same pattern as PMs above with delete buttons

elif page == "Work Orders":
    st.header("Work Orders")
    df = load_table("WorkOrders")
    today = datetime.today().strftime("%Y-%m-%d")
    for i, row in df.iterrows():
        due = row["due_date"]
        if due < today:
            color = "red"
        elif due == today:
            color = "orange"
        else:
            color = "green"
        cols = st.columns([1, 2, 3, 2, 1])
        cols[0].write(row["wo_id"])
        cols[1].write(row["asset_id"])
        cols[2].write(row["description"])
        cols[3].markdown(f"<span style='color:{color}'>{due}</span>", unsafe_allow_html=True)
        if cols[4].button("Delete", key=f"delete_wo_{row['wo_id']}"):
            delete_row("WorkOrders", "wo_id", row["wo_id"])
            st.experimental_rerun()

elif page == "Operator Checks":
    st.header("Operator Checks")
    df = load_table("OperatorChecks")
    today = datetime.today().strftime("%Y-%m-%d")
    for i, row in df.iterrows():
        due = row["due_date"]
        if due < today:
            color = "red"
        elif due == today:
            color = "orange"
        else:
            color = "green"
        cols = st.columns([1, 2, 3, 2, 1])
        cols[0].write(row["oc_id"])
        cols[1].write(row["asset_id"])
        cols[2].write(row["description"])
        cols[3].markdown(f"<span style='color:{color}'>{due}</span>", unsafe_allow_html=True)
        if cols[4].button("Delete", key=f"delete_oc_{row['oc_id']}"):
            delete_row("OperatorChecks", "oc_id", row["oc_id"])
            st.experimental_rerun()

elif page == "Breakdowns":
    st.header("Breakdowns")
    df = load_table("Breakdowns")
    today = datetime.today().strftime("%Y-%m-%d")
    for i, row in df.iterrows():
        due = row["due_date"]
        if due < today:
            color = "red"
        elif due == today:
            color = "orange"
        else:
            color = "green"
        cols = st.columns([1, 2, 3, 2, 1])
        cols[0].write(row["bd_id"])
        cols[1].write(row["asset_id"])
        cols[2].write(row["description"])
        cols[3].markdown(f"<span style='color:{color}'>{due}</span>", unsafe_allow_html=True)
        if cols[4].button("Delete", key=f"delete_bd_{row['bd_id']}"):
            delete_row("Breakdowns", "bd_id", row["bd_id"])
            st.experimental_rerun()
