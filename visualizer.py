"""
This module will generate graphs and visualizations
from Android performance data.
"""
import matplotlib.pyplot as plt


def plot_cpu_usage(df):
    top_cpu = df.sort_values("cpu_percent", ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    plt.bar(top_cpu["process"], top_cpu["cpu_percent"])

    plt.xlabel("Process")
    plt.ylabel("CPU Usage (%)")
    plt.title("Top Processes by CPU Usage")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig("output/cpu_usage.png")
    plt.close()

import matplotlib.pyplot as plt


def plot_cpu_usage(df):
    top_cpu = df.sort_values("cpu_percent", ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    plt.bar(top_cpu["process"], top_cpu["cpu_percent"])

    plt.xlabel("Process")
    plt.ylabel("CPU Usage (%)")
    plt.title("Top Processes by CPU Usage")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig("output/cpu_usage.png")
    plt.close()


def plot_memory_usage(df):
    top_memory = df.sort_values("memory_mb", ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    plt.bar(top_memory["process"], top_memory["memory_mb"])

    plt.xlabel("Process")
    plt.ylabel("Memory Usage (MB)")
    plt.title("Top Processes by Memory Usage")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig("output/memory_usage.png")
    plt.close()


def plot_thread_count(df):
    top_threads = df.sort_values("threads", ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    plt.bar(top_threads["process"], top_threads["threads"])

    plt.xlabel("Process")
    plt.ylabel("Thread Count")
    plt.title("Top Processes by Thread Count")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig("output/thread_count.png")
    plt.close()