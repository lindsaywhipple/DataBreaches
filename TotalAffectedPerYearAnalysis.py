import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


#=========================
# TOTAL AFFECTED PER YEAR
#=========================

# Load Data
df = pd.read_csv("breach_report.csv")  

# Format Date
df["Breach Submission Date"] = pd.to_datetime(df["Breach Submission Date"])
df["Year"] = df["Breach Submission Date"].dt.year

# Convert Individuals Affected to Numeric
df["Individuals Affected"] = pd.to_numeric(df["Individuals Affected"], errors="coerce")

# Summary by Year
affected_summary = df.groupby("Year")["Individuals Affected"].agg(["sum", "mean", "median", "count"]).reset_index()
affected_summary["YoY % Change"] = affected_summary["sum"].pct_change() * 100

print("📊 Yearly Impact Summary:\n")
print(affected_summary)

# Boxplot 
plt.figure(figsize=(10, 5))
sns.boxplot(x="Year", y="Individuals Affected", data=df)
plt.yscale("log")  # optional, but useful if some values are huge
plt.title("Distribution of Individuals Affected per Breach by Year")
plt.ylabel("Individuals Affected (log scale)")
plt.grid(True, axis="y")
plt.tight_layout()
plt.show()

# Identify Top 1% Most Harmful Breaches
threshold = df["Individuals Affected"].quantile(0.99)
outliers = df[df["Individuals Affected"] > threshold]
print("\n🔥 Top 1% Most Harmful Breaches:\n")
print(outliers[["Name of Covered Entity", "Year", "Individuals Affected"]])



#==========
# ANALYSIS
#==========

# Within these three years, the total number of individuals affected by healthcare-related data breaches varied significantly. 
# 2024 saw a large spike in the total number of indivduals affected, most likely driven by some extremely large data breaches including, Change Healthcare, Inc. (190 million) anf Kaiser Foundation Health Plan, Inc. (13.4 million).
# There appears to be high skewness in the data caused by massive outliers which is shown by the median in contrast to the mean. 

# The top one percent of data breaches alone account for a majority of all indviduals affected in this time span. 
# These breaches include Change Healthcare, Inc. (2024, 190 million), Kaiser Foundation (2024, 13.4 million), HCA Healthcare (2023, 11.2 million), Ascension Health (2024, 5.4 million), and Yale New Haven (2025, 5.5 million).

