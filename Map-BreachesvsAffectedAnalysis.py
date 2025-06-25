import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore

#==============================
# MAP OF BREACHES VS. AFFECTED
#==============================

# Data
df = pd.read_csv("breach_report.csv")  
df["Individuals Affected"] = pd.to_numeric(df["Individuals Affected"], errors="coerce")
df["State"] = df["State"].str.upper() 

# Aggregate by State
by_state = df.groupby("State").agg({
    "Name of Covered Entity": "count",
    "Individuals Affected": "sum"
}).rename(columns={
    "Name of Covered Entity": "Breach Count",
    "Individuals Affected": "Total Affected"
}).reset_index()

# Correlation Analysis
print("\n🔗 Correlation Between Breach Count and Total Affected:\n")
print(by_state[["Breach Count", "Total Affected"]].corr())

# Most Severe States (Avg Affected Per Breach)
by_state["Avg Affected per Breach"] = by_state["Total Affected"] / by_state["Breach Count"]
top_severity = by_state.sort_values("Avg Affected per Breach", ascending=False).head(10)
print("\n🔥 Top 10 Most Severe States (Avg Affected per Breach):\n")
print(top_severity[["State", "Breach Count", "Total Affected", "Avg Affected per Breach"]])

# Statistical Outliers (Z-scores)
by_state["Breach Z"] = zscore(by_state["Breach Count"])
by_state["Impact Z"] = zscore(by_state["Total Affected"])

outliers = by_state[(by_state["Breach Z"].abs() > 2) | (by_state["Impact Z"].abs() > 2)]
print("\n🚨 Statistical Outlier States:\n")
print(outliers[["State", "Breach Count", "Total Affected", "Breach Z", "Impact Z"]])


#==========
# ANALYSIS
#==========

# This interactive map is exploring the geographic dimension of breach incidents, allowing users to toggle between Breach Count and Total Indivduals Affected for each US state (with readily available data).
# Texas, New York, and California report the highest number of data breaches, at 72, 57, and 54 respectively. 
# Minnesota has over 190 million indivduals affected, which was driven by a small number of high-severity data breaches. 
# My correlation analysis shows a weak relationship (r = 0.14) between breach count and total affected per state, indicating that breach volume is not a reliable predictor of breach severity. 
# These four mentioned states, along with Illinois, all appear to be statistical outliers.
# Minnesota has a breach count of 19, but high impact due to a few massive incidents, resulting in a Z-score of 6.67.
# California, Texas, and New York all have significantly above-average breach counts, with Z-Scores > 2.3, but a bit less extreme in individuals affected.
# Illinois, has a high breach count of 52 without a corresponding high impact, making it an interesting outlier in the opposite direction.


