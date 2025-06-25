import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

#=========================
# TOP 10 HARMFUL BREACHES
#=========================

# Data
df = pd.read_csv("breach_report.csv")  
df["Individuals Affected"] = pd.to_numeric(df["Individuals Affected"], errors="coerce")
df["Breach Submission Date"] = pd.to_datetime(df["Breach Submission Date"])
df["Year"] = df["Breach Submission Date"].dt.year

# Get Top 10 Most Harmful Breaches
top10 = df.sort_values("Individuals Affected", ascending=False).head(10)
rest = df[~df.index.isin(top10.index)]

# Entity Type Distribution in Top 10
print("📊 Entity Type Breakdown (Top 10):\n")
print(top10["Covered Entity Type"].value_counts())

# Compare Top 10 vs. Rest (Mann-Whitney U Test)
u_stat, p = mannwhitneyu(top10["Individuals Affected"], rest["Individuals Affected"])
print(f"\n🔬 Mann-Whitney U Test: U = {u_stat}, p = {p:.4f}")
if p < 0.05:
    print("✅ Top 10 breaches are significantly more severe")
else:
    print("❌ No significant difference (possibly due to skew or small sample)")

# Other Breakdown Insights (Type, Location, Year)
print("\n🔍 Type of Breach Breakdown (Top 10):\n")
print(top10["Type of Breach"].value_counts())

print("\n🗂️ Breached Information Location (Top 10):\n")
print(top10["Location of Breached Information"].value_counts())

print("\n📅 Year Distribution (Top 10):\n")
print(top10["Year"].value_counts().sort_index())

# Top 10 Share of Overall Impact
top10_total = top10["Individuals Affected"].sum()
overall_total = df["Individuals Affected"].sum()
percent = (top10_total / overall_total) * 100

print(f"\n📊 Total Individuals Affected (Top 10): {top10_total:,}")
print(f"📊 Total Individuals Affected (Overall): {overall_total:,}")
print(f"🔥 Top 10 breaches account for {percent:.2f}% of total individuals affected.")


#==========
# ANALYSIS
#==========

# Here, I am highlighting the most impactful breaches by number of indviduals affected, offering insight into their characteristics, severity, and systemic patterns. 
# There appears to be a disproportional impact where just ten breaches account for nearly 77% of all indviduals affected, showing the extreme skew of breach severity.
# A Mann-Whitney U test confirms a statistically significant difference (U = 7800.0, p < 0.0001), meaning the top ten breaches are significantly more severe than the rest.
# Eight out of ten breaches were due to Hacking/IT Incidents and ten out of ten were targeted at Network Servers, indicating a vulnerability in network infrastructure and highlights the importance of modernizing server security practices.

