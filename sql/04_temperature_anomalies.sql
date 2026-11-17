-- Anomaly = month's mean temperature minus the 2020-2025 baseline for that city and month.
CREATE OR REPLACE VIEW vw_monthly_temperature_anomalies AS
WITH monthly AS (
    SELECT
        city_id,
        EXTRACT(YEAR FROM date)::int  AS year,
        EXTRACT(MONTH FROM date)::int AS month_number,
        AVG(temperature_mean)   AS monthly_mean_temp,
        COUNT(temperature_mean) AS valid_days,
        EXTRACT(DAY FROM (date_trunc('month', MIN(date))::date
                          + INTERVAL '1 month' - INTERVAL '1 day'))::int AS days_in_month
    FROM fact_daily_weather
    GROUP BY city_id, EXTRACT(YEAR FROM date)::int, EXTRACT(MONTH FROM date)::int
),
complete_months AS (
    SELECT * FROM monthly WHERE valid_days = days_in_month
),
baseline AS (
    SELECT
        city_id,
        month_number,
        AVG(monthly_mean_temp) AS baseline_mean_temp,
        COUNT(*)               AS baseline_year_count
    FROM complete_months
    WHERE year BETWEEN 2020 AND 2025
    GROUP BY city_id, month_number
    HAVING COUNT(*) = 6
)
SELECT
    d.city_id,
    d.city,
    d.state,
    c.year,
    c.month_number,
    TO_CHAR(make_date(2000, c.month_number, 1), 'FMMonth') AS month_name,
    ROUND(c.monthly_mean_temp::numeric, 2)  AS monthly_mean_temp,
    ROUND(b.baseline_mean_temp::numeric, 2) AS baseline_mean_temp,
    ROUND((c.monthly_mean_temp - b.baseline_mean_temp)::numeric, 2) AS temperature_anomaly,
    b.baseline_year_count,
    TRUE AS is_complete_month
FROM complete_months c
JOIN baseline b ON b.city_id = c.city_id AND b.month_number = c.month_number
JOIN dim_city d ON d.city_id = c.city_id;