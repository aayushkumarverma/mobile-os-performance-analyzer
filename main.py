from adb_collector import (
    ADBError,
    collect_raw_data,
    get_threads_raw,
)

from parser import (
    build_process_data,
    parse_process_status,
    parse_memory_output,
    parse_battery_output,
)

from analyzer import (
    create_dataframe,
    get_top_cpu_process,
    get_top_memory_process,
    get_average_cpu,
    get_average_memory,
    export_csv,
)

from visualizer import (
    plot_cpu_usage,
    plot_memory_usage,
    plot_thread_count,
)


# -------------------------------------------------
# Sample Data
# -------------------------------------------------

def get_sample_data():
    return [
        {
            "pid": 1023,
            "process": "SystemUI",
            "cpu_percent": 3.5,
            "memory_mb": 180,
            "threads": 42,
        },
        {
            "pid": 2201,
            "process": "Chrome",
            "cpu_percent": 8.1,
            "memory_mb": 410,
            "threads": 65,
        },
    ]


# -------------------------------------------------
# Real Android Data
# -------------------------------------------------

def get_real_data():
    print("\nCollecting data from Android device...")

    raw_data = collect_raw_data()

    # First parse process + CPU information
    processes = build_process_data(
        raw_data["processes"],
        raw_data["cpu"],
    )

    if not processes:
        print("No process information could be parsed.")
        return [], raw_data

    # Sort processes so we collect detailed information
    # for the most active ones.
    processes = sorted(
        processes,
        key=lambda process: (
            process["cpu_percent"],
            process["memory_mb"],
        ),
        reverse=True,
    )

    # Getting /proc/PID/status for hundreds of processes
    # would be slow, so analyze the top 20 processes.
    selected_processes = processes[:20]

    status_data = {}

    print(
        f"Collecting RAM and thread information "
        f"for {len(selected_processes)} processes..."
    )

    for process in selected_processes:

        pid = process["pid"]

        try:
            status_raw = get_threads_raw(pid)

            status_data[pid] = parse_process_status(
                status_raw
            )

        except ADBError:
            # Some Android processes may disappear or
            # deny access while data is being collected.
            continue

    # Build data again with thread/RAM information
    final_processes = build_process_data(
        raw_data["processes"],
        raw_data["cpu"],
        status_data,
    )

    selected_pids = {
        process["pid"]
        for process in selected_processes
    }

    final_processes = [
        process
        for process in final_processes
        if process["pid"] in selected_pids
    ]

    return final_processes, raw_data


# -------------------------------------------------
# Device Information
# -------------------------------------------------

def display_device_information(raw_data):

    print("\n=== DEVICE INFORMATION ===")

    print(
        "Device:",
        raw_data.get(
            "device_model",
            "Unknown"
        )
    )

    print(
        "Android Version:",
        raw_data.get(
            "android_version",
            "Unknown"
        )
    )

    # Battery
    battery = parse_battery_output(
        raw_data["battery"]
    )

    print("\n=== BATTERY ===")

    print(
        "Battery Level:",
        battery.get(
            "battery_percent",
            "Unknown"
        ),
        "%"
    )

    print(
        "Battery Status:",
        battery.get(
            "status",
            "Unknown"
        )
    )

    print(
        "Temperature:",
        battery.get(
            "temperature_c",
            "Unknown"
        ),
        "°C"
    )

    # System memory
    memory = parse_memory_output(
        raw_data["memory"]
    )

    print("\n=== SYSTEM MEMORY ===")

    total_memory = memory.get(
        "MemTotal"
    )

    available_memory = memory.get(
        "MemAvailable"
    )

    if total_memory is not None:
        print(
            "Total RAM:",
            round(
                total_memory / 1024,
                2
            ),
            "GB"
        )

    if available_memory is not None:
        print(
            "Available RAM:",
            round(
                available_memory / 1024,
                2
            ),
            "GB"
        )

    if (
        total_memory is not None
        and available_memory is not None
    ):

        used_memory = (
            total_memory
            - available_memory
        )

        print(
            "Approx. Used RAM:",
            round(
                used_memory / 1024,
                2
            ),
            "GB"
        )


# -------------------------------------------------
# Analysis
# -------------------------------------------------

def analyze_data(data):

    if not data:
        print("\nNo process data available.")
        return

    df = create_dataframe(data)

    print("\n=== PROCESS DATA ===")
    print(df.to_string(index=False))

    print("\n=== TOP CPU PROCESSES ===")

    print(
        get_top_cpu_process(
            df
        ).head(5).to_string(
            index=False
        )
    )

    print("\n=== TOP RAM PROCESSES ===")

    print(
        get_top_memory_process(
            df
        ).head(5).to_string(
            index=False
        )
    )

    print("\nAverage CPU Usage:")
    print(
        round(
            get_average_cpu(df),
            2
        ),
        "%"
    )

    print("\nAverage Process RAM:")
    print(
        round(
            get_average_memory(df),
            2
        ),
        "MB"
    )

    # Save CSV
    csv_file = export_csv(df)

    print(
        "\nCSV saved:",
        csv_file
    )

    # Generate graphs
    plot_cpu_usage(df)

    plot_memory_usage(df)

    plot_thread_count(df)

    print(
        "Graphs saved in output folder."
    )


# -------------------------------------------------
# Main Program
# -------------------------------------------------

def main():

    print(
        "=== Mobile OS Performance Analyzer ==="
    )

    while True:

        print("\n1. Analyze connected Android device")
        print("2. Analyze sample data")
        print("3. Exit")

        choice = input(
            "\nEnter your choice: "
        )

        # REAL DEVICE
        if choice == "1":

            try:

                data, raw_data = (
                    get_real_data()
                )

                display_device_information(
                    raw_data
                )

                analyze_data(
                    data
                )

            except ADBError as error:

                print(
                    "\nADB Error:",
                    error
                )

            except Exception as error:

                print(
                    "\nUnexpected Error:",
                    error
                )

        # SAMPLE MODE
        elif choice == "2":

            try:

                data = get_sample_data()

                analyze_data(
                    data
                )

            except Exception as error:

                print(
                    "\nError:",
                    error
                )

        # EXIT
        elif choice == "3":

            print(
                "\nExiting Mobile OS Performance Analyzer."
            )

            break

        else:

            print(
                "\nInvalid choice. "
                "Enter 1, 2, or 3."
            )


if __name__ == "__main__":
    main()