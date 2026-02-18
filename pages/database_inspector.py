import streamlit as st
import pandas as pd
from src.db_manager import get_connection

st.set_page_config(page_title="SQL Inspector", page_icon="🗄️", layout="wide")

st.title("🗄️ Database Inspector")
st.markdown("Run live SQL queries against the **UFC Data Warehouse** (`ufc_data.db`).")

# Helper to run query
def run_query(query):
    conn = get_connection()
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        return str(e)
    finally:
        conn.close()

# --- Schema Reference ---
with st.expander("📖 View Database Schema"):
    st.markdown("""
    **Tables:**
    *   `fighters` (`id`, `name`, `nickname`, `weight_class`, `height_cm`...)
    *   `fighter_stats` (`fighter_id`, `wins`, `slpm`, `td_avg`...)
    
    **Example Join:**
    ```sql
    SELECT f.name, f.weight_class, s.wins 
    FROM fighters f 
    JOIN fighter_stats s ON f.id = s.fighter_id 
    WHERE s.wins > 20
    ORDER BY s.wins DESC
    ```
    """)

# --- Query Editor ---
col1, col2 = st.columns([2, 1])

with col1:
    default_query = "SELECT * FROM fighters ORDER BY RANDOM() LIMIT 10;"
    query = st.text_area("✍️ SQL Query", value=default_query, height=150)
    
    if st.button("▶️ Run Query", type="primary"):
        if "DROP" in query.upper() or "DELETE" in query.upper() or "UPDATE" in query.upper():
            st.error("⚠️ Read-only commands only, please!")
        else:
            result = run_query(query)
            if isinstance(result, pd.DataFrame):
                st.success(f"Returned {len(result)} rows.")
                st.dataframe(result, use_container_width=True)
            else:
                st.error(f"Error: {result}")

with col2:
    st.info("💡 **Try these queries:**")
    st.markdown("""
    **Top Strikers:**
    ```sql
    SELECT f.name, s.slpm 
    FROM fighters f 
    JOIN fighter_stats s ON f.id = s.fighter_id 
    ORDER BY s.slpm DESC LIMIT 5
    ```
    
    **Heavyweights:**
    ```sql
    SELECT * FROM fighters 
    WHERE weight_class = 'Heavyweight'
    ```
    """)
