import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://attorneygeneral.delaware.gov/fraud/cpu/securitybreachnotification/database/"
state_name = "Delaware"

# Prepare to collect data
data_rows = []

# We'll fetch first page, then loop through pagination via AJAX
r = requests.get(base_url)
soup = BeautifulSoup(r.text, "html.parser")

# DataTables uses AJAX; find the API endpoint:
# Inspect the table; DataTables loads via /securitybreachnotification/ajax/...
ajax_url = base_url + "database/"  # If the page contains complete table without AJAX, we can loop pages

# But simpler: the HTML has all rows hidden in <table id="example">, no AJAX needed
table = soup.find("table")
headers = [th.get_text(strip=True) for th in table.find_all("th")]

for tr in table.tbody.find_all("tr"):
    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
    if len(cols) < 4:
        continue
    org, date_incident, reported_date, affected = cols[:4]
    # Format date fields (keep as-is or parse)
    data_rows.append({
        "Organization": org,
        "Industry": "",
        "Date Reported": reported_date,
        "Date of Incident": date_incident,
        "Date of Discovery": "",
        "State": state_name,
        "Residents Affected": affected,
        "Breach Type": "",
        "Notes": ""
    })

# Export DataFrame
df = pd.DataFrame(data_rows, columns=[
    "Organization","Industry","Date Reported","Date of Incident","Date of Discovery",
    "State","Residents Affected","Breach Type","Notes"
])
df.to_csv("delaware_data_breaches.csv", index=False)
print(f"✅ Extracted {len(df)} records for Delaware.")