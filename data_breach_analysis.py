import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest


#======================
# BREACH COUNT BY YEAR
#======================
# Import Data
df = pd.read_csv("breach_report.csv")  

# PERCENT CHANGE
# Reformat Date
df["Breach Submission Date"] = pd.to_datetime(df["Breach Submission Date"])

# Extract the Year
df["Year"] = df["Breach Submission Date"].dt.year
breach_counts = df.groupby("Year").size().reset_index(name="Breach Count")

# Calculate Percent Change
breach_counts["% Change"] = breach_counts["Breach Count"].pct_change() * 100
print(round(breach_counts, 2))

# CHI-SQUARE TEST OF INDEPENDENCE
contingency = pd.crosstab(df["Year"], df["Type of Breach"])
chi2, p, dof, expected = chi2_contingency(contingency)

print("Chi-square statistic:", round(chi2, 4))
print("p-value:", round(p, 4))

if p < 0.05:
    print("Result: Significant association between breach type and year")
else:
    print("Result: No significant association between breach type and year")

# PROPORTION OF HACKING BREACHES TEST BETWEEN YEARS
breach_types = df["Type of Breach"].dropna().unique()
years = [2023, 2024, 2025]
comparisons = [(0, 1), (0, 2), (1, 2)]

# Total Breaches per Year
totals = {y: df[df["Year"] == y].shape[0] for y in years}

# Run Pairwise Proportion Z-Tests for Each Breach Type
for breach in breach_types:
    print(f"\n🔍 Testing breach type: {breach}")
    # Count Breaches of This Type per Year
    counts = {y: df[(df["Year"] == y) & (df["Type of Breach"] == breach)].shape[0] for y in years}
    
    for i, j in comparisons:
        count_vals = [counts[years[i]], counts[years[j]]]
        total_vals = [totals[years[i]], totals[years[j]]]

        # (only test if at least one count > 0)
        if sum(count_vals) > 0:
            stat, pval = proportions_ztest(count_vals, total_vals)
            print(f"{years[i]} vs {years[j]} → z = {stat:.2f}, p = {pval:.4f}", end=" ")
            if pval < 0.05:
                print("→ ✅ Significant")
            else:
                print("→ ❌ Not significant")


#==========
# Analysis
#==========

# Between 2023 and 2025, there was significant fluctuation in the number of reported healthcare data breaches.
# In 2023, 100 breaches were reported, in 2024, this number almost quadrupled reaching 396 breaches (a 296% increase) before declining to 294 in 2025 (25.8% decrease).
# Despite this drop, breach levels in 2025 were almost triple as high as in 2023. 

# A chi-square test of independence confirmed significant association between breach type and year (χ² = 31.54, p <0.001) which indicates that the distribution of breach types had meaningfully changed over time.

# Looking at specific breach types, 
    # Hacking/IT Incidents showed significant increases over the years and were the most common breach type. 
        # Each pairwise comparison yielded statistically significatn results (all p < 0.01) over the years.
    # Unauthorized Access/Disclosure also showed significant increases over the years, following a similar patter to Hacking/IT Incidents.
        # Each pairwise comparison yielded statistically significatn results (all p <0.01) over the years.
    # Improper Disposal, Theft, and Loss did not show statistically significant changes across years (all p > 0.01), suggesting these breaches may be less volatile or requently reported.

# These findings suggest that hacking and unauthorized access are becoming increasingly dominant and statistically distinguishable from other breach types within the healthcare spector. 

