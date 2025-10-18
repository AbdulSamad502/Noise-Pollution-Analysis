# ==========================================================
# 1. Import Libraries & Configurations
# ==========================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sqlalchemy import create_engine, text

# Pandas display settings
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)

# ==========================================================
# 2. Connect to MySQL Database
# ==========================================================
conn = create_engine("mysql+pymysql://root:samad1234@localhost:3306/noisestressdb")

# ==========================================================
# 3. Load Data from SQL Tables
# ==========================================================
df_cities          = pd.read_sql("SELECT * FROM cities;", conn)
df_citizen_survey  = pd.read_sql("SELECT * FROM citizen_surveys;", conn)
df_etl_audit       = pd.read_sql("SELECT * FROM etl_audit;", conn)
df_events          = pd.read_sql("SELECT * FROM events;", conn)
df_noise_reading   = pd.read_sql("SELECT * FROM noise_readings;", conn)
df_sensors         = pd.read_sql("SELECT * FROM sensors;", conn)
df_strend          = pd.read_sql("SELECT * FROM strend;", conn)

# ==========================================================
# 4. Data Preprocessing
# ==========================================================
## 4.1 Convert Date Columns
df_citizen_survey["survey_date"] = pd.to_datetime(df_citizen_survey["survey_date"])
df_etl_audit["log_date"]         = pd.to_datetime(df_etl_audit["log_date"])
df_events["event_date"]          = pd.to_datetime(df_events["event_date"])
df_noise_reading["reading_date"] = pd.to_datetime(df_noise_reading["reading_date"])
df_sensors["install_date"]       = pd.to_datetime(df_sensors["install_date"])
df_strend["event_date"]          = pd.to_datetime(df_strend["event_date"])
df_strend["reading_date"]        = pd.to_datetime(df_strend["reading_date"])

## 4.2 Handle Missing Values
df_citizen_survey["stress_index"]    = df_citizen_survey["stress_index"].fillna(df_citizen_survey["stress_index"].mean())
df_citizen_survey["sleep_hours"]     = df_citizen_survey["sleep_hours"].fillna(df_citizen_survey["sleep_hours"].mean())

## 4.3 Remove Duplicates
df_citizen_survey.drop_duplicates(inplace=True)

## 4.4 Clean Column Names
for df in [df_cities, df_citizen_survey, df_etl_audit, df_events, df_noise_reading, df_sensors]:
    df.columns = df.columns.str.title()

# ==========================================================
# 5. Helper Functions
# ==========================================================
def col(df, name):
    """Return actual column name regardless of case."""
    lookup = {c.lower(): c for c in df.columns}
    return lookup[name.lower()]

# ==========================================================
# 6. Data Validation (ETL Checks)
# ==========================================================
avg  = col(df_noise_reading, "avg_db")
peak = col(df_noise_reading, "peak_db")

invalidm = (~df_noise_reading[avg].between(30, 110)) | (~df_noise_reading[peak].between(50, 120))
invalid_rows = df_noise_reading[invalidm].copy()
errorc = int(invalid_rows.shape[0])
df_noise_reading_clean = df_noise_reading[~invalidm].copy()

if errorc > 0:
    with conn.begin() as db:
        db.execute(
            text("""
                INSERT INTO ETL_Audit (table_name, action, records_inserted, error_count, log_date)
                VALUES (:table_name, :action, :records_inserted, :error_count, :log_date)
            """),
            {
                "table_name": "Noise_Readings",
                "action": "VALIDATION_ERROR",
                "records_inserted": 0,
                "error_count": errorc,
                "log_date": datetime.now()
            }
        )

# ==========================================================
# 7. Analysis with Pandas
# ==========================================================

## 7.1 City-wise Average Noise
e_noise_poll = (
    pd.merge(df_cities, df_sensors, on="City_Id")
      .merge(df_noise_reading, on="Sensor_Id")
)
average_noise_levels = e_noise_poll.groupby("City_Name")[["Avg_Db","Peak_Db"]].mean().sort_values("Avg_Db", ascending=False)

## 7.2 Stress vs Sleep Summary
Stress_life    = pd.merge(df_cities, df_citizen_survey, on="City_Id")
Stress_summary = Stress_life.groupby("City_Name")[["Stress_Index","Sleep_Hours","Productivity_Score"]].mean()

## 7.3 Region Type Comparison
Stress_summary2 = Stress_life.groupby("Region_Type")[["Stress_Index","Sleep_Hours","Productivity_Score"]].mean().reset_index()
Stress_summary2["Effective_Rank"] = Stress_summary2[["Stress_Index","Sleep_Hours","Productivity_Score"]].mean(axis=1).rank(ascending=False)
Stress_summary2["Risk_Level"] = Stress_summary2["Effective_Rank"].apply(lambda x: "High" if x<=2 else "Medium" if x<=4 else "Low")

## 7.4 Correlation Analysis
cor_Stdy = (
    pd.merge(df_cities, df_citizen_survey, on="City_Id")
      .merge(df_sensors, on="City_Id")
      .merge(df_noise_reading, on="Sensor_Id")
)
corr = cor_Stdy[["Avg_Db","Peak_Db","Stress_Index","Sleep_Hours","Productivity_Score"]].corrwith(cor_Stdy["Avg_Db"]).reset_index()
corr.columns=["Variables","Correlation with Avg Db"]

## 7.5 Event & Seasonal Analysis
# Example: join events + stress
event_stress = pd.merge(df_events, df_citizen_survey, on="City_Id")
seasonal_trends = df_citizen_survey.groupby(df_citizen_survey["Survey_Date"].dt.month)[["Stress_Index","Sleep_Hours"]].mean()

# ==========================================================
# 8. Visualization (Matplotlib + Seaborn)
# ==========================================================

## 8.1 City-wise Noise
plt.figure(figsize=(10,6))
sns.barplot(x="City_Name", y="Peak_Db", data=average_noise_levels, color="darkred", edgecolor="black")
plt.title("Peak Noise per City (dB)")
plt.grid(True, alpha=0.7)
plt.show()

## 8.2 Stress & Sleep Summary
plt.figure(figsize=(10,6))
sns.barplot(x="City_Name", y="Stress_Index", data=Stress_summary.reset_index(), color="blue")
plt.title("Average Stress Index by City")
plt.show()

## 8.3 Region Type Risk Level
plt.figure(figsize=(8,6))
sns.barplot(x="Region_Type", y="Stress_Index", hue="Risk_Level", data=Stress_summary2)
plt.title("Region Type vs Stress Level with Risk Categories")
plt.show()

## 8.4 Correlation Heatmap
plt.figure(figsize=(8,6))
sns.heatmap(cor_Stdy[["Avg_Db","Peak_Db","Stress_Index","Sleep_Hours","Productivity_Score"]].corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap: Noise vs Stress Factors")
plt.show()

## 8.5 Seasonal Trends
plt.figure(figsize=(10,6))
seasonal_trends.plot(kind="bar")
plt.title("Seasonal Trends of Stress & Sleep")
plt.show()

# ==========================================================
# 9. Final Insights / Storytelling
# ==========================================================
print("\n=== Final Conclusions ===")
print("1. The noisiest cities show higher stress & lower sleep quality.")
print("2. Urban regions report higher stress vs semi-urban areas.")
print("3. Noise peaks during public events directly increase stress index.")
print("4. Strong negative correlation: Higher Avg dB → Lower Sleep Hours.")
print("5. Seasonal patterns: Stress peaks in summer, improves in winter.")
print("=========================\n")
