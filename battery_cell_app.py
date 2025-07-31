import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Battery Testing Dashboard", layout="wide")

# ---------------- INITIALIZE STATES ----------------
if 'experiments' not in st.session_state:
    st.session_state.experiments = {}
if 'current_experiment' not in st.session_state:
    st.session_state.current_experiment = {}
if 'experiment_name' not in st.session_state:
    st.session_state.experiment_name = "Experiment_1"
if 'num_cells' not in st.session_state:
    st.session_state.num_cells = 8

# ---------------- FUNCTIONS ----------------
def get_default_values(cell_type):
    if cell_type == "LFP":
        return {"voltage": 3.2, "max_voltage": 3.4, "min_voltage": 2.8,
                "temp": round(random.uniform(25, 40), 1),
                "current": round(random.uniform(1.0, 5.0), 2),
                "capacitance": round(random.uniform(2500, 3500), 0)}
    else:  # NMC
        return {"voltage": 3.6, "max_voltage": 4.0, "min_voltage": 3.2,
                "temp": round(random.uniform(25, 40), 1),
                "current": round(random.uniform(1.0, 5.0), 2),
                "capacitance": round(random.uniform(2800, 3800), 0)}

def create_overview_charts(df, title="Overview"):
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=('Temperature', 'Voltage', 'Capacitance', 'Current'))
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffa726']
    params = ['Temperature', 'Voltage', 'Capacitance', 'Current']
    for idx, param in enumerate(params):
        row, col = idx // 2 + 1, idx % 2 + 1
        fig.add_trace(go.Scatter(x=df['Cell'], y=df[param], mode='lines+markers', name=param,
                                 line=dict(color=colors[idx])), row=row, col=col)
    fig.update_layout(height=600, title=title, plot_bgcolor='#1e1e1e',
                      paper_bgcolor='#1e1e1e', font=dict(color='white'))
    return fig

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Experiment Controls")
    st.session_state.experiment_name = st.text_input("Experiment Name", value=st.session_state.experiment_name)
    st.session_state.num_cells = st.number_input("Number of Cells", min_value=1, max_value=20,
                                                 value=st.session_state.num_cells)

    if st.button("Randomize Current Values"):
        st.session_state.current_experiment = {}
        for i in range(st.session_state.num_cells):
            ctype = random.choice(["NMC", "LFP"])
            defaults = get_default_values(ctype)
            st.session_state.current_experiment[f"Cell {i+1}"] = {"Cell Type": ctype, **defaults}

    if st.button("💾 Save Experiment"):
        if st.session_state.current_experiment:
            st.session_state.experiments[st.session_state.experiment_name] = st.session_state.current_experiment.copy()
            st.success(f"Saved {st.session_state.experiment_name}")
        else:
            st.warning("No data to save!")

    exp_to_load = st.selectbox("📂 Load Experiment", ["Select"] + list(st.session_state.experiments.keys()))
    if exp_to_load != "Select" and st.button("Load Selected Experiment"):
        st.session_state.current_experiment = st.session_state.experiments[exp_to_load].copy()
        st.session_state.experiment_name = exp_to_load
        st.session_state.num_cells = len(st.session_state.current_experiment)
        st.info(f"Loaded {exp_to_load}")

    if st.button("🆕 New Experiment"):
        st.session_state.current_experiment = {}
        st.session_state.experiment_name = f"Experiment_{len(st.session_state.experiments) + 1}"
        st.session_state.num_cells = 8

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["Data Input", "Visualizations", "Insights", "Compare Experiments"])

# ---- TAB 1: Data Input ----
with tab1:
    st.subheader("Enter Cell Data")
    for i in range(st.session_state.num_cells):
        cols = st.columns(5)
        cell_key = f"{st.session_state.experiment_name}_Cell_{i}"
        label = f"Cell {i+1}"

        ctype = cols[0].selectbox(f"Type_{cell_key}", ["NMC", "LFP"],
                                  value=st.session_state.current_experiment.get(label, {}).get("Cell Type", "NMC"),
                                  key=f"type_{cell_key}")
        defaults = get_default_values(ctype)
        temp = cols[1].number_input(f"T_{cell_key}", 0.0, 100.0,
                                    value=st.session_state.current_experiment.get(label, {}).get("temp", defaults["temp"]),
                                    step=0.1, key=f"temp_{cell_key}")
        curr = cols[2].number_input(f"I_{cell_key}", 0.0, 20.0,
                                    value=st.session_state.current_experiment.get(label, {}).get("current", defaults["current"]),
                                    step=0.01, key=f"curr_{cell_key}")
        volt = cols[3].number_input(f"V_{cell_key}", 0.0, 5.0,
                                    value=st.session_state.current_experiment.get(label, {}).get("voltage", defaults["voltage"]),
                                    step=0.01, key=f"volt_{cell_key}")
        cap = cols[4].number_input(f"C_{cell_key}", 0.0, 10000.0,
                                   value=st.session_state.current_experiment.get(label, {}).get("capacitance", defaults["capacitance"]),
                                   step=1.0, key=f"cap_{cell_key}")

        st.session_state.current_experiment[label] = {
            "Cell Type": ctype, "temp": temp, "current": curr, "voltage": volt, "capacitance": cap,
            "max_voltage": defaults["max_voltage"], "min_voltage": defaults["min_voltage"]
        }

# ---- TAB 2: Visualizations ----
with tab2:
    if st.session_state.current_experiment:
        df = pd.DataFrame([{"Cell": k, "Temperature": v["temp"], "Voltage": v["voltage"],
                            "Current": v["current"], "Capacitance": v["capacitance"]}
                           for k, v in st.session_state.current_experiment.items()])
        st.plotly_chart(create_overview_charts(df, title=f"{st.session_state.experiment_name} Overview"),
                        use_container_width=True)
    else:
        st.info("Enter data to visualize.")

# ---- TAB 3: Insights ----
with tab3:
    if st.session_state.current_experiment:
        df = pd.DataFrame([{"Cell": k, **v} for k, v in st.session_state.current_experiment.items()])
        st.subheader("Summary Table")
        st.dataframe(df)

        csv = df.to_csv(index=False)
        st.download_button("📤 Export Current Experiment to CSV", csv,
                           file_name=f"{st.session_state.experiment_name}.csv")
    else:
        st.info("Enter data to analyze.")

# ---- TAB 4: Compare Experiments ----
with tab4:
    if st.session_state.experiments:
        selected_exps = st.multiselect("Select Experiments to Compare", list(st.session_state.experiments.keys()))
        if selected_exps:
            comp_data = []
            for exp in selected_exps:
                df_exp = pd.DataFrame([{"Cell": k, **v} for k, v in st.session_state.experiments[exp].items()])
                df_exp["Experiment"] = exp
                comp_data.append(df_exp)
            comp_df = pd.concat(comp_data)
            st.dataframe(comp_df)

            fig = go.Figure()
            for exp in selected_exps:
                avg_temp = np.mean([v["temp"] for v in st.session_state.experiments[exp].values()])
                fig.add_trace(go.Bar(name=exp, x=["Avg Temp"], y=[avg_temp]))
            fig.update_layout(barmode="group", title="Experiment Temperature Comparison")
            st.plotly_chart(fig)

            csv_all = comp_df.to_csv(index=False)
            st.download_button("📤 Export All Experiments to CSV", csv_all, file_name="All_Experiments.csv")
    else:
        st.info("Save at least 2 experiments to compare.")
