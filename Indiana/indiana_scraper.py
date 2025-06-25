import pdfplumber
import pandas as pd
import os

# Folder path with your Indiana PDFs
pdf_folder = os.path.expanduser("~/Documents/GitHub/Data-Breach-Tracker/Indiana")
output_csv = "indiana_data_breaches.csv"

# Output columns in the desired order
target_columns = [
    "Organization",
    "Industry",
    "Date Reported",
    "Date of Incident",
    "Date of Discovery",
    "State",
    "Residents Affected",
    "Breach Type",
    "Notes"
]

# Flexible column header matching
header_mapping = {
    "Organization": ["Respondent", "Name of Company or Organization", "Matter: Name"],
    "Date Reported": ["Notification Sent", "Notific Sent", "Date of Notification"],
    "Date of Incident": ["Breach Occurred", "Breach Occ", "Date of the Breach"],
    "Residents Affected": ["IN Affected"]
}

def match_column(columns, match_list):
    """Return the actual column name from a list of possible matches"""
    for possible in match_list:
        for col in columns:
            if possible.lower() in col.lower():
                return col
    return None

# Store all rows
all_data = []

# Loop through each Indiana PDF
for filename in sorted(os.listdir(pdf_folder)):
    if filename.endswith(".pdf") and filename.startswith("IN_"):
        pdf_path = os.path.join(pdf_folder, filename)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue

                headers = table[0]
                data_rows = table[1:]

                # Dynamically find matching headers
                col_org = match_column(headers, header_mapping["Organization"])
                col_reported = match_column(headers, header_mapping["Date Reported"])
                col_incident = match_column(headers, header_mapping["Date of Incident"])
                col_affected = match_column(headers, header_mapping["Residents Affected"])

                for row in data_rows:
                    row_dict = dict(zip(headers, row))

                    record = {
                        "Organization": row_dict.get(col_org, "").strip() if col_org else "Unknown",
                        "Industry": "",
                        "Date Reported": row_dict.get(col_reported, "").strip() if col_reported else "Unknown",
                        "Date of Incident": row_dict.get(col_incident, "").strip() if col_incident else "",
                        "Date of Discovery": "",
                        "State": "Indiana",
                        "Residents Affected": row_dict.get(col_affected, "").strip() if col_affected else "",
                        "Breach Type": "",
                        "Notes": ""
                    }

                    all_data.append(record)

# Final DataFrame and export
df = pd.DataFrame(all_data, columns=target_columns)
df.to_csv(output_csv, index=False)

print(f"✅ Successfully exported {len(df)} Indiana records to {output_csv}")