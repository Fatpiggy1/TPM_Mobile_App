import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "tpm.db"

# Connect to DB
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Helper: load table
def load_table(table):
    return pd.read_sql_query(f"SELECT * FROM {table}", conn)

# Helper: color-coded status
def color_status(due_date_str):
    if not due_date_str:
        return ""
    today = datetime.today().date()
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    if due_date < today:
        return "🔴 Overdue"
    elif due_date == today:
        return "🟠 Due Today"
    else:
        return "🟢 Upcoming"

# Sidebar navigation
page = st.sidebar.selectbox("Choose Page", ["Assets", "PMs", "Work Orders", "Operator Checks", "Breakdowns", "Dashboard"])

# --- Assets ---
if page == "Assets":
    st.header("📦 Assets")
    df = load_table("Assets")
    st.dataframe(df)

    with st.form("add_asset"):
        st.subheader("Add Asset")
        asset_id = st.text_input("Asset ID")
        name = st.text_input("Name")
        type_ = st.text_input("Type")
        location = st.text_input("Location")
        submitted = st.form_submit_button("Add Asset")
        if submitted:
            if not asset_id.isdigit():
                st.error("Asset ID must be a number!")
            else:
                cursor.execute("INSERT OR IGNORE INTO Assets (asset_id,name,type,location,due_date) VALUES (?,?,?,?,?)",
                               (int(asset_id), name, type_, location, datetime.today().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Asset added!")

# --- PMs ---
elif page == "PMs":
    st.header("🛠 Preventive Maintenance")
    df = load_table("PMs")
    df['Status'] = df['due_date'].apply(color_status)
    st.dataframe(df)

    assets = [str(row[0]) for row in cursor.execute("SELECT asset_id FROM Assets")]
    with st.form("add_pm"):
        st.subheader("Add PM")
        pm_id = st.text_input("PM ID")
        asset_id = st.selectbox("Asset ID", assets)
        description = st.text_input("Description")
        frequency = st.selectbox("Frequency", ["1hr","24hrs","7days","6months","12months"])
        submitted = st.form_submit_button("Add PM")
        if submitted:
            if not pm_id.isdigit():
                st.error("PM ID must be a number!")
            else:
                cursor.execute("INSERT OR IGNORE INTO PMs (pm_id,asset_id,description,frequency,due_date) VALUES (?,?,?,?,?)",
                               (int(pm_id), int(asset_id), description, frequency, datetime.today().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("PM added!")

# --- Work Orders ---
elif page == "Work Orders":
    st.header("📝 Work Orders")
    df = load_table("WorkOrders")
    df['Status'] = df['due_date'].apply(color_status)
    st.dataframe(df)

    assets = [str(row[0]) for row in cursor.execute("SELECT asset_id FROM Assets")]
    with st.form("add_wo"):
        st.subheader("Add Work Order")
        order_id = st.text_input("Order ID")
        asset_id = st.selectbox("Asset ID", assets)
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Work Order")
        if submitted:
            if not order_id.isdigit():
                st.error("Order ID must be a number!")
            else:
                cursor.execute("INSERT OR IGNORE INTO WorkOrders (order_id,asset_id,description,due_date) VALUES (?,?,?,?)",
                               (int(order_id), int(asset_id), description, datetime.today().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Work Order added!")

# --- Operator Checks ---
elif page == "Operator Checks":
    st.header("✅ Operator Checks")
    df = load_table("OperatorChecks")
    df['Status'] = df['due_date'].apply(color_status)
    st.dataframe(df)

    assets = [str(row[0]) for row in cursor.execute("SELECT asset_id FROM Assets")]
    with st.form("add_oc"):
        st.subheader("Add Operator Check")
        oc_id = st.text_input("Check ID")
        asset_id = st.selectbox("Asset ID", assets)
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Operator Check")
        if submitted:
            if not oc_id.isdigit():
                st.error("Check ID must be a number!")
            else:
                cursor.execute("INSERT OR IGNORE INTO OperatorChecks (oc_id,asset_id,description,due_date) VALUES (?,?,?,?)",
                               (int(oc_id), int(asset_id), description, datetime.today().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Operator Check added!")

# --- Breakdowns ---
elif page == "Breakdowns":
    st.header("⚠ Breakdowns")
    df = load_table("Breakdowns")
    df['Status'] = df['due_date'].apply(color_status)
    st.dataframe(df)

    assets = [str(row[0]) for row in cursor.execute("SELECT asset_id FROM Assets")]
    with st.form("add_bd"):
        st.subheader("Add Breakdown")
        bd_id = st.text_input("Breakdown ID")
        asset_id = st.selectbox("Asset ID", assets)
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Breakdown")
        if submitted:
            if not bd_id.isdigit():
                st.error("Breakdown ID must be a number!")
            else:
                cursor.execute("INSERT OR IGNORE INTO Breakdowns (bd_id,asset_id,description,due_date) VALUES (?,?,?,?)",
                               (int(bd_id), int(asset_id), description, datetime.today().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Breakdown added!")

# --- Dashboard ---
elif page == "Dashboard":
    st.header("📊 Dashboard Overview")
    for table in ["PMs","WorkOrders","OperatorChecks","Breakdowns"]:
        st.subheader(table)
        df = load_table(table)
        df['Status'] = df['due_date'].apply(color_status)
        st.dataframe(df)
