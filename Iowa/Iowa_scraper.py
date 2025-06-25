import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import re
import csv
import time

# Year–URL map for Iowa AG breach pages (some use different slugs)
year_urls = {
    2025: "2025-security-breach-notification",
    2024: "2024-security-breach-notification",
    2023: "2023-security-breach-notification",
    2022: "2022-security-breach-notifications",
    2021: "2021-security-brea",
    2020: "2020-security-breach-notification",
    2019: "2019",
    2018: "2018-security-breach-notifications",
    2017: "2017",
    2016: "2016-security-breach-notifications",
    2015: "2015-security-breach-notifications",
    2014: "2014-security-breach-notifications",
    2013: "2013-security-breach-notifications",
    2012: "2012-security-breach-notifications",
    2011: "2011-security-breach-notifications",
}

BASE_URL = "https://www.iowaattorneygeneral.gov/for-consumers/security-breach-notifications/"

output_data = []

def extract_pdf_data(url):
    try:
        response = requests.get(url, timeout=15)
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        # Extract fields
        incident_date = re.search(r"incident.*?on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
        discovery_date = re.search(r"discover(?:ed|y).*?on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
        residents = re.search(r"notify(?:ing)?\s+approximately\s+([\d,]+)\s+.*?(residents|individuals)", text, re.IGNORECASE)
        breach_type = re.search(r"(ransomware|hacking|phishing|theft|unauthorized access|data exfiltration|third[- ]party breach|external system breach)", text, re.IGNORECASE)

        return {
            "Date of Incident": incident_date.group(1) if incident_date else "",
            "Date of Discovery": discovery_date.group(1) if discovery_date else "",
            "Residents Affected": residents.group(1).replace(",", "") if residents else "",
            "Breach Type": breach_type.group(1).title() if breach_type else "",
            "Notes": text[:1000].replace("\n", " ")  # truncated text
        }
    except Exception as e:
        print(f"⚠️ PDF parsing failed: {url} — {e}")
        return {
            "Date of Incident": "",
            "Date of Discovery": "",
            "Residents Affected": "",
            "Breach Type": "",
            "Notes": ""
        }

for year, slug in year_urls.items():
    print(f"🔍 Scraping {year}...")
    try:
        url = BASE_URL + slug
        resp = requests.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            date_reported = cols[0].get_text(strip=True)
            org_links = cols[1].find_all("a")

            for link in org_links:
                name = link.get_text(strip=True)
                href = link.get("href")

                if "supplemental" in name.lower():
                    continue

                # Avoid trimming after comma — keep full name
                org_name = name

                pdf_url = "https://www.iowaattorneygeneral.gov" + href if href else ""

                entry = {
                    "Year": year,
                    "Date Reported": date_reported,
                    "Organization": org_name,
                    "PDF Link": pdf_url
                }

                if pdf_url.endswith(".pdf"):
                    pdf_data = extract_pdf_data(pdf_url)
                    entry.update(pdf_data)

                output_data.append(entry)
                time.sleep(1)

        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Failed to process year {year}: {e}")

# Save to CSV
if output_data:
    with open("iowa_breach_reports.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_data[0].keys())
        writer.writeheader()
        writer.writerows(output_data)
    print(f"\n✅ Done! {len(output_data)} breaches saved to iowa_breach_reports.csv")
else:
    print("❌ No data extracted.")