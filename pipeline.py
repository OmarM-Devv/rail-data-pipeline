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


def validate_data(df):
    required_columns = [
        "station_name",
        "entries_and_exits_full_price_tickets",
        "entries_and_exits_reduced_price_tickets",
        "entries_and_exits_season_tickets",
        "entries_and_exits_all_tickets",
        "entries_and_exits_rank",
        "interchanges",
        "main_origin_or_destination_station",
        "number_of_journeys_to_or_from_main_origin_or_destination_station",
        "data_source_or_adjustments",
        "estimates_supplemented_by_local_ticketing_data_or_by_retailing_organisation",
        "quality_limitations",
        "additional_information",
        "national_location_code_nlc",
        "three_letter_code_tlc",
        "region",
        "station_facility_owner",
        "station_group",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    row_count = len(df)
    if not 2000 <= row_count <= 3500:
        raise ValueError(
            f"Expected between 2000 and 3500 station rows, found {row_count}"
        )

    identity_columns = [
        "station_name",
        "national_location_code_nlc",
    ]

    for column in identity_columns:
        if df[column].isna().any():
            raise ValueError(f"Missing values found in {column}")

        if df[column].str.strip().eq("").any():
            raise ValueError(f"Blank values found in {column}")

    numeric_columns = [
        "entries_and_exits_full_price_tickets",
        "entries_and_exits_reduced_price_tickets",
        "entries_and_exits_season_tickets",
        "entries_and_exits_all_tickets",
        "entries_and_exits_rank",
        "interchanges",
        "number_of_journeys_to_or_from_main_origin_or_destination_station",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Non-numeric data found in {column}")

        if (df[column] < 0).any():
            raise ValueError(f"Negative values found in {column}")

    print("All data validation checks passed")


def reshape_ticket_data(df):
    ticket_columns = {
        "entries_and_exits_full_price_tickets": "full_price",
        "entries_and_exits_reduced_price_tickets": "reduced_price",
        "entries_and_exits_season_tickets": "season",
    }

    ticket_df = df.melt(
        id_vars=[
            "station_name",
            "national_location_code_nlc",
            "region",
        ],
        value_vars=list(ticket_columns),
        var_name="ticket_type",
        value_name="entries_and_exits",
    )

    ticket_df["ticket_type"] = ticket_df["ticket_type"].map(ticket_columns)
    ticket_df["entries_and_exits"] = ticket_df["entries_and_exits"].astype("Int64")

    print("Rows after reshaping ticket data:", len(ticket_df))
    return ticket_df


def validate_ticket_data(ticket_df, station_count):
    expected_columns = [
        "station_name",
        "national_location_code_nlc",
        "region",
        "ticket_type",
        "entries_and_exits",
    ]

    if list(ticket_df.columns) != expected_columns:
        raise ValueError("Unexpected columns in reshaped ticket data")

    expected_rows = station_count * 3
    if ticket_df.empty or len(ticket_df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} ticket rows, found {len(ticket_df)}"
        )

    for column in ["station_name", "national_location_code_nlc", "ticket_type"]:
        if ticket_df[column].isna().any():
            raise ValueError(f"Missing values found in {column}")

        if ticket_df[column].str.strip().eq("").any():
            raise ValueError(f"Blank values found in {column}")

    expected_types = {"full_price", "reduced_price", "season"}
    if set(ticket_df["ticket_type"]) != expected_types:
        raise ValueError("Unexpected ticket types in reshaped data")

    if ticket_df.duplicated(
        subset=["national_location_code_nlc", "ticket_type"]
    ).any():
        raise ValueError("Duplicate station and ticket-type combinations")

    if not pd.api.types.is_numeric_dtype(ticket_df["entries_and_exits"]):
        raise ValueError("Reshaped entries and exits must be numeric")

    if (ticket_df["entries_and_exits"] < 0).any():
        raise ValueError("Negative entries and exits in reshaped data")

    print("Reshaped ticket data validation passed")


def save_processed_csv(df, processed_path):
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    print("Saved processed data to", processed_path)


def validate_processed_file(processed_path):
    if not processed_path.is_file():
        raise ValueError(f"Processed file not found: {processed_path}")

    if processed_path.stat().st_size == 0:
        raise ValueError(f"Processed file is empty: {processed_path}")

    print("Processed file validation passed")


def main():
    url = "https://dataportal.orr.gov.uk/media/1909/table-1410-passenger-entries-and-exits-and-interchanges-by-station.csv"
    raw_path = Path("data/raw/station_usage.csv")
    raw_path = fetch_raw_csv(url, raw_path)

    df = load_and_clean_data(raw_path)
    validate_data(df)

    ticket_df = reshape_ticket_data(df)
    validate_ticket_data(ticket_df, len(df))

    processed_path = Path("data/processed/station_usage.csv")
    save_processed_csv(df, processed_path)
    validate_processed_file(processed_path)

    ticket_path = Path("data/processed/station_usage_by_ticket_type.csv")
    save_processed_csv(ticket_df, ticket_path)
    validate_processed_file(ticket_path)


if __name__ == "__main__":
    main()