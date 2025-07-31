import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np

# Configure page
st.set_page_config(page_title="Battery Cell Testing Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark professional theme
st.markdown("""
<style>
    .stApp { background-color: #121212; color: white; }
    .main .block-container { padding-top: 1rem; background-color: #121212; }
    .stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #1e1e1e; color: white; border: 1px solid #333;
    }
    .metric-card { background-color: #1e1e1e; padding: 1rem; border-radius: 0.5rem; border: 1px solid #333; margin-bottom: 1rem; }
    .highlight-high { color: #ff4d4d; font-weight: bold; }
    .highlight-low { color: #4dd0e1; font-weight: bold; }
    .highlight-warning { color: #ffa726; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'experiments' not in st.session_state:
    st.session_state.experiments = {}
if 'num_cells' not in st.session_state:
    st.session_state.num_cells = 8

# Default values
def get_default_values(cell_type):
    return {
        "voltage": 3.2 if cell_type == "LFP" else 3.6,
        "max_voltage": 3.4 if cell_type == "LFP" else 4.0,
        "min_voltage": 2.8 if cell_type == "LFP" else 3.2,
        "temp": round(random.uniform(25, 40), 1),
        "current": round(random.uniform(1.0, 5.0), 2),
        "capacitance": round(random.uniform(2500, 3500) if cell_type == "LFP" else random.uniform(2800, 3800), 0)
    }

# Charts
def create_overview_charts(df):
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=('Temperature vs Cell', 'Voltage vs Cell',
                                        'Capacitance vs Cell', 'Current vs Cell'))
    colors = {'Temperature':'#ff4d4d','Voltage':'#4dd0e1','Capacitance':'#2196f3','Current':'#ffa726'}
    for i,(y,col) in enumerate(zip(['Temperature','Voltage','Capacitance','Current'],[1,2,1,2])):
        fig.add_trace(go.Scatter(x=df['Cell'], y=df[y], mode='lines+markers', name=y,
                                 line=dict(color=colors[y], width=3), marker=dict(size=8)),
                      row=(i//2)+1, col=col)
    fig.update_layout(height=600, plot_bgcolor='#121212', paper_bgcolor='#121212', font=dict(color='white'))
    fig.update_xaxes(gridcolor='#333'); fig.update_yaxes(gridcolor='#333')
    return fig

def create_individual_cell_chart(cell_data, cell_name):
    parameters = ['Temperature', 'Voltage', 'Current', 'Capacitance']
    values = [cell_data['temp'], cell_data['voltage'], cell_data['current'], cell_data['capacitance']]
    colors = ['#ff4d4d', '#4dd0e1', '#ffa726', '#2196f3']
    fig = go.Figure(data=[go.Bar(x=parameters, y=values, marker_color=colors, text=values, textposition='auto')])
    fig.update_layout(title=f"{cell_name}", plot_bgcolor='#121212', paper_bgcolor='#121212', font=dict(color='white'), height=300)
    fig.update_xaxes(gridcolor='#333'); fig.update_yaxes(gridcolor='#333')
    return fig

def compare_experiments_chart(experiments):
    fig = go.Figure()
    for exp_name, cells in experiments.items():
        avg_temp = np.mean([d['temp'] for d in cells.values()])
        avg_voltage = np.mean([d['voltage'] for d in cells.values()])
        fig.add_trace(go.Bar(name=f"{exp_name} - Temp", x=[exp_name], y=[avg_temp]))
        fig.add_trace(go.Bar(name=f"{exp_name} - Voltage", x=[exp_name], y=[avg_voltage]))
    fig.update_layout(barmode='group', plot_bgcolor='#121212', paper_bgcolor='#121212', font=dict(color='white'))
    return fig

# Sidebar
with st.sidebar:
    st.header("⚙️ Test Configuration")
    experiment_name = st.text_input("Experiment Name", value=f"Experiment_{len(st.session_state.experiments)+1}")
    experiment_type = st.selectbox("Experiment Type", ["Standard", "Overcharge Test", "Thermal Stress"])
    st.session_state.num_cells = st.number_input("Number of Cells", min_value=1, max_value=20, value=st.session_state.num_cells, step=1)
    bench_name = st.text_input("Bench Name", value="Bench_001")
    group_name = st.text_input("Group Name", value="Group_A")
    primary_cell_type = st.selectbox("Primary Cell Type", ["NMC", "LFP"])

    if st.button("Randomize All Values", type="primary"):
        cells_data = {}
        for i in range(st.session_state.num_cells):
            cell_type = random.choice(["NMC", "LFP"])
            defaults = get_default_values(cell_type)
            cells_data[f"Cell {i+1}"] = {"Cell Type":cell_type,**defaults}
        st.session_state.experiments[experiment_name] = cells_data
        st.success(f"{experiment_name} data randomized and saved!")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Input", "📈 Visualization", "📑 Insights & Export", "🔍 Compare Experiments"])

# Data Input Tab
with tab1:
    st.header("Cell Testing Data Input")
    if experiment_name not in st.session_state.experiments:
        st.session_state.experiments[experiment_name] = {}
    for i in range(st.session_state.num_cells):
        cols = st.columns(5)
        cell_label = f"Cell {i+1}"
        cell_type = cols[0].selectbox(f"Type {i+1}",["NMC","LFP"],key=f"type_{i}")
        defaults = get_default_values(cell_type)
        temp = cols[1].number_input(f"T {i+1}",0.0,100.0,value=defaults["temp"],step=0.1,key=f"temp_{i}")
        current = cols[2].number_input(f"I {i+1}",0.0,20.0,value=defaults["current"],step=0.01,key=f"curr_{i}")
        voltage = cols[3].number_input(f"V {i+1}",0.0,5.0,value=defaults["voltage"],step=0.01,key=f"volt_{i}")
        cap = cols[4].number_input(f"C {i+1}",0.0,10000.0,value=defaults["capacitance"],step=1.0,key=f"cap_{i}")
        st.session_state.experiments[experiment_name][cell_label] = {"Cell Type":cell_type,"temp":temp,"current":current,"voltage":voltage,"capacitance":cap,
                                                                     "max_voltage":defaults["max_voltage"],"min_voltage":defaults["min_voltage"]}

# Visualization Tab
with tab2:
    st.header(f"Visualization for {experiment_name}")
    if experiment_name in st.session_state.experiments:
        df = pd.DataFrame([
            {"Cell":c,"Cell Type":d["Cell Type"],"Temperature":d["temp"],"Voltage":d["voltage"],
             "Current":d["current"],"Capacitance":d["capacitance"]}
            for c,d in st.session_state.experiments[experiment_name].items()
        ])
        st.plotly_chart(create_overview_charts(df), use_container_width=True)

        st.subheader("Cell-wise Analysis")
        cell_cols = [st.columns(4) for _ in range((st.session_state.num_cells+3)//4)]
        for i,(cell_name,cell_data) in enumerate(st.session_state.experiments[experiment_name].items()):
            row = i // 4
            col = i % 4
            with cell_cols[row][col]:
                st.plotly_chart(create_individual_cell_chart(cell_data, cell_name), use_container_width=True)
    else:
        st.warning("Please enter data in Data Input tab.")

# Insights & Export Tab
with tab3:
    st.header("Insights & CSV Export")
    if experiment_name in st.session_state.experiments:
        df = pd.DataFrame([
            {"Cell":c,"Type":d["Cell Type"],"Temperature":d["temp"],"Voltage":d["voltage"],
             "Current":d["current"],"Capacitance":d["capacitance"]}
            for c,d in st.session_state.experiments[experiment_name].items()
        ])
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Data as CSV",data=csv,file_name=f"{experiment_name}.csv",mime="text/csv")
    else:
        st.info("No experiment data to export.")

# Compare Experiments Tab
with tab4:
    st.header("Experiment Comparison")
    if len(st.session_state.experiments) > 1:
        st.plotly_chart(compare_experiments_chart(st.session_state.experiments), use_container_width=True)
    else:
        st.info("Add more than one experiment to compare.")
