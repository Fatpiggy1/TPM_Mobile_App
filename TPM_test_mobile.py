import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="TPM Mobile", layout="wide")

DB_PATH = "tpm.db"
today_str = datetime.now().strftime("%Y-%m-%d")

# --- Ensure due_date columns exist ---
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    for table in ["PMs", "WorkOrders"]:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if "due_date" not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN due_date TEXT")
    # Fill missing due_date with today
    for table in ["PMs", "WorkOrders"]:
        cursor.execute(f"UPDATE {table} SET due_date = ? WHERE due_date IS NULL OR due_date = ''", (today_str,))
    conn.commit()

st.write("Database exists:", os.path.exists(DB_PATH))

# --- Helper Functions ---
def get_table(table_name):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

def calculate_due_date(frequency):
    now = datetime.now()
    if frequency == "1hr":
        return (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    elif frequency == "24hrs":
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif frequency == "7days":
        return (now + timedelta(days=7)).strftime("%Y-%m-%d")
    elif frequency == "6months":
        return (now + timedelta(days=182)).strftime("%Y-%m-%d")
    elif frequency == "12months":
        return (now + timedelta(days=365)).strftime("%Y-%m-%d")
    else:
        return now.strftime("%Y-%m-%d")

def get_table_columns(table_name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [col[1] for col in cursor.fetchall()]

frequency_options = ["1hr", "24hrs", "7days", "6months", "12months"]

st.title("📱 TPM Mobile Dashboard")

page = st.sidebar.radio(
    "Select Section",
    ["Assets", "PMs", "Work Orders", "Operator Checks", "Breakdowns", "Upcoming", "Completed History"]
)

# --- Assets ---
if page == "Assets":
    st.header("🧱 Assets")
    st.subheader("➕ Add New Asset")
    with st.form("add_asset_form"):
        asset_id = st.text_input("Asset ID")
        name = st.text_input("Asset Name")
        type_ = st.text_input("Type")
        location = st.text_input("Location")
        submitted = st.form_submit_button("Add Asset")
        if submitted:
            if not asset_id.isdigit():
                st.error("Asset ID must be a number!")
            else:
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        cols = get_table_columns("Assets")
                        placeholders = ",".join("?" for _ in cols)
                        values = []
                        for c in cols:
                            if c.lower() == "asset_id":
                                values.append(int(asset_id))
                            elif c.lower() == "name":
                                values.append(name)
                            elif c.lower() == "type":
                                values.append(type_)
                            elif c.lower() == "location":
                                values.append(location)
                            else:
                                values.append(None)
                        cursor.execute(f"INSERT INTO Assets ({','.join(cols)}) VALUES ({placeholders})", values)
                        conn.commit()
                    st.success(f"Asset '{name}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding asset: {e}")
    try:
        df = get_table("Assets")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading Assets: {e}")

# --- PMs ---
elif page == "PMs":
    st.header("🧰 Preventive Maintenance")
    try:
        df = get_table("PMs")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading PMs: {e}")

    st.subheader("➕ Add New PM")
    try:
        asset_options = get_table("Assets")['asset_id'].astype(str).tolist()
    except:
        asset_options = []

    with st.form("add_pm_form"):
        asset_id = st.selectbox("Select Asset ID", options=asset_options)
        pm_id = st.text_input("PM ID")
        description = st.text_input("Description")
        frequency = st.selectbox("Frequency", options=frequency_options)
        submitted = st.form_submit_button("Add PM")
        if submitted:
            if not pm_id.isdigit():
                st.error("PM ID must be a number!")
            else:
                due_date = calculate_due_date(frequency)
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        cols = get_table_columns("PMs")
                        placeholders = ",".join("?" for _ in cols)
                        values = []
                        for c in cols:
                            name = c.lower()
                            if "pm_id" in name:
                                values.append(int(pm_id))
                            elif "asset_id" in name:
                                values.append(int(asset_id))
                            elif "description" in name:
                                values.append(description)
                            elif "frequency" in name:
                                values.append(frequency)
                            elif "due_date" in name:
                                values.append(due_date)
                            else:
                                values.append(None)
                        cursor.execute(f"INSERT INTO PMs ({','.join(cols)}) VALUES ({placeholders})", values)
                        conn.commit()
                    st.success(f"PM '{pm_id}' added for Asset '{asset_id}'! Due: {due_date}")
                except Exception as e:
                    st.error(f"Error adding PM: {e}")

# --- Work Orders ---
elif page == "Work Orders":
    st.header("📄 Work Orders")
    try:
        df = get_table("WorkOrders")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading Work Orders: {e}")

    st.subheader("➕ Add New Work Order")
    try:
        asset_options = get_table("Assets")['asset_id'].astype(str).tolist()
    except:
        asset_options = []

    with st.form("add_wo_form"):
        asset_id = st.selectbox("Select Asset ID", options=asset_options)
        wo_id = st.text_input("Work Order ID")
        description = st.text_input("Description")
        frequency = st.selectbox("Frequency", options=frequency_options)
        submitted = st.form_submit_button("Add Work Order")
        if submitted:
            if not wo_id.isdigit():
                st.error("Work Order ID must be a number!")
            else:
                due_date = calculate_due_date(frequency)
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        cols = get_table_columns("WorkOrders")
                        placeholders = ",".join("?" for _ in cols)
                        values = []
                        for c in cols:
                            name = c.lower()
                            if "wo_id" in name:
                                values.append(int(wo_id))
                            elif "asset_id" in name:
                                values.append(int(asset_id))
                            elif "description" in name:
                                values.append(description)
                            elif "frequency" in name:
                                values.append(frequency)
                            elif "due_date" in name:
                                values.append(due_date)
                            else:
                                values.append(None)
                        cursor.execute(f"INSERT INTO WorkOrders ({','.join(cols)}) VALUES ({placeholders})", values)
                        conn.commit()
                    st.success(f"Work Order '{wo_id}' added for Asset '{asset_id}'! Due: {due_date}")
                except Exception as e:
                    st.error(f"Error adding Work Order: {e}")

# --- Operator Checks ---
elif page == "Operator Checks":
    st.header("✅ Operator Checks")
    try:
        df = get_table("OperatorChecks")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading Operator Checks: {e}")

    st.subheader("➕ Add New Operator Check")
    try:
        asset_options = get_table("Assets")['asset_id'].astype(str).tolist()
    except:
        asset_options = []

    with st.form("add_oc_form"):
        asset_id = st.selectbox("Select Asset ID", options=asset_options)
        check_id = st.text_input("Check ID")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Operator Check")
        if submitted:
            if not check_id.isdigit():
                st.error("Check ID must be a number!")
            else:
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        cols = get_table_columns("OperatorChecks")
                        placeholders = ",".join("?" for _ in cols)
                        values = []
                        for c in cols:
                            name = c.lower()
                            if "id" in name:
                                values.append(int(check_id))
                            elif "asset_id" in name:
                                values.append(int(asset_id))
                            elif "description" in name:
                                values.append(description)
                            else:
                                values.append(None)
                        cursor.execute(f"INSERT INTO OperatorChecks ({','.join(cols)}) VALUES ({placeholders})", values)
                        conn.commit()
                    st.success(f"Operator Check '{check_id}' added for Asset '{asset_id}'!")
                except Exception as e:
                    st.error(f"Error adding Operator Check: {e}")

# --- Breakdowns ---
# --- Breakdowns ---
elif page == "Breakdowns":
    st.header("🚨 Breakdowns")
    try:
        df = get_table("Breakdowns")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading Breakdowns: {e}")

    st.subheader("➕ Add New Breakdown")
    try:
        asset_options = get_table("Assets")['asset_id'].astype(str).tolist()
    except:
        asset_options = []

    with st.form("add_bd_form"):
        asset_id = st.selectbox("Select Asset ID", options=asset_options)
        bd_id = st.text_input("Breakdown ID")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Breakdown")
        if submitted:
            if not bd_id.isdigit():
                st.error("Breakdown ID must be a number!")
            else:
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        cols = get_table_columns("Breakdowns")
                        placeholders = ",".join("?" for _ in cols)
                        values = []
                        for c in cols:
                            name = c.lower()
                            if "id" in name:
                                values.append(int(bd_id))
                            elif "asset_id" in name:
                                values.append(int(asset_id))
                            elif "description" in name:
                                values.append(description)
                            else:
                                values.append(None)
                        cursor.execute(f"INSERT INTO Breakdowns ({','.join(cols)}) VALUES ({placeholders})", values)
                        conn.commit()
                    st.success(f"Breakdown '{bd_id}' added for Asset '{asset_id}'!")
                except Exception as e:
                    st.error(f"Error adding Breakdown: {e}")


# --- Upcoming PMs / Work Orders ---
elif page == "Upcoming":
    st.header("📅 Upcoming PMs & Work Orders")

    # Legend
    st.markdown("""
    **Legend:**  
    <span style='color:red'>■ Overdue</span>  
    <span style='color:orange'>■ Due Today</span>  
    <span style='color:green'>■ Upcoming</span>  
    """, unsafe_allow_html=True)

    status_filter = st.selectbox("Filter by Status", ["All", "Overdue", "Due Today", "Upcoming"])

    try:
        pms = get_table("PMs")
        wos = get_table("WorkOrders")
    except Exception as e:
        st.error(f"Error loading PMs or Work Orders: {e}")
        pms, wos = pd.DataFrame(), pd.DataFrame()

    # Ensure due_date is datetime
    for df, id_col, typ in [(pms, 'pm_id', 'PM'), (wos, 'wo_id', 'Work Order')]:
        if not df.empty:
            df['Type'] = typ
            df.rename(columns={id_col: 'ID'}, inplace=True)
            if 'due_date' in df.columns:
                df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
            else:
                df['due_date'] = pd.to_datetime(today_str)

    combined = pd.concat([pms, wos], ignore_index=True, sort=False)
    if combined.empty:
        st.info("No PMs or Work Orders available.")
    else:
        today = pd.to_datetime(datetime.now().date())
        combined['Status'] = combined['due_date'].apply(
            lambda x: "Overdue" if x.date() < today.date()
            else ("Due Today" if x.date() == today.date() else "Upcoming")
        )

        if status_filter != "All":
            combined = combined[combined['Status'] == status_filter]

        # Color map for status
        color_map = {"Overdue": "background-color:#f8d7da;",  # red
                     "Due Today": "background-color:#fff3cd;",  # orange
                     "Upcoming": "background-color:#d4edda;"}  # green

        st.subheader("Mark PMs / Work Orders as Complete")
        for idx, row in combined.iterrows():
            col1, col2 = st.columns([6,1])
            style = color_map.get(row['Status'], "")
            with col1:
                st.markdown(f"<div style='{style} padding:5px; border-radius:5px;'>"
                            f"{row['Type']} {row['ID']} | Asset: {row['asset_id']} | "
                            f"{row['description']} | Due: {row['due_date'].date()} | Status: {row['Status']}"
                            f"</div>", unsafe_allow_html=True)
            with col2:
                completed = st.checkbox("✅ Complete", key=f"complete_{row['Type']}_{row['ID']}")
                if completed:
                    table_name = "PMs" if row['Type'] == "PM" else "WorkOrders"
                    id_column = "pm_id" if row['Type'] == "PM" else "wo_id"
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        # Delete safely using explicit column name
                        cursor.execute(f"DELETE FROM [{table_name}] WHERE [{id_column}] = ?", (row['ID'],))
                        # Insert into CompletedHistory
                        cursor.execute("""CREATE TABLE IF NOT EXISTS CompletedHistory (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            Type TEXT,
                                            item_id INTEGER,
                                            asset_id INTEGER,
                                            description TEXT,
                                            completed_date TEXT
                                          )""")
                        cursor.execute("""INSERT INTO CompletedHistory (Type, item_id, asset_id, description, completed_date)
                                          VALUES (?, ?, ?, ?, ?)""",
                                       (row['Type'], row['ID'], row['asset_id'], row['description'], today_str))
                        conn.commit()
                    st.success(f"{row['Type']} {row['ID']} marked complete!")
                    st.experimental_rerun()  # Refresh page

# --- Completed History ---
elif page == "Completed History":
    st.header("📜 Completed PMs / Work Orders History")
    try:
        df = get_table("CompletedHistory")
        if not df.empty:
            st.dataframe(df.sort_values("completed_date", ascending=False), use_container_width=True)
        else:
            st.info("No completed items yet.")
    except Exception as e:
        st.error(f"Error loading Completed History: {e}")
