-- Compares cities over the same completed years, 2020-2025.
CREATE OR REPLACE VIEW vw_long_term_city_comparison AS
WITH yearly AS (
    SELECT
        city_id,
        EXTRACT(YEAR FROM date)::int AS year,
        AVG(temperature_mean) AS avg_mean,
        AVG(temperature_max)  AS avg_max,
        AVG(temperature_min)  AS avg_min,
        SUM(precipitation_mm) AS precip,
        SUM(rain_mm)          AS rain,
        AVG(wind_speed_max)   AS wind,
        AVG(sunshine_hours)   AS sunshine,
        COUNT(*) FILTER (WHERE precipitation_mm >= 1.0)      AS rainy_days,
        COUNT(*) FILTER (WHERE temperature_mean IS NOT NULL) AS observed_days
    FROM fact_daily_weather
    WHERE date >= DATE '2020-01-01' AND date < DATE '2026-01-01'
    GROUP BY city_id, EXTRACT(YEAR FROM date)::int
)
SELECT
    d.city_id,
    d.city,
    d.state,
    COUNT(*) AS years_used,
    ROUND(AVG(y.avg_mean)::numeric, 2) AS avg_annual_mean_temp,
    ROUND(AVG(y.avg_max)::numeric, 2)  AS avg_annual_max_temp,
    ROUND(AVG(y.avg_min)::numeric, 2)  AS avg_annual_min_temp,
    ROUND(AVG(y.precip)::numeric, 1)   AS avg_annual_precipitation_mm,
    ROUND(AVG(y.rain)::numeric, 1)     AS avg_annual_rain_mm,
    ROUND(AVG(y.wind)::numeric, 2)     AS avg_daily_max_wind_kmh,
    ROUND(AVG(y.sunshine)::numeric, 2) AS avg_daily_sunshine_hours,
    ROUND(AVG(y.rainy_days)::numeric, 1) AS avg_annual_rainy_days,
    ROUND(AVG(y.observed_days::numeric
              / (make_date(y.year, 12, 31) - make_date(y.year, 1, 1) + 1) * 100), 2) AS avg_coverage_pct
FROM yearly y
JOIN dim_city d ON d.city_id = y.city_id
GROUP BY d.city_id, d.city, d.state;