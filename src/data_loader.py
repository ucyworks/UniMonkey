from __future__ import annotations
import pandas as pd
from pathlib import Path
from rich import print
from rich.table import Table
from . import config
from .preprocess import preprocess

def load_yks_table(csv_path: Path | None = None, low_memory: bool = False) -> pd.DataFrame:
    """Load the YKS placement CSV into a pandas DataFrame.

    Parameters
    ----------
    csv_path: optional override path to the CSV file. If None, uses config.RAW_DATA_FILE.
    low_memory: pass to pandas.read_csv to control dtype inference.

    Returns
    -------
    DataFrame with the raw YKS placement data.
    """
    path = Path(csv_path) if csv_path else config.RAW_DATA_FILE
    if not path.exists():
        # Try legacy location
        if config.LEGACY_RAW_DATA_FILE.exists():
            path = config.LEGACY_RAW_DATA_FILE
        else:
            raise FileNotFoundError(f"CSV bulunamadı: {path}")

    # Try UTF-8 first, then fallback to latin-1 if needed
    encodings_to_try = ["utf-8-sig", "utf-8", "latin-1", "cp1254"]
    last_err = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=low_memory)
            break
        except UnicodeDecodeError as e:
            last_err = e
    else:
        raise last_err  # type: ignore

    return df

def preview_dataframe(df: pd.DataFrame, max_rows: int = 10) -> None:
    """Pretty-print a small preview of the DataFrame using rich."""
    rows = df.head(max_rows)
    table = Table(show_header=True, header_style="bold magenta")
    for col in rows.columns:
        table.add_column(str(col))
    for _, row in rows.iterrows():
        table.add_row(*[str(v) for v in row.tolist()])
    print(table)

def load_processed(csv_path: Path | None = None) -> pd.DataFrame:
    """Load and run preprocessing (program no, geography)."""
    raw = load_yks_table(csv_path=csv_path)
    return preprocess(raw)

if __name__ == "__main__":
    df_raw = load_yks_table()
    df_proc = load_processed()
    print(f"Ham satır sayısı: {len(df_raw):,}")
    print(f"İşlenmiş satır sayısı: {len(df_proc):,}")
    preview_dataframe(df_proc)
