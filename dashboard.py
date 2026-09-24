"""
Streamlit Dashboard
Mobile OS Performance Analyzer

Run with:
    streamlit run dashboard.py

This file only builds the GUI. All the real work is done by the
existing project modules:

    main.py          -> get_real_data()  (collects + parses the phone data)
    adb_collector.py -> ADBError
    parser.py        -> parse_battery_output(), parse_memory_output()
    analyzer.py      -> create_dataframe(), get_top_cpu_process(), ...
"""

from datetime import datetime

import streamlit as st

from adb_collector import ADBError
from analyzer import (
    create_dataframe,
    get_top_cpu_process,
    get_top_memory_process,
)
from main import get_real_data
from parser import parse_battery_output, parse_memory_output


# -------------------------------------------------
# Page setup
# -------------------------------------------------

st.set_page_config(
    page_title="Mobile OS Performance Analyzer",
    page_icon="📱",
    layout="wide",
)

NO_DEVICE_MESSAGE = (
    "**No authorized Android device detected.**\n\n"
    "Connect the phone, enable USB debugging, and try again."
)


# -------------------------------------------------
# Small helper functions
# -------------------------------------------------

def mb_to_gb_text(value_mb):
    """Turn a value in MB into text like '5.84 GB'."""
    if value_mb is None:
        return "Unknown"
    return f"{value_mb / 1024:.2f} GB"


def collect_and_analyze():
    """
    Collect fresh data from the phone using the existing backend
    and return everything the dashboard needs in one dictionary.
    """

    # Same function the CLI (main.py) uses.
    processes, raw_data = get_real_data()

    if not processes:
        raise ValueError("No process information could be parsed.")

    # Device information (same parsing as main.py's display function)
    battery = parse_battery_output(raw_data["battery"])
    memory = parse_memory_output(raw_data["memory"])

    device = {
        "model": raw_data.get("device_model", "Unknown"),
        "android_version": raw_data.get("android_version", "Unknown"),
        "battery_percent": battery.get("battery_percent"),
        "battery_status": battery.get("status", "Unknown"),
        "temperature_c": battery.get("temperature_c"),
        "total_ram_mb": memory.get("MemTotal"),
        "available_ram_mb": memory.get("MemAvailable"),
    }

    # Process data as a Pandas table (same as main.py)
    df = create_dataframe(processes)

    return {
        "device": device,
        "df": df,
        "timestamp": datetime.now(),
    }


def show_top_chart(df, column, y_label):
    """Draw a horizontal bar chart of the top 10 processes for one column."""
    top_10 = df.sort_values(column, ascending=False).head(10)

    st.bar_chart(
        top_10,
        x="process",
        y=column,
        x_label=y_label,
        y_label="Process",
        horizontal=True,
        sort=f"-{column}",  # keep the biggest process at the top
    )


# -------------------------------------------------
# Header
# -------------------------------------------------

st.title("Mobile OS Performance Analyzer")
st.caption("Real-time Android system monitoring using ADB and Python")

# -------------------------------------------------
# Analyze button
# -------------------------------------------------

# st.session_state remembers the last result, so the page does not
# go blank when Streamlit reruns (for example after a CSV download).
if "result" not in st.session_state:
    st.session_state["result"] = None
if "error" not in st.session_state:
    st.session_state["error"] = None

if st.button("Analyze Connected Device", type="primary"):

    st.session_state["result"] = None
    st.session_state["error"] = None

    with st.spinner("Collecting data from the Android device..."):
        try:
            st.session_state["result"] = collect_and_analyze()

        except ADBError as error:
            # No phone, USB debugging off, ADB missing, timeout, etc.
            st.session_state["error"] = ("no_device", str(error))

        except Exception as error:
            st.session_state["error"] = ("other", str(error))

# -------------------------------------------------
# Error / empty states
# -------------------------------------------------

if st.session_state["error"] is not None:

    error_type, error_text = st.session_state["error"]

    if error_type == "no_device":
        st.warning(NO_DEVICE_MESSAGE, icon="🔌")
    else:
        st.error(
            "Something went wrong while analyzing the device. "
            "Please try again.",
            icon="⚠️",
        )

    # Technical detail is available, but tucked away.
    with st.expander("Technical details"):
        st.code(error_text)

    st.stop()

if st.session_state["result"] is None:
    st.info("Press **Analyze Connected Device** to start.")
    st.stop()

# -------------------------------------------------
# Results
# -------------------------------------------------

result = st.session_state["result"]
device = result["device"]
df = result["df"]

top_cpu = get_top_cpu_process(df).iloc[0]
top_memory = get_top_memory_process(df).iloc[0]

st.caption(
    f"Latest analysis: {result['timestamp'].strftime('%d %b %Y, %H:%M:%S')}"
)

# ---- Device information ----

st.subheader("Device Information")

battery_percent = device["battery_percent"]
temperature = device["temperature_c"]

device_items = [
    ("Device model", device["model"]),
    ("Android version", device["android_version"]),
    (
        "Battery",
        f"{battery_percent}%" if battery_percent is not None else "Unknown",
    ),
    ("Battery status", device["battery_status"]),
    (
        "Battery temperature",
        f"{temperature:.1f} °C" if temperature is not None else "Unknown",
    ),
    ("Total RAM", mb_to_gb_text(device["total_ram_mb"])),
    ("Available RAM", mb_to_gb_text(device["available_ram_mb"])),
]

with st.container(border=True):
    columns = st.columns(len(device_items))

    for column, (label, value) in zip(columns, device_items):
        column.caption(label)
        column.markdown(f"**{value}**")

# ---- Metric cards ----

st.subheader("Overview")

card_1, card_2, card_3, card_4, card_5 = st.columns(5)

card_1.metric(
    "Battery",
    f"{battery_percent}%" if battery_percent is not None else "Unknown",
    border=True,
)
card_2.metric("Processes Analyzed", len(df), border=True)
card_3.metric("Highest CPU Usage", f"{top_cpu['cpu_percent']}%", border=True)
card_4.metric("Highest RAM Usage", f"{top_memory['memory_mb']} MB", border=True)
card_5.metric(
    "Available RAM",
    mb_to_gb_text(device["available_ram_mb"]),
    border=True,
)

# ---- Top CPU / Top RAM process ----

left, right = st.columns(2)

with left:
    st.markdown("##### Top CPU Process")
    st.success(f"{top_cpu['process']} — {top_cpu['cpu_percent']}%")

with right:
    st.markdown("##### Top RAM Process")
    st.info(f"{top_memory['process']} — {top_memory['memory_mb']:.0f} MB")

# ---- Charts ----

st.subheader("Top 10 Processes")

cpu_tab, ram_tab, thread_tab = st.tabs(["CPU usage", "RAM usage", "Thread count"])

with cpu_tab:
    show_top_chart(df, "cpu_percent", "CPU usage (%)")

with ram_tab:
    show_top_chart(df, "memory_mb", "RAM usage (MB)")

with thread_tab:
    show_top_chart(df, "threads", "Thread count")

# ---- Process table ----

st.subheader("Process Data")

# Only the display column names change here. The original
# DataFrame (and the CSV) keep the project's field names.
table = get_top_cpu_process(df).rename(
    columns={
        "pid": "PID",
        "process": "Process",
        "cpu_percent": "CPU %",
        "memory_mb": "RAM MB",
        "threads": "Threads",
    }
)

st.dataframe(
    table[["PID", "Process", "CPU %", "RAM MB", "Threads"]],
    hide_index=True,
)

# ---- CSV download ----

file_name = f"performance_{result['timestamp'].strftime('%Y%m%d_%H%M%S')}.csv"

st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=file_name,
    mime="text/csv",
)
