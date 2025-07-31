import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# Configure page
st.set_page_config(page_title="Battery Cell Testing Dashboard", layout="wide")

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
        background-color: #121212;
    }
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border: 1px solid #333333;
        border-radius: 5px;
    }
    .stDataFrame {
        background-color: #1E1E1E;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333333;
        margin-bottom: 1rem;
        box-shadow: 0 0 10px #222;
    }
    .highlight-high {
        color: #FF6B6B;
        font-weight: 600;
    }
    .highlight-low {
        color: #4ECDC4;
        font-weight: 600;
    }
    .highlight-warning {
        color: #FFA726;
        font-weight: 600;
    }
    .btn-randomize {
        background-color: #4ECDC4;
        color: #121212;
        font-weight: 700;
        border-radius: 5px;
        padding: 8px 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state containers
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}

if 'experiments' not in st.session_state:
    st.session_state.experiments = {}

if 'current_experiment_name' not in st.session_state:
    st.session_state.current_experiment_name = "Default Experiment"

if st.session_state.current_experiment_name not in st.session_state.experiments:
    st.session_state.experiments[st.session_state.current_experiment_name] = {}

# Function to get default values by cell type
def get_default_values(cell_type):
    if cell_type == "LFP":
        return {
            "voltage": 3.2,
            "max_voltage": 3.4,
            "min_voltage": 2.8,
            "temp": round(random.uniform(25, 40), 1),
            "current": round(random.uniform(1.0, 5.0), 2),
            "capacitance": round(random.uniform(2500, 3500), 0)
        }
    else:  # NMC
        return {
            "voltage": 3.6,
            "max_voltage": 4.0,
            "min_voltage": 3.2,
            "temp": round(random.uniform(25, 40), 1),
            "current": round(random.uniform(1.0, 5.0), 2),
            "capacitance": round(random.uniform(2800, 3800), 0)
        }

# Function to generate realistic charging curve
def generate_charging_curve(voltage_start, voltage_max, capacity, current):
    charge_time_h = capacity / (current * 1000)  # convert mAh to Ah
    time = np.linspace(0, charge_time_h, 100)
    voltage = voltage_start + (voltage_max - voltage_start) / (1 + np.exp(-12 * (time/charge_time_h - 0.5)))
    noise = np.random.normal(0, 0.02, size=voltage.shape)
    voltage += noise
    voltage = np.clip(voltage, voltage_start, voltage_max)
    return time, voltage

# Function to generate realistic discharging curve
def generate_discharging_curve(voltage_max, voltage_min, capacity, current):
    discharge_time_h = capacity / (current * 1000)
    time = np.linspace(0, discharge_time_h, 100)
    voltage = voltage_min + (voltage_max - voltage_min) / (1 + np.exp(12 * (time/discharge_time_h - 0.5)))
    noise = np.random.normal(0, 0.02, size=voltage.shape)
    voltage += noise
    voltage = np.clip(voltage, voltage_min, voltage_max)
    return time, voltage

# Store data to current experiment
def update_experiment_data():
    data = {}
    for i in range(st.session_state.num_cells):
        key = f"cell_{i+1}"
        data[key] = st.session_state.cells_data.get(key, {})
    st.session_state.experiments[st.session_state.current_experiment_name] = data

# Load experiment data into cells_data session
def load_experiment_data(name):
    exp_data = st.session_state.experiments.get(name, {})
    st.session_state.cells_data = {k: v.copy() for k, v in exp_data.items()}

# Initialize number of cells, min 4 max 12
if 'num_cells' not in st.session_state:
    st.session_state.num_cells = 8

# Sidebar controls
with st.sidebar:
    st.header("Test Configuration")
    bench_name = st.text_input("Bench Name", value="Bench_001")
    group_name = st.text_input("Group Name", value="Group_A")
    primary_cell_type = st.selectbox("Primary Cell Type", ["NMC", "LFP"])
    
    st.markdown("---")
    st.number_input("Number of Cells", min_value=4, max_value=12, value=st.session_state.num_cells, step=1, key="num_cells")
    
    st.markdown("---")
    st.subheader("Experiments")
    
    exp_names = list(st.session_state.experiments.keys())
    if not exp_names:
        st.warning("No experiments found. Create a new experiment.")
        selected_exp = None
    else:
        try:
            selected_exp = st.selectbox("Select Experiment", exp_names, index=exp_names.index(st.session_state.current_experiment_name))
        except ValueError:
            selected_exp = exp_names[0]
    
    if st.button("Load Experiment") and selected_exp:
        if selected_exp in st.session_state.experiments:
            st.session_state.current_experiment_name = selected_exp
            load_experiment_data(selected_exp)
            st.experimental_rerun()
        else:
            st.error("Selected experiment not found.")
    
    new_exp_name = st.text_input("New Experiment Name", value="")
    if st.button("Create New Experiment") and new_exp_name.strip():
        if new_exp_name in st.session_state.experiments:
            st.warning("Experiment name already exists.")
        else:
            st.session_state.current_experiment_name = new_exp_name.strip()
            st.session_state.experiments[new_exp_name.strip()] = {}
            st.session_state.cells_data = {}
            st.experimental_rerun()
    
    if st.button("Save Current Experiment"):
        update_experiment_data()
        st.success(f"Experiment '{st.session_state.current_experiment_name}' saved.")

    st.markdown("---")
    if st.button("Randomize All Cell Values"):
        for i in range(st.session_state.num_cells):
            cell_type = random.choice(["NMC", "LFP"])
            defaults = get_default_values(cell_type)
            st.session_state.cells_data[f"cell_{i+1}"] = {
                "cell_type": cell_type,
                **defaults
            }
        update_experiment_data()
        st.experimental_rerun()

    st.markdown("---")
    if st.button("Export Current Experiment Data as CSV"):
        update_experiment_data()
        exp_data = st.session_state.experiments.get(st.session_state.current_experiment_name, {})
        rows = []
        for key, d in exp_data.items():
            rows.append({
                "Cell": key,
                "Type": d.get("cell_type", ""),
                "Temperature (°C)": d.get("temp", ""),
                "Voltage (V)": d.get("voltage", ""),
                "Max Voltage (V)": d.get("max_voltage", ""),
                "Min Voltage (V)": d.get("min_voltage", ""),
                "Current (A)": d.get("current", ""),
                "Capacity (mAh)": d.get("capacitance", "")
            })
        df_export = pd.DataFrame(rows)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv_data, file_name=f"{st.session_state.current_experiment_name}.csv", mime='text/csv')

# Tabs: Data Input, Visualizations, Charging Profiles, Discharging Profiles, Insights
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Data Input", "Visualizations", "Charging Profiles", "Discharging Profiles", "Insights"])

with tab1:
    st.header("Cell Testing Data Input")
    st.markdown(f"Enter data for {st.session_state.num_cells} cell slots:")
    
    for i in range(st.session_state.num_cells):
        key = f"cell_{i+1}"
        if key not in st.session_state.cells_data:
            defaults = get_default_values(primary_cell_type)
            st.session_state.cells_data[key] = {
                "cell_type": primary_cell_type,
                **defaults
            }
        data = st.session_state.cells_data[key]
        
        cols = st.columns([1,2,2,2,2,2])
        cols[0].markdown(f"**Cell {i+1}**")
        
        ctype = cols[1].selectbox(f"Type_{key}", ["NMC", "LFP"], index=0 if data.get("cell_type","NMC")=="NMC" else 1, key=f"type_{key}")
        st.session_state.cells_data[key]["cell_type"] = ctype
        
        defaults = get_default_values(ctype)
        
        temp = cols[2].number_input(f"Temp_{key}", min_value=0.0, max_value=100.0, value=data.get("temp", defaults["temp"]), step=0.1, key=f"temp_{key}")
        current = cols[3].number_input(f"Current_{key}", min_value=0.0, max_value=20.0, value=data.get("current", defaults["current"]), step=0.01, key=f"current_{key}")
        voltage = cols[4].number_input(f"Voltage_{key}", min_value=0.0, max_value=5.0, value=data.get("voltage", defaults["voltage"]), step=0.01, key=f"voltage_{key}")
        capacitance = cols[5].number_input(f"Capacity_{key}", min_value=0.0, max_value=20000.0, value=data.get("capacitance", defaults["capacitance"]), step=1.0, key=f"capacitance_{key}")

        st.session_state.cells_data[key].update({
            "temp": temp,
            "current": current,
            "voltage": voltage,
            "capacitance": capacitance,
            "max_voltage": defaults["max_voltage"],
            "min_voltage": defaults["min_voltage"]
        })

with tab2:
    st.header("Data Visualizations")
    if st.session_state.cells_data:
        chart_data = []
        for i in range(st.session_state.num_cells):
            key = f"cell_{i+1}"
            d = st.session_state.cells_data.get(key, {})
            chart_data.append({
                "Cell_Slot": f"Cell {i+1}",
                "Cell_Type": d.get("cell_type",""),
                "Temperature": d.get("temp", 0),
                "Voltage": d.get("voltage", 0),
                "Current": d.get("current", 0),
                "Capacitance": d.get("capacitance", 0)
            })
        df = pd.DataFrame(chart_data)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperature vs Cell Slot', 'Voltage vs Cell Slot', 
                           'Capacitance vs Cell Slot', 'Current vs Cell Slot'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        fig.add_trace(go.Scatter(x=df["Cell_Slot"], y=df["Temperature"], mode='lines+markers', 
                                 name="Temperature", line=dict(color="#FF6B6B", width=3)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Cell_Slot"], y=df["Voltage"], mode='lines+markers', 
                                 name="Voltage", line=dict(color="#4ECDC4", width=3)), row=1, col=2)
        fig.add_trace(go.Scatter(x=df["Cell_Slot"], y=df["Capacitance"], mode='lines+markers', 
                                 name="Capacitance", line=dict(color="#45B7D1", width=3)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df["Cell_Slot"], y=df["Current"], mode='lines+markers', 
                                 name="Current", line=dict(color="#FFA726", width=3)), row=2, col=2)
        
        fig.update_layout(height=600, plot_bgcolor='#121212', paper_bgcolor='#121212',
                          font=dict(color='white'), showlegend=False)
        fig.update_xaxes(gridcolor='#333333')
        fig.update_yaxes(gridcolor='#333333')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Individual Cell Parameters")
        rows = [st.columns(4) for _ in range((st.session_state.num_cells + 3)//4)]
        for i in range(st.session_state.num_cells):
            row = i // 4
            col = i % 4
            key = f"cell_{i+1}"
            d = st.session_state.cells_data[key]
            parameters = ['Temperature', 'Voltage', 'Current', 'Capacitance']
            values = [d['temp'], d['voltage'], d['current'], d['capacitance']]
            colors = ['#FF6B6B', '#4ECDC4', '#FFA726', '#45B7D1']
            fig_ind = go.Figure(go.Bar(x=parameters, y=values, marker_color=colors, text=values, textposition='auto'))
            fig_ind.update_layout(height=350, plot_bgcolor='#121212', paper_bgcolor='#121212',
                                  font=dict(color='white'), title=f"Cell {i+1} Parameters")
            fig_ind.update_xaxes(gridcolor='#333333')
            fig_ind.update_yaxes(gridcolor='#333333')
            with rows[row][col]:
                st.plotly_chart(fig_ind, use_container_width=True)
    else:
        st.info("Enter cell data to see visualizations.")

with tab3:
    st.header("Charging Profiles")
    if st.session_state.cells_data:
        rows = [st.columns(2) for _ in range((st.session_state.num_cells + 1)//2)]
        for i in range(st.session_state.num_cells):
            row = i // 2
            col = i % 2
            key = f"cell_{i+1}"
            d = st.session_state.cells_data[key]
            time, voltage_curve = generate_charging_curve(
                voltage_start=d["voltage"]*0.9,
                voltage_max=d["max_voltage"],
                capacity=d["capacitance"],
                current=d["current"]
            )
            fig_chg = go.Figure(go.Scatter(x=time*60, y=voltage_curve, mode='lines+markers', line=dict(color="#4ECDC4", width=3)))
            fig_chg.update_layout(
                title=f"Charging Profile - Cell {i+1}",
                xaxis_title="Time (minutes)",
                yaxis_title="Voltage (V)",
                plot_bgcolor='#121212',
                paper_bgcolor='#121212',
                font=dict(color='white'),
                height=350,
                margin=dict(t=40, b=40)
            )
            fig_chg.update_xaxes(gridcolor='#333333')
            fig_chg.update_yaxes(gridcolor='#333333', range=[d["voltage"]*0.85, d["max_voltage"]+0.1])
            with rows[row][col]:
                st.plotly_chart(fig_chg, use_container_width=True)
    else:
        st.info("Enter cell data to generate charging profiles.")

with tab4:
    st.header("Discharging Profiles")
    if st.session_state.cells_data:
        rows = [st.columns(2) for _ in range((st.session_state.num_cells + 1)//2)]
        for i in range(st.session_state.num_cells):
            row = i // 2
            col = i % 2
            key = f"cell_{i+1}"
            d = st.session_state.cells_data[key]
            time, voltage_curve = generate_discharging_curve(
                voltage_max=d["voltage"],
                voltage_min=d["min_voltage"],
                capacity=d["capacitance"],
                current=d["current"]
            )
            fig_dis = go.Figure(go.Scatter(x=time*60, y=voltage_curve, mode='lines+markers', line=dict(color="#FF6B6B", width=3)))
            fig_dis.update_layout(
                title=f"Discharging Profile - Cell {i+1}",
                xaxis_title="Time (minutes)",
                yaxis_title="Voltage (V)",
                plot_bgcolor='#121212',
                paper_bgcolor='#121212',
                font=dict(color='white'),
                height=350,
                margin=dict(t=40, b=40)
            )
            fig_dis.update_xaxes(gridcolor='#333333')
            fig_dis.update_yaxes(gridcolor='#333333', range=[d["min_voltage"]-0.1, d["voltage"]*1.05])
            with rows[row][col]:
                st.plotly_chart(fig_dis, use_container_width=True)
    else:
        st.info("Enter cell data to generate discharging profiles.")

with tab5:
    st.header("Test Insights & Summary")
    if st.session_state.cells_data:
        temps = [st.session_state.cells_data[f"cell_{i+1}"]['temp'] for i in range(st.session_state.num_cells)]
        voltages = [st.session_state.cells_data[f"cell_{i+1}"]['voltage'] for i in range(st.session_state.num_cells)]
        currents = [st.session_state.cells_data[f"cell_{i+1}"]['current'] for i in range(st.session_state.num_cells)]
        capacities = [st.session_state.cells_data[f"cell_{i+1}"]['capacitance'] for i in range(st.session_state.num_cells)]
        
        avg_temp = np.mean(temps)
        avg_voltage = np.mean(voltages)
        avg_current = np.mean(currents)
        avg_capacity = np.mean(capacities)
        
        # Highlights for high/low
        max_temp = max(temps)
        min_temp = min(temps)
        max_voltage = max(voltages)
        min_voltage = min(voltages)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='metric-card'><h3>Temperature Summary (°C)</h3></div>", unsafe_allow_html=True)
            for i, temp in enumerate(temps):
                highlight = ""
                if temp >= 40:
                    highlight = "highlight-high"
                elif temp <= 25:
                    highlight = "highlight-low"
                st.markdown(f"Cell {i+1}: <span class='{highlight}'>{temp:.1f}</span>", unsafe_allow_html=True)
            st.markdown(f"**Average Temperature:** {avg_temp:.1f} °C")
            
        with col2:
            st.markdown("<div class='metric-card'><h3>Voltage Summary (V)</h3></div>", unsafe_allow_html=True)
            for i, volt in enumerate(voltages):
                highlight = ""
                if volt >= 4.0:
                    highlight = "highlight-high"
                elif volt <= 3.0:
                    highlight = "highlight-low"
                st.markdown(f"Cell {i+1}: <span class='{highlight}'>{volt:.2f}</span>", unsafe_allow_html=True)
            st.markdown(f"**Average Voltage:** {avg_voltage:.2f} V")
        
        st.markdown("---")
        
        # Additional Insights
        st.subheader("General Insights")
        warnings = []
        for i, temp in enumerate(temps):
            if temp > 45:
                warnings.append(f"Cell {i+1}: Temperature exceeds safe limit!")
        for i, volt in enumerate(voltages):
            if volt < 2.5:
                warnings.append(f"Cell {i+1}: Voltage too low, risk of deep discharge!")
        
        if warnings:
            for w in warnings:
                st.markdown(f"<p class='highlight-warning'>⚠️ {w}</p>", unsafe_allow_html=True)
        else:
            st.success("All cells are operating within safe parameters.")
    else:
        st.info("Enter cell data to see insights.")

# Save experiment data on exit or when changes happen
update_experiment_data()
