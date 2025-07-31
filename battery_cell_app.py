import streamlit as st
import pandas as pd
import random
import numpy as np


# Configure page
st.set_page_config(
    page_title="Battery Cell Testing Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        background-color: #1e1e1e;
    }
    
    .stSelectbox > div > div {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .stNumberInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .stDataFrame {
        background-color: #2d2d2d;
    }
    
    .metric-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #404040;
        margin-bottom: 1rem;
    }
    
    .highlight-high {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    .highlight-low {
        color: #4ecdc4;
        font-weight: bold;
    }
    
    .highlight-warning {
        color: #ffa726;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}

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
st.title("🔋 Battery Cell Testing Dashboard")
st.markdown("---")

# Sidebar for main inputs
with st.sidebar:
    st.header("Test Configuration")
    bench_name = st.text_input("Bench Name", value="Bench_001")
    group_name = st.text_input("Group Name", value="Group_A")
    primary_cell_type = st.selectbox("Primary Cell Type", ["NMC", "LFP"])
    
    st.markdown("---")
    if st.button("🔄 Randomize All Values", type="primary"):
        for i in range(8):
            cell_type = random.choice(["NMC", "LFP"])
            defaults = get_default_values(cell_type)
            st.session_state.cells_data[f"cell_{i+1}"] = {
                "cell_type": cell_type,
                **defaults
            }
        st.rerun()

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["📝 Data Input", "📊 Visualizations", "🔍 Insights"])

with tab1:
    st.header("Cell Testing Data Input")
    st.markdown("Enter data for 8 cell slots:")
    
    # Create columns for input table
    cols = st.columns([1, 2, 2, 2, 2, 2])
    
    # Headers
    cols[0].markdown("**Slot**")
    cols[1].markdown("**Cell Type**")
    cols[2].markdown("**Temperature (°C)**")
    cols[3].markdown("**Current (A)**")
    cols[4].markdown("**Voltage (V)**")
    cols[5].markdown("**Capacitance (mAh)**")
    
    # Input rows
    for i in range(8):
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
                value=defaults["temp"],
                step=0.1,
                key=f"temp_{i}",
                label_visibility="collapsed"
            )
        
        with cols[3]:
            current = st.number_input(
                f"Current {i+1}",
                min_value=0.0,
                max_value=20.0,
                value=defaults["current"],
                step=0.01,
                key=f"current_{i}",
                label_visibility="collapsed"
            )
        
        with cols[4]:
            voltage = st.number_input(
                f"Voltage {i+1}",
                min_value=0.0,
                max_value=5.0,
                value=defaults["voltage"],
                step=0.01,
                key=f"voltage_{i}",
                label_visibility="collapsed"
            )
        
        with cols[5]:
            capacitance = st.number_input(
                f"Capacitance {i+1}",
                min_value=0.0,
                max_value=10000.0,
                value=defaults["capacitance"],
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
        
        # Create 2x4 grid for individual charts
        rows = [st.columns(4) for _ in range(2)]
        
        for i, (cell_name, cell_data) in enumerate(st.session_state.cells_data.items()):
            row = i // 4
            col = i % 4
            
            with rows[row][col]:
                individual_fig = create_individual_cell_chart(cell_data, cell_name.replace('_', ' ').title())
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
        st.subheader("🌡️ Temperature Analysis")
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
        st.subheader("⚡ Voltage Analysis")
        
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
                    <h4>⚠️ Cells Outside Nominal Range</h4>
                    <p class="highlight-warning">{cells_str}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>✅ Voltage Status</h4>
                    <p>All cells within nominal range</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Capacity analysis
        st.subheader("🔋 Capacity Analysis")
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
        st.subheader("📋 Summary Table")
        summary_data = []
        for i, (cell_name, data) in enumerate(st.session_state.cells_data.items()):
            summary_data.append({
                'Cell': f"Cell {i+1}",
                'Type': data['cell_type'],
                'Temperature (°C)': data['temp'],
                'Voltage (V)': data['voltage'],
                'Current (A)': data['current'],
                'Capacitance (mAh)': data['capacitance'],
                'Status': '⚠️ Out of Range' if f"Cell {i+1}" in out_of_range_cells else '✅ Normal'
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
    else:
        st.info("Please enter cell data in the Data Input tab to see insights.")

# Footer
st.markdown("---")
st.markdown(f"**Test Configuration:** {bench_name} | {group_name} | Primary Type: {primary_cell_type}")
