import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://cca.hawaii.gov/ocp/notices/security-breach/"
state = "Hawaii"
rows = []

resp = requests.get(url)
soup = BeautifulSoup(resp.text, "html.parser")

# Locate the table
table = soup.find("table")
headers = [th.get_text(strip=True) for th in table.find_all("th")]

for tr in table.find("tbody").find_all("tr"):
    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
    if len(cols) < 5:
        continue

    date_notified, _, org, breach_type, residents = cols[:5]

    rows.append({
        "Organization": org,
        "Industry": "",
        "Date Reported": date_notified,
        "Date of Incident": "",
        "Date of Discovery": "",
        "State": state,
        "Residents Affected": residents.replace(",", ""),
        "Breach Type": breach_type,
        "Notes": ""
    })

df = pd.DataFrame(rows, columns=[
    "Organization", "Industry", "Date Reported", "Date of Incident",
    "Date of Discovery", "State", "Residents Affected", "Breach Type", "Notes"
])
df.to_csv("hawaii_data_breaches.csv", index=False)
print(f"✅ Scraped {len(df)} records for {state}")