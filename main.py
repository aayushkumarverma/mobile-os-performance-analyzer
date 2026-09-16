from analyzer import (
    create_dataframe,
    get_top_cpu_process,
    get_top_memory_process,
    get_average_cpu,
    get_average_memory,
    export_csv
)

from visualizer import (
    plot_cpu_usage,
    plot_memory_usage,
    plot_thread_count
)


def get_sample_data():
    return [
        {
            "pid": 1023,
            "process": "SystemUI",
            "cpu_percent": 3.5,
            "memory_mb": 180,
            "threads": 42
        },
        {
            "pid": 2201,
            "process": "Chrome",
            "cpu_percent": 8.1,
            "memory_mb": 410,
            "threads": 65
        }
    ]


def analyze_data(data):
    if not data:
        print("\nNo process data available.")
        return

    print("\nProcess Data:")

    for process in data:
        print(
            f"PID: {process['pid']} | "
            f"Process: {process['process']} | "
            f"CPU: {process['cpu_percent']}% | "
            f"RAM: {process['memory_mb']} MB | "
            f"Threads: {process['threads']}"
        )

    df = create_dataframe(data)

    print("\nPandas DataFrame:")
    print(df)

    print("\nProcesses sorted by CPU usage:")
    print(get_top_cpu_process(df))

    print("\nProcesses sorted by RAM usage:")
    print(get_top_memory_process(df))

    print("\nAverage CPU Usage:")
    print(get_average_cpu(df), "%")

    print("\nAverage RAM Usage:")
    print(get_average_memory(df), "MB")

    csv_file = export_csv(df)

    print("\nCSV file saved successfully:")
    print(csv_file)

    plot_cpu_usage(df)
    plot_memory_usage(df)
    plot_thread_count(df)

    print("\nGraphs saved successfully.")


def main():
    print("=== Mobile OS Performance Analyzer ===")

    while True:
        print("\n1. Analyze sample data")
        print("2. View sample data")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            try:
                data = get_sample_data()
                analyze_data(data)

            except Exception as e:
                print("\nAn error occurred:")
                print(e)

        elif choice == "2":
            data = get_sample_data()

            print("\nSample Data:")

            for process in data:
                print(process)

        elif choice == "3":
            print("\nExiting Mobile OS Performance Analyzer.")
            break

        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()