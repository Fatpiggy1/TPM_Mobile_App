import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- Database setup ---
DB_PATH = "tpm.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# --- Ensure due_date exists ---
tables = ["Assets", "PMs", "WorkOrders", "OperatorChecks", "Breakdowns"]
for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    if "due_date" not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN due_date TEXT")
conn.commit()

# --- Load table function ---
def load_table(table):
    return pd.read_sql_query(f"SELECT * FROM {table}", conn)

# --- Colour helper ---
def due_colour(due_str):
    if due_str:
        due_date = datetime.strptime(due_str, "%Y-%m-%d")
        today = datetime.today().date()
        if due_date < today:
            return 'red'
        elif due_date == today:
            return 'orange'
        else:
            return 'green'
    return 'grey'

# --- Streamlit page ---
st.set_page_config(page_title="📱 TPM Mobile Dashboard", layout="wide")
st.title("📱 TPM Mobile Dashboard")

page = st.sidebar.selectbox("Select Function", ["Assets", "PMs", "Work Orders", "Operator Checks", "Breakdowns", "Upcoming"])

# --- Forms and tables ---
if page == "Assets":
    st.header("Assets")
    df = load_table("Assets")
    st.dataframe(df)
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
                try:
                    cursor.execute("INSERT INTO Assets (asset_id,name,type,location) VALUES (?,?,?,?)",
                                   (int(asset_id), name, type_, location))
                    conn.commit()
                    st.success("Asset added!")
                except Exception as e:
                    st.error(f"Error adding asset: {e}")

elif page == "PMs":
    st.header("Preventative Maintenance")
    df = load_table("PMs")
    st.dataframe(df)
    with st.form("add_pm_form"):
        pm_id = st.text_input("PM ID")
        asset_id = st.text_input("Asset ID")
        description = st.text_input("Description")
        interval = st.selectbox("Interval", ["1hr", "24hrs", "7 days", "6 months", "12 months"])
        submitted = st.form_submit_button("Add PM")
        if submitted:
            if not pm_id.isdigit() or not asset_id.isdigit():
                st.error("IDs must be numbers!")
            else:
                due_date = datetime.today().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO PMs (pm_id,asset_id,description,interval,due_date) VALUES (?,?,?,?,?)",
                               (int(pm_id), int(asset_id), description, interval, due_date))
                conn.commit()
                st.success("PM added!")

elif page == "Work Orders":
    st.header("Work Orders")
    df = load_table("WorkOrders")
    st.dataframe(df)
    with st.form("add_wo_form"):
        wo_id = st.text_input("WO ID")
        asset_id = st.text_input("Asset ID")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Work Order")
        if submitted:
            if not wo_id.isdigit() or not asset_id.isdigit():
                st.error("IDs must be numbers!")
            else:
                due_date = datetime.today().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO WorkOrders (workorder_id,asset_id,description,due_date) VALUES (?,?,?,?)",
                               (int(wo_id), int(asset_id), description, due_date))
                conn.commit()
                st.success("Work Order added!")

elif page == "Operator Checks":
    st.header("Operator Checks")
    df = load_table("OperatorChecks")
    st.dataframe(df)
    with st.form("add_oc_form"):
        oc_id = st.text_input("Check ID")
        asset_id = st.text_input("Asset ID")
        result = st.text_input("Result")
        submitted = st.form_submit_button("Add Check")
        if submitted:
            if not oc_id.isdigit() or not asset_id.isdigit():
                st.error("IDs must be numbers!")
            else:
                due_date = datetime.today().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO OperatorChecks (oc_id,asset_id,result,due_date) VALUES (?,?,?,?)",
                               (int(oc_id), int(asset_id), result, due_date))
                conn.commit()
                st.success("Operator Check added!")

elif page == "Breakdowns":
    st.header("Breakdowns")
    df = load_table("Breakdowns")
    st.dataframe(df)
    with st.form("add_bd_form"):
        bd_id = st.text_input("Breakdown ID")
        asset_id = st.text_input("Asset ID")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Breakdown")
        if submitted:
            if not bd_id.isdigit() or not asset_id.isdigit():
                st.error("IDs must be numbers!")
            else:
                due_date = datetime.today().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO Breakdowns (breakdown_id,asset_id,description,due_date) VALUES (?,?,?,?)",
                               (int(bd_id), int(asset_id), description, due_date))
                conn.commit()
                st.success("Breakdown added!")

elif page == "Upcoming":
    st.header("📅 Upcoming PMs & Work Orders")
    try:
        pms = load_table("PMs")
        wos = load_table("WorkOrders")
        today = datetime.today().date()
        st.subheader("PMs")
        for _, row in pms.iterrows():
            colour = due_colour(row.get("due_date", ""))
            st.markdown(f"- <span style='color:{colour}'>{row['pm_id']} - {row['description']} (Due: {row.get('due_date','N/A')})</span>", unsafe_allow_html=True)
        st.subheader("Work Orders")
        for _, row in wos.iterrows():
            colour = due_colour(row.get("due_date", ""))
            st.markdown(f"- <span style='color:{colour}'>{row['workorder_id']} - {row['description']} (Due: {row.get('due_date','N/A')})</span>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading upcoming tasks: {e}")
