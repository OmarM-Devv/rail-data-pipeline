import requests
from pathlib import Path

url = "https://dataportal.orr.gov.uk/media/1909/table-1410-passenger-entries-and-exits-and-interchanges-by-station.csv"

response = requests.get(url)

print(response.status_code)
raw_path = Path("data/raw/station_usage.csv")
raw_path.parent.mkdir(parents=True, exist_ok=True)

with open(raw_path, "wb") as f:
    f.write(response.content)
    
print("Saved to", raw_path)
