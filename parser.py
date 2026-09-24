"""
Parsing Module
Mobile OS Performance Analyzer

Converts raw ADB output into structured Python data.
"""

import re
from typing import Optional


# -------------------------------------------------
# Basic helper functions
# -------------------------------------------------

def parse_number(value: str) -> Optional[float]:
    """Safely convert text into a float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def memory_to_mb(value: str) -> Optional[float]:
    """
    Convert memory values into MB.

    Supports values such as:
    41000
    41000K
    410M
    1.5G
    """

    if value is None:
        return None

    value = value.strip().upper()

    match = re.match(r"^([\d.]+)([KMG]?)B?$", value)

    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2)

    if unit == "K":
        return round(number / 1024, 2)

    if unit == "G":
        return round(number * 1024, 2)

    if unit == "M":
        return round(number, 2)

    # Android ps commonly reports RSS as KB
    return round(number / 1024, 2)


# -------------------------------------------------
# Process parsing
# -------------------------------------------------

def parse_processes(raw_output: str) -> list[dict]:
    """
    Parse Android 'ps' output.

    Returns the common project format:

    pid
    process
    cpu_percent
    memory_mb
    threads
    """

    processes = []

    lines = raw_output.strip().splitlines()

    if not lines:
        return processes

    header_index = None
    headers = []

    # Find the ps table header
    for index, line in enumerate(lines):

        columns = line.split()

        possible_names = {
            "NAME",
            "CMD",
            "COMMAND",
            "ARGS",
        }

        if "PID" in columns and any(
            name in columns for name in possible_names
        ):
            header_index = index
            headers = columns
            break

    if header_index is None:
        return processes

    pid_index = headers.index("PID")

    # Find process-name column
    name_index = None

    for name in ["NAME", "CMD", "COMMAND", "ARGS"]:
        if name in headers:
            name_index = headers.index(name)
            break

    if name_index is None:
        return processes

    rss_index = (
        headers.index("RSS")
        if "RSS" in headers
        else None
    )

    # Read process rows
    for line in lines[header_index + 1:]:

        columns = line.split()

        if len(columns) <= max(pid_index, name_index):
            continue

        try:
            pid = int(columns[pid_index])
        except ValueError:
            continue

        process_name = columns[name_index]

        memory_mb = 0.0

        if rss_index is not None and len(columns) > rss_index:

            converted_memory = memory_to_mb(
                columns[rss_index]
            )

            if converted_memory is not None:
                memory_mb = converted_memory

        processes.append(
            {
                "pid": pid,
                "process": process_name,
                "cpu_percent": 0.0,
                "memory_mb": memory_mb,
                "threads": 0,
            }
        )

    return processes


# -------------------------------------------------
# CPU parsing
# -------------------------------------------------

def parse_cpu_output(raw_output: str) -> dict[int, float]:
    """
    Parse process CPU usage from Android 'top'.

    Returns:
        {
            PID: CPU_PERCENT
        }
    """

    cpu_data = {}

    lines = raw_output.strip().splitlines()

    header = None
    header_index = None
    cpu_header = None

    # Different Android versions may use:
    # %CPU
    # CPU%
    cpu_names = ["%CPU", "CPU%"]

    for index, line in enumerate(lines):

        columns = line.split()

        if "PID" not in columns:
            continue

        for possible_cpu in cpu_names:

            if possible_cpu in columns:
                header = columns
                header_index = index
                cpu_header = possible_cpu
                break

        if header is not None:
            break

    if header is None:
        return cpu_data

    pid_index = header.index("PID")
    cpu_index = header.index(cpu_header)

    for line in lines[header_index + 1:]:

        columns = line.split()

        if len(columns) <= max(pid_index, cpu_index):
            continue

        try:
            pid = int(columns[pid_index])

            cpu_text = columns[cpu_index].replace("%", "")

            cpu = float(cpu_text)

        except (ValueError, TypeError):
            continue

        cpu_data[pid] = cpu

    return cpu_data


# -------------------------------------------------
# Process status parsing
# -------------------------------------------------

def parse_thread_count(raw_output: str) -> Optional[int]:
    """
    Parse thread count from /proc/PID/status.
    """

    match = re.search(
        r"^\s*Threads:\s*(\d+)",
        raw_output,
        re.MULTILINE
    )

    if match:
        return int(match.group(1))

    return None


def parse_process_memory(raw_output: str) -> Optional[float]:
    """
    Parse VmRSS from /proc/PID/status.

    VmRSS represents the resident memory being
    used by that process.
    """

    match = re.search(
        r"^\s*VmRSS:\s*(\d+)\s+kB",
        raw_output,
        re.MULTILINE
    )

    if not match:
        return None

    memory_kb = int(match.group(1))

    return round(memory_kb / 1024, 2)


def parse_process_status(raw_output: str) -> dict:
    """
    Parse useful information from /proc/PID/status.

    Returns:
        {
            "threads": ...,
            "memory_mb": ...
        }
    """

    return {
        "threads": parse_thread_count(raw_output),
        "memory_mb": parse_process_memory(raw_output),
    }


# -------------------------------------------------
# Overall memory parsing
# -------------------------------------------------

def parse_memory_output(raw_output: str) -> dict:
    """
    Parse /proc/meminfo.

    Values are converted from KB to MB.
    """

    memory = {}

    for line in raw_output.splitlines():

        match = re.match(
            r"^(\w+):\s+(\d+)\s+kB",
            line
        )

        if not match:
            continue

        key = match.group(1)

        value_kb = int(match.group(2))

        memory[key] = round(
            value_kb / 1024,
            2
        )

    return memory


# -------------------------------------------------
# Battery parsing
# -------------------------------------------------

def parse_battery_output(raw_output: str) -> dict:
    """
    Parse 'dumpsys battery' output.
    """

    battery = {}

    status_names = {
        "1": "Unknown",
        "2": "Charging",
        "3": "Discharging",
        "4": "Not Charging",
        "5": "Full",
    }

    for line in raw_output.splitlines():

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        if key == "level":

            try:
                battery["battery_percent"] = int(value)
            except ValueError:
                pass

        elif key == "temperature":

            try:
                battery["temperature_c"] = (
                    int(value) / 10
                )
            except ValueError:
                pass

        elif key == "AC powered":

            battery["ac_powered"] = (
                value.lower() == "true"
            )

        elif key == "USB powered":

            battery["usb_powered"] = (
                value.lower() == "true"
            )

        elif key == "status":

            battery["status"] = status_names.get(
                value,
                value
            )

    return battery


# -------------------------------------------------
# Merge functions
# -------------------------------------------------

def merge_cpu_data(
    processes: list[dict],
    cpu_data: dict[int, float],
) -> list[dict]:
    """
    Add CPU usage to each process record.
    """

    for process in processes:

        pid = process["pid"]

        if pid in cpu_data:
            process["cpu_percent"] = cpu_data[pid]

    return processes


def merge_process_status(
    processes: list[dict],
    status_data: dict[int, dict],
) -> list[dict]:
    """
    Add thread and memory information obtained
    from /proc/PID/status.
    """

    for process in processes:

        pid = process["pid"]

        if pid not in status_data:
            continue

        status = status_data[pid]

        threads = status.get("threads")

        memory_mb = status.get("memory_mb")

        if threads is not None:
            process["threads"] = threads

        if memory_mb is not None:
            process["memory_mb"] = memory_mb

    return processes


# -------------------------------------------------
# Final process-data builder
# -------------------------------------------------

def build_process_data(
    process_output: str,
    cpu_output: str,
    status_data: Optional[dict[int, dict]] = None,
) -> list[dict]:
    """
    Build the final shared process-data format.

    Output example:

    {
        "pid": 2201,
        "process": "com.android.chrome",
        "cpu_percent": 8.1,
        "memory_mb": 40.04,
        "threads": 56
    }
    """

    processes = parse_processes(
        process_output
    )

    cpu_data = parse_cpu_output(
        cpu_output
    )

    processes = merge_cpu_data(
        processes,
        cpu_data
    )

    if status_data is not None:

        processes = merge_process_status(
            processes,
            status_data
        )

    return processes


# -------------------------------------------------
# Test
# -------------------------------------------------

if __name__ == "__main__":

    sample_ps = """
USER       PID   PPID  VSZ    RSS   WCHAN  ADDR S NAME
system     845   1     50000  18000 ...    ...  S system_server
u0_a123    2201  845   80000  41000 ...    ...  S com.android.chrome
"""

    sample_top = """
PID USER      PR  NI VIRT RES SHR S %CPU %MEM TIME+ NAME
845 system    10  0  50000 18000 0 S 4.1 2.0 00:01 system_server
2201 u0_a123  10  0  80000 41000 0 S 8.1 5.0 00:02 com.android.chrome
"""

    sample_status = """
Name:   com.android.chrome
State:  S (sleeping)
VmRSS:  41000 kB
Threads:    56
"""

    status_data = {
        2201: parse_process_status(
            sample_status
        )
    }

    process_data = build_process_data(
        sample_ps,
        sample_top,
        status_data
    )

    print("\nParsed Process Data:\n")

    for record in process_data:
        print(record)