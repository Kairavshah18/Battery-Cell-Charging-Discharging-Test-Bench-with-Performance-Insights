import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np
from datetime import datetime
import io

# Configure page
st.set_page_config(
    page_title="Battery Cell Testing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        background: transparent;
        max-width: 95%;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e1e3e 0%, #2a2a4a 100%);
        border-right: 2px solid #3a3a5a;
    }
    
    /* Enhanced form controls */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #2a2a4a, #1e1e3e);
        color: #ffffff;
        border: 1px solid #4a4a6a;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #2a2a4a, #1e1e3e);
        color: #ffffff;
        border: 1px solid #4a4a6a;
        border-radius: 8px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #64b5f6;
        box-shadow: 0 0 10px rgba(100, 181, 246, 0.3);
    }
    
    .stNumberInput > div > div > input {
        background: linear-gradient(145deg, #2a2a4a, #1e1e3e);
        color: #ffffff;
        border: 1px solid #4a4a6a;
        border-radius: 8px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #64b5f6;
        box-shadow: 0 0 10px rgba(100, 181, 246, 0.3);
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(145deg, #4a90e2, #357abd);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        transition: all 0.3s ease;
        transform: translateY(0);
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #357abd, #2968a3);
        box-shadow: 0 6px 16px rgba(74, 144, 226, 0.4);
        transform: translateY(-2px);
    }
    
    /* Secondary buttons for presets */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(145deg, #6a4c93, #553c7b);
        box-shadow: 0 4px 12px rgba(106, 76, 147, 0.3);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(145deg, #553c7b, #4a3269);
        box-shadow: 0 6px 16px rgba(106, 76, 147, 0.4);
    }
    
    /* Enhanced data display */
    .stDataFrame {
        background: linear-gradient(145deg, #2a2a4a, #1e1e3e);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        border: 1px solid #4a4a6a;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(145deg, #2a2a4a, #1e1e3e);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #4a4a6a;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #64b5f6, #4fc3f7, #29b6f6);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
    }
    
    .metric-card h4 {
        color: #b0bec5;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced highlights */
    .highlight-high {
        color: #ff5722;
        font-weight: 700;
        font-size: 1.2rem;
        text-shadow: 0 0 10px rgba(255, 87, 34, 0.3);
    }
    
    .highlight-low {
        color: #00e676;
        font-weight: 700;
        font-size: 1.2rem;
        text-shadow: 0 0 10px rgba(0, 230, 118, 0.3);
    }
    
    .highlight-warning {
        color: #ffc107;
        font-weight: 700;
        font-size: 1.2rem;
        text-shadow: 0 0 10px rgba(255, 193, 7, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(145deg, #2a2a4a, #1e1e3e);
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #4a4a6a;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #b0bec5;
        font-weight: 500;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #4a90e2, #357abd);
        color: white;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
    }
    
    /* Headers styling */
    h1, h2, h3 {
        background: linear-gradient(135deg, #64b5f6, #42a5f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Input headers */
    .stColumns > div > div > p > strong {
        color: #64b5f6;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(145deg, #43a047, #2e7d32);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(67, 160, 71, 0.3);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(145deg, #2e7d32, #1b5e20);
        box-shadow: 0 6px 16px rgba(67, 160, 71, 0.4);
        transform: translateY(-2px);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e1e3e;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(145deg, #4a4a6a, #3a3a5a);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(145deg, #5a5a7a, #4a4a6a);
    }
    
    /* Info box styling */
    .stAlert {
        background: linear-gradient(145deg, #1a237e, #283593);
        border: 1px solid #3949ab;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(25, 35, 126, 0.3);
    }
    
    /* Animation for metric cards */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card {
        animation: slideInUp 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'num_cells' not in st.session_state:
    st.session_state.num_cells = 8

def get_default_values(cell_type):
    """Get default values based on cell type"""
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

def get_preset_values(mode, cell_type):
    """Get preset values based on testing mode and cell type"""
    presets = {
        "charging": {
            "LFP": {
                "voltage": 3.3,
                "temp": 28.0,
                "current": 2.5,
                "capacitance": 3200
            },
            "NMC": {
                "voltage": 3.8,
                "temp": 30.0,
                "current": 3.0,
                "capacitance": 3400
            }
        },
        "discharging": {
            "LFP": {
                "voltage": 3.1,
                "temp": 35.0,
                "current": 4.0,
                "capacitance": 2800
            },
            "NMC": {
                "voltage": 3.4,
                "temp": 38.0,
                "current": 4.5,
                "capacitance": 3000
            }
        },
        "performance": {
            "LFP": {
                "voltage": 3.25,
                "temp": 45.0,
                "current": 6.0,
                "capacitance": 3000
            },
            "NMC": {
                "voltage": 3.7,
                "temp": 42.0,
                "current": 7.0,
                "capacitance": 3200
            }
        }
    }
    
    base_values = get_default_values(cell_type)
    preset_values = presets[mode][cell_type]
    
    return {
        **base_values,
        **preset_values
    }

def apply_preset_to_all_cells(mode):
    """Apply preset values to all cells"""
    for i in range(st.session_state.num_cells):
        cell_type = st.session_state.get(f"type_{i}", "NMC")
        preset_values = get_preset_values(mode, cell_type)
        
        st.session_state.cells_data[f"cell_{i+1}"] = {
            "cell_type": cell_type,
            **preset_values
        }

def update_cell_count(new_count):
    """Update the number of cells and adjust data accordingly"""
    old_count = st.session_state.num_cells
    st.session_state.num_cells = new_count
    
    # If increasing cell count, add new cells with default values
    if new_count > old_count:
        for i in range(old_count, new_count):
            cell_type = "NMC"  # Default type for new cells
            defaults = get_default_values(cell_type)
            st.session_state.cells_data[f"cell_{i+1}"] = {
                "cell_type": cell_type,
                **defaults
            }
    
    # If decreasing cell count, remove excess cells
    elif new_count < old_count:
        for i in range(new_count, old_count):
            if f"cell_{i+1}" in st.session_state.cells_data:
                del st.session_state.cells_data[f"cell_{i+1}"]

def export_to_csv():
    """Export current data to CSV format"""
    if not st.session_state.cells_data:
        return None
    
    export_data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for i in range(st.session_state.num_cells):
        cell_key = f"cell_{i+1}"
        if cell_key in st.session_state.cells_data:
            data = st.session_state.cells_data[cell_key]
            export_data.append({
                'Timestamp': timestamp,
                'Bench_Name': st.session_state.get('bench_name', 'Bench_001'),
                'Group_Name': st.session_state.get('group_name', 'Group_A'),
                'Cell_Slot': i + 1,
                'Cell_Type': data['cell_type'],
                'Temperature_C': data['temp'],
                'Voltage_V': data['voltage'],
                'Current_A': data['current'],
                'Capacitance_mAh': data['capacitance'],
                'Max_Voltage_V': data['max_voltage'],
                'Min_Voltage_V': data['min_voltage'],
                'Voltage_Status': 'Out_of_Range' if (data['voltage'] < data['min_voltage'] or data['voltage'] > data['max_voltage']) else 'Normal'
            })
    
    return pd.DataFrame(export_data)

def create_overview_charts(df):
    """Create overview charts for all parameters"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature vs Cell Slot', 'Voltage vs Cell Slot', 
                       'Capacitance vs Cell Slot', 'Current vs Cell Slot'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Temperature chart
    fig.add_trace(
        go.Scatter(x=df['Cell_Slot'], y=df['Temperature'], 
                  mode='lines+markers', name='Temperature',
                  line=dict(color='#ff6b6b', width=3),
                  marker=dict(size=8)),
        row=1, col=1
    )
    
    # Voltage chart
    fig.add_trace(
        go.Scatter(x=df['Cell_Slot'], y=df['Voltage'], 
                  mode='lines+markers', name='Voltage',
                  line=dict(color='#4ecdc4', width=3),
                  marker=dict(size=8)),
        row=1, col=2
    )
    
    # Capacitance chart
    fig.add_trace(
        go.Scatter(x=df['Cell_Slot'], y=df['Capacitance'], 
                  mode='lines+markers', name='Capacitance',
                  line=dict(color='#45b7d1', width=3),
                  marker=dict(size=8)),
        row=2, col=1
    )
    
    # Current chart
    fig.add_trace(
        go.Scatter(x=df['Cell_Slot'], y=df['Current'], 
                  mode='lines+markers', name='Current',
                  line=dict(color='#ffa726', width=3),
                  marker=dict(size=8)),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='white'),
        title_font=dict(color='white')
    )
    
    fig.update_xaxes(gridcolor='#404040', title_font=dict(color='white'))
    fig.update_yaxes(gridcolor='#404040', title_font=dict(color='white'))
    
    return fig

def create_individual_cell_chart(cell_data, cell_name):
    """Create individual cell parameter chart"""
    parameters = ['Temperature', 'Voltage', 'Current', 'Capacitance']
    values = [cell_data['temp'], cell_data['voltage'], 
             cell_data['current'], cell_data['capacitance']]
    colors = ['#ff6b6b', '#4ecdc4', '#ffa726', '#45b7d1']
    
    fig = go.Figure(data=[
        go.Bar(x=parameters, y=values, marker_color=colors,
               text=values, textposition='auto')
    ])
    
    fig.update_layout(
        title=f"Parameters for {cell_name}",
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='white'),
        title_font=dict(color='white'),
        height=400
    )
    
    fig.update_xaxes(gridcolor='#404040', title_font=dict(color='white'))
    fig.update_yaxes(gridcolor='#404040', title_font=dict(color='white'))
    
    return fig

# Main App
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 50%, #2196f3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        Battery Cell Testing Dashboard
    </h1>
    <p style="color: #b0bec5; font-size: 1.2rem; font-weight: 300;">Advanced Battery Analysis & Monitoring System</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Sidebar for main inputs
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <h2 style="background: linear-gradient(135deg, #64b5f6, #42a5f5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem;">
            Control Panel
        </h2>
        <div style="height: 2px; background: linear-gradient(90deg, #64b5f6, #42a5f5); border-radius: 1px; margin: 0 2rem;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Test Configuration")
    bench_name = st.text_input("Bench Name", value="Bench_001", key="bench_name")
    group_name = st.text_input("Group Name", value="Group_A", key="group_name")
    primary_cell_type = st.selectbox("Primary Cell Type", ["NMC", "LFP"])
    
    # Cell count configuration
    st.markdown("---")
    st.subheader("Cell Configuration")
    new_cell_count = st.selectbox(
        "Number of Cells",
        options=[4, 8, 12, 16, 20, 24],
        index=1,  # Default to 8 cells
        key="cell_count_selector"
    )
    
    if new_cell_count != st.session_state.num_cells:
        update_cell_count(new_cell_count)
        st.rerun()
    
    # Testing mode presets
    st.markdown("---")
    st.subheader("Testing Mode Presets")
    st.markdown("""
    <div style="background: linear-gradient(145deg, #2a2a4a, #1e1e3e); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #4a4a6a;">
        <p style="color: #b0bec5; font-size: 0.9rem; margin-bottom: 1rem;">Quick preset configurations for different testing scenarios</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Charging Mode", type="secondary", key="charging_preset"):
            apply_preset_to_all_cells("charging")
            st.rerun()
    
    with col2:
        if st.button("🔋 Discharging Mode", type="secondary", key="discharging_preset"):
            apply_preset_to_all_cells("discharging")
            st.rerun()
    
    if st.button("🏎️ Performance Mode", type="secondary", key="performance_preset"):
        apply_preset_to_all_cells("performance")
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(145deg, #4a90e2, #357abd); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
        <p style="color: white; font-size: 0.9rem; margin-bottom: 0; text-align: center; font-weight: 500;">🎲 Generate Random Test Data</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Randomize All Values", type="primary"):
        for i in range(st.session_state.num_cells):
            cell_type = random.choice(["NMC", "LFP"])
            
            # Randomize voltage within cell type specific ranges with more variation
            if cell_type == "LFP":
                voltage_range = (2.8, 3.4)
                base_voltage = 3.2
            else:  # NMC
                voltage_range = (3.2, 4.0)
                base_voltage = 3.6
            
            # Add more randomization to voltage
            voltage = round(random.uniform(voltage_range[0], voltage_range[1]), 2)
            
            # Randomize other parameters with wider ranges
            temp = round(random.uniform(20, 50), 1)
            current = round(random.uniform(0.5, 8.0), 2)
            
            if cell_type == "LFP":
                capacitance = round(random.uniform(2000, 4000), 0)
                max_voltage = 3.4
                min_voltage = 2.8
            else:  # NMC
                capacitance = round(random.uniform(2200, 4200), 0)
                max_voltage = 4.0
                min_voltage = 3.2
            
            st.session_state.cells_data[f"cell_{i+1}"] = {
                "cell_type": cell_type,
                "voltage": voltage,
                "temp": temp,
                "current": current,
                "capacitance": capacitance,
                "max_voltage": max_voltage,
                "min_voltage": min_voltage
            }
        st.rerun()
    
    # Export section
    st.markdown("---")
    st.subheader("Data Export")
    st.markdown("""
    <div style="background: linear-gradient(145deg, #43a047, #2e7d32); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
        <p style="color: white; font-size: 0.9rem; margin-bottom: 0; text-align: center; font-weight: 500;">📊 Export Test Results</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Export to CSV", type="primary"):
        csv_data = export_to_csv()
        if csv_data is not None:
            csv_string = csv_data.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"battery_test_data_{timestamp}.csv"
            
            st.download_button(
                label="📥 Download CSV File",
                data=csv_string,
                file_name=filename,
                mime="text/csv",
                key="download_csv"
            )
        else:
            st.error("No data available to export")

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Data Input", "Visualizations", "Insights", "Export Data"])

with tab1:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="background: linear-gradient(135deg, #64b5f6, #42a5f5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            Cell Testing Data Input
        </h2>
        <p style="color: #b0bec5;">Configure parameters for {} cell slots</p>
    </div>
    """.format(st.session_state.num_cells), unsafe_allow_html=True)
    
    # Create enhanced header row
    st.markdown("""
    <div style="background: linear-gradient(145deg, #2a2a4a, #1e1e3e); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #4a4a6a;">
        <div style="display: grid; grid-template-columns: 1fr 2fr 2fr 2fr 2fr 2fr; gap: 1rem; text-align: center;">
            <div><strong style="color: #64b5f6;">SLOT</strong></div>
            <div><strong style="color: #64b5f6;">CELL TYPE</strong></div>
            <div><strong style="color: #ff5722;">TEMP (°C)</strong></div>
            <div><strong style="color: #ffc107;">CURRENT (A)</strong></div>
            <div><strong style="color: #4caf50;">VOLTAGE (V)</strong></div>
            <div><strong style="color: #2196f3;">CAPACITY (mAh)</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for input table
    cols = st.columns([1, 2, 2, 2, 2, 2])
    
    # Input rows
    for i in range(st.session_state.num_cells):
        cols = st.columns([1, 2, 2, 2, 2, 2])
        
        with cols[0]:
            st.markdown(f"**{i+1}**")
        
        with cols[1]:
            cell_type = st.selectbox(
                f"Type {i+1}",
                ["NMC", "LFP"],
                key=f"type_{i}",
                label_visibility="collapsed"
            )
        
        # Get defaults for current cell type
        defaults = get_default_values(cell_type)
        
        with cols[2]:
            temp = st.number_input(
                f"Temp {i+1}",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.cells_data.get(f"cell_{i+1}", {}).get("temp", defaults["temp"]),
                step=0.1,
                key=f"temp_{i}",
                label_visibility="collapsed"
            )
        
        with cols[3]:
            current = st.number_input(
                f"Current {i+1}",
                min_value=0.0,
                max_value=20.0,
                value=st.session_state.cells_data.get(f"cell_{i+1}", {}).get("current", defaults["current"]),
                step=0.01,
                key=f"current_{i}",
                label_visibility="collapsed"
            )
        
        with cols[4]:
            voltage = st.number_input(
                f"Voltage {i+1}",
                min_value=0.0,
                max_value=5.0,
                value=st.session_state.cells_data.get(f"cell_{i+1}", {}).get("voltage", defaults["voltage"]),
                step=0.01,
                key=f"voltage_{i}",
                label_visibility="collapsed"
            )
        
        with cols[5]:
            capacitance = st.number_input(
                f"Capacitance {i+1}",
                min_value=0.0,
                max_value=10000.0,
                value=st.session_state.cells_data.get(f"cell_{i+1}", {}).get("capacitance", defaults["capacitance"]),
                step=1.0,
                key=f"capacitance_{i}",
                label_visibility="collapsed"
            )
        
        # Store data in session state
        st.session_state.cells_data[f"cell_{i+1}"] = {
            "cell_type": cell_type,
            "temp": temp,
            "current": current,
            "voltage": voltage,
            "capacitance": capacitance,
            "max_voltage": defaults["max_voltage"],
            "min_voltage": defaults["min_voltage"]
        }

with tab2:
    st.header("Data Visualizations")
    
    if st.session_state.cells_data:
        # Prepare data for charts
        chart_data = []
        for slot, data in st.session_state.cells_data.items():
            chart_data.append({
                'Cell_Slot': slot.replace('cell_', 'Cell '),
                'Cell_Type': data['cell_type'],
                'Temperature': data['temp'],
                'Voltage': data['voltage'],
                'Current': data['current'],
                'Capacitance': data['capacitance']
            })
        
        df = pd.DataFrame(chart_data)
        
        # Overview charts
        st.subheader("Overview Charts")
        overview_fig = create_overview_charts(df)
        st.plotly_chart(overview_fig, use_container_width=True)
        
        # Individual cell charts
        st.subheader("Individual Cell Analysis")
        
        # Calculate number of columns and rows needed
        cols_per_row = 4
        num_rows = (st.session_state.num_cells + cols_per_row - 1) // cols_per_row
        
        # Create dynamic grid for individual charts
        for row in range(num_rows):
            cols = st.columns(cols_per_row)
            for col in range(cols_per_row):
                cell_index = row * cols_per_row + col
                if cell_index < st.session_state.num_cells:
                    cell_name = f"cell_{cell_index + 1}"
                    if cell_name in st.session_state.cells_data:
                        with cols[col]:
                            individual_fig = create_individual_cell_chart(
                                st.session_state.cells_data[cell_name], 
                                cell_name.replace('_', ' ').title()
                            )
                            st.plotly_chart(individual_fig, use_container_width=True)
    
    else:
        st.info("Please enter cell data in the Data Input tab to see visualizations.")

with tab3:
    st.header("Test Insights & Analysis")
    
    if st.session_state.cells_data:
        # Calculate insights
        temps = [data['temp'] for data in st.session_state.cells_data.values()]
        voltages = [data['voltage'] for data in st.session_state.cells_data.values()]
        capacitances = [data['capacitance'] for data in st.session_state.cells_data.values()]
        currents = [data['current'] for data in st.session_state.cells_data.values()]
        
        # Temperature analysis
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3 style="background: linear-gradient(135deg, #ff5722, #ff7043); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                🌡️ Temperature Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_temp_idx = temps.index(max(temps))
            max_temp_cell = f"Cell {max_temp_idx + 1}"
            st.markdown(f"""
            <div class="metric-card">
                <h4>Highest Temperature</h4>
                <p class="highlight-high">{max_temp_cell}: {max(temps):.1f}°C</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            min_temp_idx = temps.index(min(temps))
            min_temp_cell = f"Cell {min_temp_idx + 1}"
            st.markdown(f"""
            <div class="metric-card">
                <h4>Lowest Temperature</h4>
                <p class="highlight-low">{min_temp_cell}: {min(temps):.1f}°C</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_temp = np.mean(temps)
            st.markdown(f"""
            <div class="metric-card">
                <h4>Average Temperature</h4>
                <p>{avg_temp:.1f}°C</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Voltage analysis
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3 style="background: linear-gradient(135deg, #4caf50, #66bb6a); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                ⚡ Voltage Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Check for cells outside nominal range
        out_of_range_cells = []
        for i, (cell_name, data) in enumerate(st.session_state.cells_data.items()):
            if data['voltage'] < data['min_voltage'] or data['voltage'] > data['max_voltage']:
                out_of_range_cells.append(f"Cell {i+1}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            avg_voltage = np.mean(voltages)
            st.markdown(f"""
            <div class="metric-card">
                <h4>Average Voltage</h4>
                <p>{avg_voltage:.2f}V</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if out_of_range_cells:
                cells_str = ", ".join(out_of_range_cells)
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Cells Outside Nominal Range</h4>
                    <p class="highlight-warning">{cells_str}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Voltage Status</h4>
                    <p>All cells within nominal range</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Capacity analysis
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3 style="background: linear-gradient(135deg, #2196f3, #42a5f5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                🔋 Capacity Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_capacity = np.mean(capacitances)
            st.markdown(f"""
            <div class="metric-card">
                <h4>Average Capacity</h4>
                <p>{avg_capacity:.0f} mAh</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            max_capacity_idx = capacitances.index(max(capacitances))
            max_capacity_cell = f"Cell {max_capacity_idx + 1}"
            st.markdown(f"""
            <div class="metric-card">
                <h4>Highest Capacity</h4>
                <p class="highlight-high">{max_capacity_cell}: {max(capacitances):.0f} mAh</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            min_capacity_idx = capacitances.index(min(capacitances))
            min_capacity_cell = f"Cell {min_capacity_idx + 1}"
            st.markdown(f"""
            <div class="metric-card">
                <h4>Lowest Capacity</h4>
                <p class="highlight-low">{min_capacity_cell}: {min(capacitances):.0f} mAh</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary table
        st.subheader("Summary Table")
        summary_data = []
        for i, (cell_name, data) in enumerate(st.session_state.cells_data.items()):
            summary_data.append({
                'Cell': f"Cell {i+1}",
                'Type': data['cell_type'],
                'Temperature (°C)': data['temp'],
                'Voltage (V)': data['voltage'],
                'Current (A)': data['current'],
                'Capacitance (mAh)': data['capacitance'],
                'Status': 'Out of Range' if f"Cell {i+1}" in out_of_range_cells else 'Normal'
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
    else:
        st.info("Please enter cell data in the Data Input tab to see insights.")

with tab4:
    st.header("Export Data")
    
    if st.session_state.cells_data:
        st.subheader("Current Test Data")
        
        # Display current configuration
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bench Name", bench_name)
        with col2:
            st.metric("Group Name", group_name)
        with col3:
            st.metric("Number of Cells", st.session_state.num_cells)
        
        # Show preview of export data
        st.subheader("Export Preview")
        export_preview = export_to_csv()
        if export_preview is not None:
            st.dataframe(export_preview, use_container_width=True)
            
            # Export options
            st.subheader("Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                csv_string = export_preview.to_csv(index=False)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"battery_test_data_{timestamp}.csv"
                
                st.download_button(
                    label="Download Complete Dataset",
                    data=csv_string,
                    file_name=filename,
                    mime="text/csv",
                    type="primary"
                )
            
            with col2:
                # Export only summary statistics
                summary_stats = {
                    'Parameter': ['Temperature', 'Voltage', 'Current', 'Capacitance'],
                    'Average': [
                        np.mean([data['temp'] for data in st.session_state.cells_data.values()]),
                        np.mean([data['voltage'] for data in st.session_state.cells_data.values()]),
                        np.mean([data['current'] for data in st.session_state.cells_data.values()]),
                        np.mean([data['capacitance'] for data in st.session_state.cells_data.values()])
                    ],
                    'Min': [
                        np.min([data['temp'] for data in st.session_state.cells_data.values()]),
                        np.min([data['voltage'] for data in st.session_state.cells_data.values()]),
                        np.min([data['current'] for data in st.session_state.cells_data.values()]),
                        np.min([data['capacitance'] for data in st.session_state.cells_data.values()])
                    ],
                    'Max': [
                        np.max([data['temp'] for data in st.session_state.cells_data.values()]),
                        np.max([data['voltage'] for data in st.session_state.cells_data.values()]),
                        np.max([data['current'] for data in st.session_state.cells_data.values()]),
                        np.max([data['capacitance'] for data in st.session_state.cells_data.values()])
                    ]
                }
                
                summary_df = pd.DataFrame(summary_stats)
                summary_csv = summary_df.to_csv(index=False)
                summary_filename = f"battery_test_summary_{timestamp}.csv"
                
                st.download_button(
                    label="Download Summary Statistics",
                    data=summary_csv,
                    file_name=summary_filename,
                    mime="text/csv",
                    type="secondary"
                )
        
        st.subheader("Export Information")
        st.info("""
        **Complete Dataset includes:**
        - Timestamp, bench and group information
        - Individual cell measurements
        - Voltage status (Normal/Out of Range)
        - Cell type and operational limits
        
        **Summary Statistics includes:**
        - Average, minimum, and maximum values
        - Aggregated data across all cells
        """)
        
    else:
        st.info("No data available to export. Please enter cell data in the Data Input tab.")

# Footer
st.markdown("---")
st.markdown(f"**Test Configuration:** {bench_name} | {group_name} | Primary Type: {primary_cell_type} | Cells: {st.session_state.num_cells}")
