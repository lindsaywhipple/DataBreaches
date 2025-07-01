import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, zscore, mannwhitneyu
from statsmodels.stats.proportion import proportions_ztest


#======================
# BREACH COUNT BY YEAR
#======================
print("BREACH COUNT BY YEAR:")
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


#=========================
# TOTAL AFFECTED PER YEAR
#=========================
print("TOTAL AFFECTED PER YEAR: ")
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


#==============================
# MAP OF BREACHES VS. AFFECTED
#==============================
print("MAP OF BREACHES VS. AFFECTED: ")
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


#===============================
# ENTITY TYPE BREAKDOWN BY YEAR
#===============================
print("ENTITY TYPE BREAKDOWN BY YEAR: ")
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



#=========================
# TOP 10 HARMFUL BREACHES
#=========================
print("TOP 10 HARMFUL BREACHES: ")
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

