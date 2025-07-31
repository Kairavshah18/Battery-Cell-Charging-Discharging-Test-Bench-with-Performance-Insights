import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import numpy as np

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Battery Cell Testing Dashboard", layout="wide")

# ---------------------- STYLES ----------------------
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        color: #EAEAEA;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {padding-top: 2rem;}
    h1, h2, h3, h4 {color: #FFFFFF;}
    .metric-card {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #333333;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- SESSION STATE ----------------------
if 'experiments' not in st.session_state:
    st.session_state.experiments = {}
if 'current_data' not in st.session_state:
    st.session_state.current_data = pd.DataFrame()
if 'num_cells' not in st.session_state:
    st.session_state.num_cells = 4  # default minimum cells

# ---------------------- FUNCTIONS ----------------------
def random_cell_data(n):
    types = ["NMC", "LFP"]
    data = []
    for i in range(1, n+1):
        cell_type = random.choice(types)
        if cell_type == "LFP":
            voltage = round(random.uniform(2.8, 3.4), 2)
            cap = round(random.uniform(2500, 3500))
        else:
            voltage = round(random.uniform(3.2, 4.0), 2)
            cap = round(random.uniform(2800, 3800))
        temp = round(random.uniform(25, 40), 1)
        current = round(random.uniform(1.0, 5.0), 2)
        data.append([f"Cell {i}", cell_type, temp, current, voltage, cap])
    return pd.DataFrame(data, columns=["Cell", "Type", "Temperature (°C)", "Current (A)", "Voltage (V)", "Capacitance (mAh)"])

def plot_experiment_table():
    if len(st.session_state.experiments) > 0:
        exp_names = list(st.session_state.experiments.keys())
        dfs = []
        for exp in exp_names:
            df = st.session_state.experiments[exp].copy()
            df.insert(0, "Experiment", exp)
            dfs.append(df)
        combined = pd.concat(dfs)
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(combined.columns), fill_color="#1E1E1E", font=dict(color="white")),
            cells=dict(values=[combined[col] for col in combined.columns], fill_color="#262626", font=dict(color="white"))
        )])
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No experiments saved yet.")

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.header("Configuration")
    st.session_state.num_cells = st.number_input("Number of Cells", min_value=4, max_value=20, value=st.session_state.num_cells)
    
    if st.button("Randomize Current Data"):
        st.session_state.current_data = random_cell_data(st.session_state.num_cells)
    
    st.markdown("---")
    exp_name = st.text_input("Experiment Name")
    if st.button("Save Experiment"):
        if not st.session_state.current_data.empty and exp_name:
            st.session_state.experiments[exp_name] = st.session_state.current_data.copy()
            st.success(f"Experiment '{exp_name}' saved.")
        else:
            st.warning("Enter experiment name and data before saving.")

# ---------------------- MAIN CONTENT ----------------------
tab1, tab2 = st.tabs(["Current Experiment", "Compare Experiments"])

# -------- Tab 1: Current Experiment --------
with tab1:
    st.header("Current Experiment Data")
    if st.session_state.current_data.empty:
        st.info("No data loaded. Click 'Randomize Current Data' or enter manually.")
    else:
        st.dataframe(st.session_state.current_data, use_container_width=True)

# -------- Tab 2: Compare Experiments --------
with tab2:
    st.header("Experiments Comparison")
    plot_experiment_table()
