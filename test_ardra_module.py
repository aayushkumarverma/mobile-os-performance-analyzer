"""
Test file for the ADB collector and parser modules.

Run:
    python test_ardra_module.py
"""

from adb_collector import (
    ADBError,
    get_device_list,
    check_device,
    get_device_model,
    get_android_version,
)

from parser import (
    build_process_data,
    parse_memory_output,
    parse_battery_output,
    parse_process_status,
)


# -------------------------------------------------
# Parser Test
# -------------------------------------------------

def test_parser():

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

    records = build_process_data(
        sample_ps,
        sample_top
    )

    assert len(records) == 2

    assert records[0]["pid"] == 845

    assert records[1]["pid"] == 2201

    assert records[1]["process"] == "com.android.chrome"

    assert records[1]["cpu_percent"] == 8.1

    print("Process parser test passed.")


# -------------------------------------------------
# Process Status Test
# -------------------------------------------------

def test_process_status():

    sample_status = """
Name:   com.android.chrome
State:  S (sleeping)
VmRSS:  41000 kB
Threads:    56
"""

    status = parse_process_status(
        sample_status
    )

    assert status["threads"] == 56

    assert status["memory_mb"] == round(
        41000 / 1024,
        2
    )

    print("Thread and process-memory parser test passed.")


# -------------------------------------------------
# System Memory Test
# -------------------------------------------------

def test_memory():

    sample_memory = """
MemTotal:       8192000 kB
MemAvailable:   4096000 kB
"""

    memory = parse_memory_output(
        sample_memory
    )

    assert memory["MemTotal"] == 8000.0

    assert memory["MemAvailable"] == 4000.0

    print("System memory parser test passed.")


# -------------------------------------------------
# Battery Test
# -------------------------------------------------

def test_battery():

    sample_battery = """
level: 76
temperature: 320
USB powered: true
status: 3
"""

    battery = parse_battery_output(
        sample_battery
    )

    assert battery["battery_percent"] == 76

    assert battery["temperature_c"] == 32.0

    assert battery["usb_powered"] is True

    assert battery["status"] == "Discharging"

    print("Battery parser test passed.")


# -------------------------------------------------
# Live ADB Test
# -------------------------------------------------

def test_adb():

    print("\nChecking ADB connection...")

    try:

        devices = get_device_list()

        print("ADB devices:")
        print(devices)

        if check_device():

            print("Authorized Android device connected.")

            print(
                "Device Model:",
                get_device_model()
            )

            print(
                "Android Version:",
                get_android_version()
            )

        else:

            print(
                "No authorized Android device connected."
            )

    except ADBError as error:

        print(
            "ADB test skipped or failed:",
            error
        )


# -------------------------------------------------
# Run All Tests
# -------------------------------------------------

if __name__ == "__main__":

    print("=== Mobile OS Performance Analyzer Tests ===\n")

    test_parser()

    test_process_status()

    test_memory()

    test_battery()

    test_adb()

    print("\nTesting complete.")