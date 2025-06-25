import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

#===============================
# ENTITY TYPE BREAKDOWN BY YEAR
#===============================

# Data
df = pd.read_csv("breach_report.csv")  
df["Breach Submission Date"] = pd.to_datetime(df["Breach Submission Date"])
df["Year"] = df["Breach Submission Date"].dt.year

# Breach Count by Entity Type and Year
entity_year = df.groupby(["Year", "Covered Entity Type"]).size().unstack(fill_value=0)
print("📊 Breach Counts by Entity Type and Year:\n")
print(entity_year)

# Percentage Breakdown by Year
entity_percent = entity_year.div(entity_year.sum(axis=1), axis=0) * 100
print("\n📈 Percentage Share of Entity Types per Year:\n")
print(entity_percent.round(2))

# Chi-Square Test:
chi2, p, dof, expected = chi2_contingency(entity_year)
print(f"\n🔬 Chi-Square Test Results:")
print(f"Chi² statistic: {chi2:.2f}")
print(f"Degrees of freedom: {dof}")
print(f"p-value: {p:.4f}")

if p < 0.05:
    print("✅ Significant change in entity type distribution over years")
else:
    print("❌ No statistically significant change over time")


#==========
# ANALYSIS
#==========

# These findings tell us that Healthcare Providers consistently account for the majority of healthcare related data breaches, peaking in 2024 with 73.2% of data breaches.  
# Business Associates shows some more fluctuation, raning between 18 and 25%.
# Health Plans and Healthcare Clearinghouses remain pretty low across all years. 

# A chi-square test was run to assess whether the distribution of entity types changed signficantly over time. 
# The results were χ² = 2.73, df = 6, and p = 0.8415 telling us that were no statistically significant changes, the proportional involvement of different entity types has remained fairly stable over these three years.   