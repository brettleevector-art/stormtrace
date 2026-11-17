-- Average of six monthly rainfall TOTALS (2020-2025), complete months only.
CREATE OR REPLACE VIEW vw_monthly_rainfall_climatology AS
WITH monthly AS (
    SELECT
        city_id,
        EXTRACT(YEAR FROM date)::int  AS year,
        EXTRACT(MONTH FROM date)::int AS month_number,
        SUM(rain_mm)   AS monthly_rain_mm,
        COUNT(rain_mm) AS valid_days,
        EXTRACT(DAY FROM (date_trunc('month', MIN(date))::date
                          + INTERVAL '1 month' - INTERVAL '1 day'))::int AS days_in_month
    FROM fact_daily_weather
    WHERE date >= DATE '2020-01-01' AND date < DATE '2026-01-01'
    GROUP BY city_id, EXTRACT(YEAR FROM date)::int, EXTRACT(MONTH FROM date)::int
),
complete_months AS (
    SELECT * FROM monthly WHERE valid_days = days_in_month
)
SELECT
    d.city_id,
    d.city,
    d.state,
    c.month_number,
    TO_CHAR(make_date(2000, c.month_number, 1), 'FMMonth') AS month_name,
    ROUND(AVG(c.monthly_rain_mm)::numeric, 1) AS avg_monthly_rain_mm,
    ROUND(MIN(c.monthly_rain_mm)::numeric, 1) AS min_monthly_rain_mm,
    ROUND(MAX(c.monthly_rain_mm)::numeric, 1) AS max_monthly_rain_mm,
    COUNT(*) AS baseline_years_used,
    (COUNT(*) = 6) AS baseline_complete
FROM complete_months c
JOIN dim_city d ON d.city_id = c.city_id
GROUP BY d.city_id, d.city, d.state, c.month_number;