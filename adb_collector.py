"""
ADB Data Collection Module
Mobile OS Performance Analyzer

Collects raw Android process, CPU, memory, thread,
battery, and device information using ADB.
"""

import shutil
import subprocess


class ADBError(Exception):
    """Raised when an ADB command fails."""
    pass


def run_adb_command(args: list[str], timeout: int = 10) -> str:
    """
    Run an ADB command and return its output as text.

    Example:
        run_adb_command(["shell", "ps"])
    """

    if shutil.which("adb") is None:
        raise ADBError(
            "ADB was not found. Install Android SDK Platform Tools "
            "and make sure adb is added to PATH."
        )

    try:
        result = subprocess.run(
            ["adb"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

    except subprocess.TimeoutExpired:
        raise ADBError(
            f"ADB command timed out after {timeout} seconds."
        )

    except OSError as error:
        raise ADBError(
            f"Could not run ADB: {error}"
        )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        if not error_message:
            error_message = "ADB command failed."

        raise ADBError(error_message)

    return result.stdout.strip()


def get_device_list() -> list[dict]:
    """
    Return all connected Android devices and their statuses.

    Example:
        [
            {
                "device_id": "ABC123",
                "status": "device"
            }
        ]
    """

    output = run_adb_command(["devices"])

    devices = []

    lines = output.splitlines()

    for line in lines[1:]:
        parts = line.split()

        if len(parts) >= 2:
            devices.append(
                {
                    "device_id": parts[0],
                    "status": parts[1],
                }
            )

    return devices


def check_device() -> bool:
    """
    Return True if at least one authorized Android
    device is connected.
    """

    devices = get_device_list()

    return any(
        device["status"] == "device"
        for device in devices
    )


def get_device_model() -> str:
    """Return the model name of the connected Android device."""

    return run_adb_command(
        ["shell", "getprop", "ro.product.model"]
    )


def get_android_version() -> str:
    """Return the Android version of the connected device."""

    return run_adb_command(
        ["shell", "getprop", "ro.build.version.release"]
    )


def get_processes_raw() -> str:
    """
    Collect raw information about currently
    running Android processes.
    """

    return run_adb_command(
        ["shell", "ps"],
        timeout=15
    )


def get_cpu_raw() -> str:
    """
    Collect one snapshot of CPU and process activity.
    """

    return run_adb_command(
        ["shell", "top", "-n", "1"],
        timeout=15
    )


def get_memory_raw() -> str:
    """
    Collect overall Android system memory information.
    """

    return run_adb_command(
        ["shell", "cat", "/proc/meminfo"],
        timeout=10
    )


def get_battery_raw() -> str:
    """
    Collect battery level, status, temperature,
    and other available battery information.
    """

    return run_adb_command(
        ["shell", "dumpsys", "battery"],
        timeout=10
    )


def get_threads_raw(pid: int) -> str:
    """
    Collect process status information for a PID.

    The returned data contains the process thread count.
    """

    return run_adb_command(
        [
            "shell",
            "cat",
            f"/proc/{int(pid)}/status"
        ],
        timeout=10
    )


def collect_raw_data() -> dict:
    """
    Collect the main raw Android performance data.

    Thread information is collected separately because
    a PID must first be known.
    """

    if not check_device():
        raise ADBError(
            "No authorized Android device found. "
            "Enable USB debugging, connect the phone, "
            "and accept the authorization prompt."
        )

    return {
        "device_model": get_device_model(),
        "android_version": get_android_version(),
        "processes": get_processes_raw(),
        "cpu": get_cpu_raw(),
        "memory": get_memory_raw(),
        "battery": get_battery_raw(),
    }


if __name__ == "__main__":

    print("=== ADB Data Collection Test ===")

    try:
        devices = get_device_list()

        if not devices:
            print("\nNo Android devices found.")

        else:
            print("\nConnected devices:")

            for device in devices:
                print(
                    f"Device ID: {device['device_id']} | "
                    f"Status: {device['status']}"
                )

        if check_device():

            print("\nADB connection successful.")

            print("\nDevice Model:")
            print(get_device_model())

            print("\nAndroid Version:")
            print(get_android_version())

            print("\nRunning Processes:")
            print(get_processes_raw()[:1500])

            print("\nCPU Information:")
            print(get_cpu_raw()[:1500])

            print("\nMemory Information:")
            print(get_memory_raw()[:1500])

            print("\nBattery Information:")
            print(get_battery_raw())

        else:
            print(
                "\nNo authorized device found. "
                "Check USB debugging and authorization."
            )

    except ADBError as error:
        print(f"\nADB Error: {error}")