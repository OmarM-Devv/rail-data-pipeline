import requests
import pandas as pd
from pathlib import Path
def fetch_raw_csv(url, raw_path):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    print(response.status_code)

    raw_path.parent.mkdir(parents=True, exist_ok=True)

    with open(raw_path, "wb") as f:
        f.write(response.content)

    print("Saved to", raw_path)
    return raw_path
def load_and_clean_data(raw_path):
    df = pd.read_csv(
        raw_path,
        skiprows=3,
        thousands=",",
        na_values="[z]",
        dtype={"National Location Code (NLC)": "string"},
    )

    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("\n", " ", regex=False)
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(r"[^a-z0-9]+", "_", regex=True)
    df.columns = df.columns.str.strip("_")

    integer_columns = [
        "entries_and_exits_full_price_tickets",
        "entries_and_exits_reduced_price_tickets",
        "entries_and_exits_season_tickets",
        "entries_and_exits_all_tickets",
        "entries_and_exits_rank",
        "interchanges",
        "number_of_journeys_to_or_from_main_origin_or_destination_station",
    ]

    df[integer_columns] = df[integer_columns].astype("Int64")
    print("Rows after removing empty rows:", len(df))
    return df


def save_processed_csv(df, processed_path):
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    print("Saved processed data to", processed_path)


def main():
    url = "https://dataportal.orr.gov.uk/media/1909/table-1410-passenger-entries-and-exits-and-interchanges-by-station.csv"
    raw_path = Path("data/raw/station_usage.csv")
    raw_path = fetch_raw_csv(url, raw_path)

    df = load_and_clean_data(raw_path)

    processed_path = Path("data/processed/station_usage.csv")
    save_processed_csv(df, processed_path)


if __name__ == "__main__":
    main()