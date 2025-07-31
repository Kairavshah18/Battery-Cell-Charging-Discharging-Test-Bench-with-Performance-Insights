import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np
from io import BytesIO

# ------------------ CONFIGURATION ------------------
st.set_page_config(
    page_title="Battery Cell Testing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .main .block-container {
        padding-top: 1rem;
        background-color: #1e1e1e;
    }

    .stSelectbox div div, .stTextInput input, .stNumberInput input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .metric-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #404040;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'experiment' not in st.session_state:
    st.session_state.experiment = "Standard Test"

# ------------------ FUNCTIONS ------------------
def get_default_values(cell_type):
    return {
        "voltage": 3.2 if cell_type == "LFP" else 3.6,
        "max_voltage": 3.4 if cell_type == "LFP" else 4.0,
        "min_voltage": 2.8 if cell_type == "LFP" else 3.2,
        "temp": round(random.uniform(25, 40), 1),
        "current": round(random.uniform(1.0, 5.0), 2),
        "capacitance": round(random.uniform(2500, 3500) if cell_type == "LFP" else random.uniform(2800, 3800), 0)
    }

def create_overview_charts(df):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature', 'Voltage', 'Capacitance', 'Current')
    )
    colors = {'Temperature': '#ff6b6b', 'Voltage': '#4ecdc4', 'Capacitance': '#45b7d1', 'Current': '#ffa726'}
    
    for i, col in enumerate(['Temperature', 'Voltage', 'Capacitance', 'Current']):
        row, c = divmod(i, 2)
        fig.add_trace(go.Scatter(x=df['Cell'], y=df[col], mode='lines+markers', name=col, line=dict(color=colors[col], width=3)), row=row+1, col=c+1)
    
    fig.update_layout(height=600, plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='white'))
    return fig

def export_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙ Test Configuration")
st.session_state.experiment = st.sidebar.selectbox("Experiment Type", ["Standard Test", "Overcharge Test", "Thermal Stress Test"])
bench_name = st.sidebar.text_input("Bench Name", value="Bench_001")
group_name = st.sidebar.text_input("Group Name", value="Group_A")
primary_cell_type = st.sidebar.selectbox("Primary Cell Type", ["NMC", "LFP"])

if st.sidebar.button("Randomize All Values"):
    for i in range(8):
        cell_type = random.choice(["NMC", "LFP"])
        defaults = get_default_values(cell_type)
        st.session_state.cells_data[f"Cell {i+1}"] = {"cell_type": cell_type, **defaults}
    st.experimental_rerun()

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["📥 Data Input", "📊 Visualizations", "📈 Insights & Export"])

# ------------------ TAB 1: DATA INPUT ------------------
with tab1:
    st.subheader(f"{st.session_state.experiment} - Data Input")
    cols = st.columns([1, 2, 2, 2, 2, 2])
    cols[0].markdown("**Slot**")
    cols[1].markdown("**Type**")
    cols[2].markdown("**Temp (°C)**")
    cols[3].markdown("**Current (A)**")
    cols[4].markdown("**Voltage (V)**")
    cols[5].markdown("**Capacity (mAh)**")

    for i in range(8):
        row = st.columns([1, 2, 2, 2, 2, 2])
        row[0].markdown(f"**{i+1}**")
        cell_type = row[1].selectbox("", ["NMC", "LFP"], key=f"type_{i}")
        defaults = get_default_values(cell_type)
        temp = row[2].number_input("", 0.0, 100.0, defaults['temp'], 0.1, key=f"temp_{i}")
        current = row[3].number_input("", 0.0, 20.0, defaults['current'], 0.01, key=f"current_{i}")
        voltage = row[4].number_input("", 0.0, 5.0, defaults['voltage'], 0.01, key=f"voltage_{i}")
        cap = row[5].number_input("", 0.0, 10000.0, defaults['capacitance'], 1.0, key=f"cap_{i}")
        st.session_state.cells_data[f"Cell {i+1}"] = {"cell_type": cell_type, "temp": temp, "current": current, "voltage": voltage, "capacitance": cap, "max_voltage": defaults['max_voltage'], "min_voltage": defaults['min_voltage']}

# ------------------ TAB 2: VISUALIZATION ------------------
with tab2:
    if st.session_state.cells_data:
        df = pd.DataFrame([{**{"Cell": k}, **v} for k, v in st.session_state.cells_data.items()])
        st.plotly_chart(create_overview_charts(df), use_container_width=True)
    else:
        st.info("Enter data in Tab 1 to visualize.")

# ------------------ TAB 3: INSIGHTS & EXPORT ------------------
with tab3:
    if st.session_state.cells_data:
        df = pd.DataFrame([{**{"Cell": k}, **v} for k, v in st.session_state.cells_data.items()])
        avg_temp, avg_voltage, avg_cap = np.mean(df['temp']), np.mean(df['voltage']), np.mean(df['capacitance'])
        st.markdown(f"**Average Temp:** {avg_temp:.2f} °C | **Average Voltage:** {avg_voltage:.2f} V | **Average Capacity:** {avg_cap:.0f} mAh")

        csv_data = export_csv(df)
        st.download_button("📥 Export CSV", data=csv_data, file_name=f"{bench_name}_{st.session_state.experiment}.csv", mime="text/csv")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Enter data in Tab 1 to see insights and export.")
