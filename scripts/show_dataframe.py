from pathlib import Path
from src.data_loader import load_yks_table, preview_dataframe

if __name__ == "__main__":
    df = load_yks_table()
    print(f"Toplam satır: {len(df):,}")
    preview_dataframe(df)
