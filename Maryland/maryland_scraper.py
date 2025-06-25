from bs4 import BeautifulSoup
import pandas as pd

# Load your saved HTML file
with open('~/Documents/GitHub/Data-Breach_Tracker/Maryland/maryland_breaches.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find the section for 2024
header_2024 = soup.find(lambda tag: tag.name == "a" and "2024" in tag.text)
if not header_2024:
    raise Exception("Could not find 2024 header!")

# Get the parent container after the header
container = header_2024.find_next("table")
if not container:
    raise Exception("Could not find a table following the 2024 header!")

# Extract table rows
rows = container.find_all("tr")
data = []

for row in rows[1:]:  # skip header
    cols = row.find_all("td")
    if len(cols) < 6:
        continue

    org = cols[0].get_text(strip=True)
    date_reported = cols[2].get_text(strip=True)
    residents_affected = cols[3].get_text(strip=True)
    notes = cols[4].get_text(strip=True)
    breach_type = cols[5].get_text(strip=True)

    data.append({
        "Organization": org,
        "Industry": "",
        "Date Reported": date_reported,
        "Date of Incident": "",
        "Date of Discovery": "",
        "State": "Maryland",
        "Residents Affected": residents_affected,
        "Breach Type": breach_type,
        "Notes": notes
    })

# Convert to DataFrame and export
df = pd.DataFrame(data)
df.to_csv("maryland_2024_breaches.csv", index=False)

print("✅ Scraping complete. Saved as maryland_2024_breaches.csv")