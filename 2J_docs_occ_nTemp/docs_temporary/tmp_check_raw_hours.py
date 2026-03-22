import pandas as pd

def check_raw_hours():
    try:
        df05 = pd.read_csv("outputs_step1/main_2005.csv", usecols=['WKWEHR_C'])
        print("=== 2005 WKWEHR_C ===")
        print(df05['WKWEHR_C'].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95]))
        print("Top 10 values:\n", df05['WKWEHR_C'].value_counts().head(10))
    except Exception as e: print(e)

    try:
        df10 = pd.read_csv("outputs_step1/main_2010.csv", usecols=['WKWEHR_C'])
        print("\n=== 2010 WKWEHR_C ===")
        print(df10['WKWEHR_C'].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95]))
        print("Top 10 values:\n", df10['WKWEHR_C'].value_counts().head(10))
    except Exception as e: print(e)

    try:
        df15 = pd.read_csv("outputs_step1/main_2015.csv", usecols=['WHWD140C'])
        print("\n=== 2015 WHWD140C ===")
        print(df15['WHWD140C'].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95]))
        print("Top 10 values:\n", df15['WHWD140C'].value_counts().head(10))
    except Exception as e: print(e)

    try:
        df22 = pd.read_csv("outputs_step1/main_2022.csv", usecols=['WHWD140G'])
        print("\n=== 2022 WHWD140G ===")
        print(df22['WHWD140G'].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95]))
        print("Top 10 values:\n", df22['WHWD140G'].value_counts().head(10))
    except Exception as e: print(e)

if __name__ == '__main__':
    check_raw_hours()
