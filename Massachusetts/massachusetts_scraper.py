import pdfplumber
import pandas as pd
import os

# Path to Folder with MA PDFs
pdf_folder = "Massachusetts/MA_Breach_Reports"
output_csv = "massachusetts_data_breaches.csv"

target_columns = [
    "Organization",
    "Industry",
    "Date Reported",
    "Date of Incident",
    "Date of Discovery",
    "State",
    "MA Residents Affected",
    "Breach Type",
    "Notes"
]

# Store all rows here
all_data = []

# Loop through each PDF file
for filename in sorted(os.listdir(pdf_folder)):
    if filename.endswith(".pdf") and filename.startswith("MA_"):
        pdf_path = os.path.join(pdf_folder, filename)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    headers = table[0]
                    for row in table[1:]:
                        row_dict = dict(zip(headers, row))

                        # Build your row based on mapped fields
                        record = {
                            "Organization": row_dict.get("Organization Name", "").strip() or "Unknown",
                            "Industry": "",  # not available
                            "Date Reported": row_dict.get("Date Reported To OCA", "").strip() or "Unknown",
                            "Date of Incident": "",
                            "Date of Discovery": "",
                            "State": "Massachusetts",
                            "MA Residents Affected": row_dict.get("MA Residents Affected", "").strip() or "Unknown",
                            "Breach Type": row_dict.get("Breach Type Description", "").strip() or "Unknown",
                            "Notes": ""
                        }

                        all_data.append(record)

# Create DataFrame and export to CSV
df = pd.DataFrame(all_data, columns=target_columns)
df.to_csv(output_csv, index=False)

print(f"✅ Successfully exported {len(df)} rows to {output_csv}")