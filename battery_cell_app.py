import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np

# ----------------------------
# 🔧 PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Battery Cell Testing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# 🎨 DARK THEME CSS
# ----------------------------
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: #ffffff; }
    .main .block-container { padding-top: 2rem; background-color: #1e1e1e; }
    .stSelectbox > div > div, .stTextInput > div > div > input,
    .stNumberInput > div > div > input { background-color: #2d2d2d; color: #ffffff; border: 1px solid #404040; }
    .metric-card { background-color: #2d2d2d; padding: 1rem; border-radius: 0.5rem; border: 1px solid #404040; margin-bottom: 1rem; }
    .highlight-high { color: #ff6b6b; font-weight: bold; }
    .highlight-low { color: #4ecdc4; font-weight: bold; }
    .highlight-warning { color: #ffa726; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 🛠️ SESSION STATE INIT
# ----------------------------
if "experiments" not in st.session_state:
    st.session_state.experiments = {}
if "current_experiment" not in st.session_state:
    st.session_state.current_experiment = {}
if "num_cells" not in st.session_state:
    st.session_state.num_cells = 8
if "selected_experiment" not in st.session_state:
    st.session_state.selected_experiment = None

# ----------------------------
# 📌 HELPER FUNCTIONS
# ----------------------------
def get_default_values(cell_type):
    """Default values based on cell type"""
    if cell_type == "LFP":
        return {"Voltage (V)": 3.2, "Max Voltage": 3.4, "Min Voltage": 2.8,
                "Temperature (°C)": round(random.uniform(25, 40), 1),
                "Current (A)": round(random.uniform(1.0, 5.0), 2),
                "Capacitance (mAh)": round(random.uniform(2500, 3500), 0)}
    else:
        return {"Voltage (V)": 3.6, "Max Voltage": 4.0, "Min Voltage": 3.2,
                "Temperature (°C)": round(random.uniform(25, 40), 1),
                "Current (A)": round(random.uniform(1.0, 5.0), 2),
                "Capacitance (mAh)": round(random.uniform(2800, 3800), 0)}

def get_safe_value(cell_key, field, default, min_val=None, max_val=None):
    """Safely fetch values from experiment"""
    val = st.session_state.current_experiment.get(cell_key, {}).get(field, default)
    if isinstance(default, (int, float)):
        try:
            val = float(val)
        except (ValueError, TypeError):
            val = default
        if min_val is not None: val = max(val, min_val)
        if max_val is not None: val = min(val, max_val)
    return val

def create_overview_charts(df):
    """Overview charts"""
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=('Temperature vs Cell Slot', 'Voltage vs Cell Slot',
                                        'Capacitance vs Cell Slot', 'Current vs Cell Slot'))
    fig.add_trace(go.Scatter(x=df['Cell'], y=df['Temperature (°C)'],
                             mode='lines+markers', line=dict(color='#ff6b6b')), 1, 1)
    fig.add_trace(go.Scatter(x=df['Cell'], y=df['Voltage (V)'],
                             mode='lines+markers', line=dict(color='#4ecdc4')), 1, 2)
    fig.add_trace(go.Scatter(x=df['Cell'], y=df['Capacitance (mAh)'],
                             mode='lines+markers', line=dict(color='#45b7d1')), 2, 1)
    fig.add_trace(go.Scatter(x=df['Cell'], y=df['Current (A)'],
                             mode='lines+markers', line=dict(color='#ffa726')), 2, 2)
    fig.update_layout(height=600, plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='white'))
    return fig

def create_individual_cell_chart(cell_data, cell_name):
    """Bar chart for one cell"""
    fig = go.Figure(data=[go.Bar(
        x=['Temp', 'Voltage', 'Current', 'Capacitance'],
        y=[cell_data['Temperature (°C)'], cell_data['Voltage (V)'],
           cell_data['Current (A)'], cell_data['Capacitance (mAh)']],
        marker_color=['#ff6b6b', '#4ecdc4', '#ffa726', '#45b7d1']
    )])
    fig.update_layout(title=f"{cell_name}", plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='white'))
    return fig

# ----------------------------
# 🖥️ MAIN APP
# ----------------------------
st.title("🔋 Battery Cell Testing Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Experiment Control")
    exp_name = st.text_input("Experiment Name", value="Experiment_1")
    if st.button("💾 Save Current Experiment"):
        st.session_state.experiments[exp_name] = st.session_state.current_experiment.copy()
        st.success(f"Experiment '{exp_name}' saved!")
    selected = st.selectbox("📂 Load Experiment", ["None"] + list(st.session_state.experiments.keys()))
    if selected != "None":
        st.session_state.current_experiment = st.session_state.experiments[selected].copy()
        st.session_state.selected_experiment = selected
    st.session_state.num_cells = st.number_input("Number of Cells", 1, 20, st.session_state.num_cells)

    if st.button("⬇ Export CSV"):
        df_export = pd.DataFrame(st.session_state.current_experiment).T.reset_index().rename(columns={"index": "Cell"})
        st.download_button("Download CSV", df_export.to_csv(index=False), file_name=f"{exp_name}.csv", mime="text/csv")

# Tabs
tab1, tab2, tab3 = st.tabs(["Data Input", "Visualizations", "Insights"])

# ----------------------------
# 📥 TAB 1 - DATA INPUT
# ----------------------------
with tab1:
    st.header("Cell Testing Data Input")
    for i in range(st.session_state.num_cells):
        cell_key = f"Cell_{i+1}"
        cols = st.columns([1.2, 2, 2, 2, 2, 2])
        with cols[0]: st.markdown(f"**{i+1}**")
        with cols[1]:
            ctype = st.selectbox(f"Type_{cell_key}", ["NMC", "LFP"],
                                 index=["NMC", "LFP"].index(get_safe_value(cell_key, "Cell Type", "NMC")),
                                 key=f"type_{cell_key}")
        with cols[2]:
            temp = st.number_input(f"Temp_{cell_key}", 0.0, 100.0,
                                   get_safe_value(cell_key, "Temperature (°C)", 30.0), 0.1, key=f"temp_{cell_key}")
        with cols[3]:
            current = st.number_input(f"Current_{cell_key}", 0.0, 20.0,
                                      get_safe_value(cell_key, "Current (A)", 2.0), 0.01, key=f"current_{cell_key}")
        with cols[4]:
            voltage = st.number_input(f"Voltage_{cell_key}", 0.0, 5.0,
                                      get_safe_value(cell_key, "Voltage (V)", 3.6), 0.01, key=f"voltage_{cell_key}")
        with cols[5]:
            capacitance = st.number_input(f"Capacitance_{cell_key}", 0.0, 10000.0,
                                          get_safe_value(cell_key, "Capacitance (mAh)", 3000.0), 1.0, key=f"capacitance_{cell_key}")

        st.session_state.current_experiment[cell_key] = {
            "Cell Type": ctype, "Temperature (°C)": temp, "Current (A)": current,
            "Voltage (V)": voltage, "Capacitance (mAh)": capacitance
        }

# ----------------------------
# 📊 TAB 2 - VISUALIZATIONS
# ----------------------------
with tab2:
    if st.session_state.current_experiment:
        df = pd.DataFrame(st.session_state.current_experiment).T.reset_index().rename(columns={"index": "Cell"})
        st.subheader("Overview Charts")
        st.plotly_chart(create_overview_charts(df), use_container_width=True)

        st.subheader("Individual Cell Analysis")
        rows = [st.columns(4) for _ in range((st.session_state.num_cells + 3) // 4)]
        for idx, (cell_name, cell_data) in enumerate(st.session_state.current_experiment.items()):
            with rows[idx // 4][idx % 4]:
                st.plotly_chart(create_individual_cell_chart(cell_data, cell_name), use_container_width=True)
    else:
        st.info("Enter data to visualize.")

# ----------------------------
# 📈 TAB 3 - INSIGHTS
# ----------------------------
with tab3:
    if st.session_state.current_experiment:
        df = pd.DataFrame(st.session_state.current_experiment).T.reset_index().rename(columns={"index": "Cell"})
        st.subheader("Summary Table")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Enter data to generate insights.")
