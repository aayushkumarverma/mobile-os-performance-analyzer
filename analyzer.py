import pandas as pd


def create_dataframe(data):
    return pd.DataFrame(data)


def get_top_cpu_process(df):
    return df.sort_values("cpu_percent", ascending=False)


def get_top_memory_process(df):
    return df.sort_values("memory_mb", ascending=False)


def get_average_cpu(df):
    return df["cpu_percent"].mean()


def get_average_memory(df):
    return df["memory_mb"].mean()


def export_csv(df, filename="output/performance.csv"):
    df.to_csv(filename, index=False)
    return filename