-- One row per city per year. 2026 is flagged partial and judged against days elapsed.
CREATE OR REPLACE VIEW vw_annual_weather_summary AS
WITH latest AS (
    SELECT MAX(date) AS max_date FROM fact_daily_weather
),
yearly AS (
    SELECT
        city_id,
        EXTRACT(YEAR FROM date)::int AS year,
        AVG(temperature_mean) AS avg_temperature_mean,
        AVG(temperature_max)  AS avg_temperature_max,
        AVG(temperature_min)  AS avg_temperature_min,
        SUM(precipitation_mm) AS total_precipitation_mm,
        SUM(rain_mm)          AS total_rain_mm,
        AVG(wind_speed_max)   AS avg_wind_speed_max,
        AVG(sunshine_hours)   AS avg_sunshine_hours,
        COUNT(*) FILTER (WHERE precipitation_mm >= 1.0)      AS rainy_days,
        COUNT(*) FILTER (WHERE temperature_mean IS NOT NULL) AS observed_days
    FROM fact_daily_weather
    GROUP BY city_id, EXTRACT(YEAR FROM date)::int
),
scoped AS (
    SELECT
        y.*,
        l.max_date,
        (LEAST(make_date(y.year, 12, 31), l.max_date) - make_date(y.year, 1, 1) + 1) AS expected_days
    FROM yearly y
    CROSS JOIN latest l
)
SELECT
    d.city_id,
    d.city,
    d.state,
    s.year,
    CASE WHEN make_date(s.year, 12, 31) > s.max_date
         THEN s.year::text || ' (partial)' ELSE s.year::text END AS year_label,
    (make_date(s.year, 12, 31) > s.max_date) AS is_partial_year,
    ROUND(s.avg_temperature_mean::numeric, 2) AS avg_temperature_mean,
    ROUND(s.avg_temperature_max::numeric, 2)  AS avg_temperature_max,
    ROUND(s.avg_temperature_min::numeric, 2)  AS avg_temperature_min,
    ROUND(s.total_precipitation_mm::numeric, 1) AS total_precipitation_mm,
    ROUND(s.total_rain_mm::numeric, 1)          AS total_rain_mm,
    ROUND(s.avg_wind_speed_max::numeric, 2)     AS avg_wind_speed_max,
    ROUND(s.avg_sunshine_hours::numeric, 2)     AS avg_sunshine_hours,
    s.rainy_days,
    s.observed_days,
    s.expected_days,
    ROUND(s.observed_days::numeric / s.expected_days * 100, 1) AS coverage_pct
FROM scoped s
JOIN dim_city d ON d.city_id = s.city_id;