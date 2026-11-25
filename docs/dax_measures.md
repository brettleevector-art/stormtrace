# DAX used in STORMTRACE.pbix

## Calendar table
```
dim_date =
VAR first_year = YEAR(MIN(fact_daily_weather[date]))
VAR last_year  = YEAR(MAX(fact_daily_weather[date]))
RETURN
ADDCOLUMNS(
    CALENDAR(DATE(first_year, 1, 1), DATE(last_year, 12, 31)),
    "year", YEAR([Date]),
    "month_number", MONTH([Date]),
    "month_name", FORMAT([Date], "mmmm"),
    "month_short", FORMAT([Date], "mmm"),
    "year_month", FORMAT([Date], "yyyy-mm"),
    "season", SWITCH(TRUE(), MONTH([Date]) <= 2, "Winter", MONTH([Date]) <= 5, "Pre-monsoon", MONTH([Date]) <= 9, "Southwest monsoon", "Post-monsoon"),
    "season_sort", SWITCH(TRUE(), MONTH([Date]) <= 2, 1, MONTH([Date]) <= 5, 2, MONTH([Date]) <= 9, 3, 4)
)
```

## Measures (on fact_daily_weather)
```
Avg Temp (°C) = AVERAGE(fact_daily_weather[temperature_mean])
Avg Max Temp (°C) = AVERAGE(fact_daily_weather[temperature_max])
Avg Min Temp (°C) = AVERAGE(fact_daily_weather[temperature_min])
Total Rainfall (mm) = SUM(fact_daily_weather[precipitation_mm])
Rainy Days (≥1 mm) = CALCULATE(COUNTROWS(fact_daily_weather), fact_daily_weather[precipitation_mm] >= 1)
Days Observed = COUNTROWS(fact_daily_weather)
Last Observed Date = CALCULATE(MAX(fact_daily_weather[date]), fact_daily_weather[temperature_mean] <> BLANK())
Data Through = CALCULATE(MAX(fact_daily_weather[date]), REMOVEFILTERS(dim_date), REMOVEFILTERS(dim_city), fact_daily_weather[temperature_mean] <> BLANK())
```

## Calculated column (vw_monthly_temperature_anomalies)
```
month_start = DATE(vw_monthly_temperature_anomalies[year], vw_monthly_temperature_anomalies[month_number], 1)
```

## Colour measure (anomaly chart)
```
Anomaly Colour = IF(AVERAGE(vw_monthly_temperature_anomalies[temperature_anomaly]) >= 0, "#C0392B", "#2E75B6")
```

## Relationships
dim_city[city_id] → fact_daily_weather and the five vw_ views (one-to-many, single direction).
dim_date[Date] → fact_daily_weather[date] (one-to-many, single direction).