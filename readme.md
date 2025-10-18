# Noise Pollution Analysis & Citizen Stress Project

## Project Overview
This project analyzes noise pollution data from multiple cities and its impact on citizen stress, sleep, and productivity. Using MySQL as the data source and Python (Pandas, SQLAlchemy, Matplotlib, Seaborn) for ETL, analysis, and visualization, the project provides insights into urban noise patterns and their effect on citizen well-being.

---

## Features
- Connects to a MySQL database (`noisestressdb`) to fetch tables like `cities`, `citizen_surveys`, `etl_audit`, `events`, `noise_readings`, `sensors`, and `strend`.
- Performs ETL tasks including:
  - Date conversion
  - Missing value handling
  - Duplicate removal
  - Column name standardization
- Validates noise readings and logs errors into an ETL audit table.
- Performs data analysis:
  - City-wise average noise levels
  - Stress vs sleep summaries
  - Region type comparisons with risk categories
  - Correlation analysis between noise and stress factors
  - Event & seasonal trend analysis
- Visualizes findings with Matplotlib and Seaborn:
  - City-wise peak noise bar plots
  - Average stress index by city
  - Region type vs stress level with risk categories
  - Correlation heatmaps
  - Seasonal trends of stress & sleep

---

## Technologies Used
- **Python 3.13**
- **Pandas** for data manipulation
- **NumPy** for numerical computations
- **Matplotlib & Seaborn** for visualization
- **SQLAlchemy** & **PyMySQL** for database connection
- **MySQL Workbench** as the database server

---

## Database Tables
- `cities` – city metadata
- `citizen_surveys` – citizen survey responses (stress index, sleep hours, productivity)
- `etl_audit` – ETL process logging
- `events` – city events data
- `noise_readings` – sensor noise measurements (avg_db, peak_db)
- `sensors` – sensor metadata
- `strend` – combined trends from noise and events

---

## Getting Started

#Install All Dependencies
pip install pandas numpy matplotlib seaborn sqlalchemy pymysql


# Configure Database Connection

Update the connection string in the Python script:

from sqlalchemy import create_engine

conn = create_engine("mysql+pymysql://root:samad1234@localhost:3306/noisestressdb")

# Run the Analysis
python Noise_pollution_cleaned.py



# Results
City-wise peak and average noise plots
Stress index and sleep quality analysis by city and region
Correlation analysis showing impact of noise on citizen well-being
Seasonal trends and event impact on stress

# Insights
Cities with higher noise levels show higher stress and lower sleep quality.
Urban regions report more stress than semi-urban regions.
Noise peaks during public events correlate with increased stress index.
Negative correlation observed: Higher average dB → Lower sleep hours.
Seasonal trends indicate stress peaks in summer and reduces in winter.

# Author

Abdul Samad

Email:samad784600@gmail.com

GitHub: https://github.com/AbdulSamad502