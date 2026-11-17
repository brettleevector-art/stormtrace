-- Per-city completeness. Missing values are counted, never hidden.
CREATE OR REPLACE VIEW vw_data_quality_summary AS
WITH latest AS (
    SELECT MAX(date) AS max_date FROM fact_daily_weather
)
SELECT
    d.city_id,
    d.city,
    d.state,
    COUNT(*)                                AS record_count,
    MIN(f.date)                             AS first_date,
    MAX(f.date)                             AS last_date,
    (l.max_date - DATE '2020-01-01' + 1)    AS expected_days,
    (l.max_date - DATE '2020-01-01' + 1) - COUNT(*) AS missing_day_rows,
    ROUND(COUNT(*) FILTER (WHERE f.temperature_mean IS NOT NULL)::numeric
          / (l.max_date - DATE '2020-01-01' + 1) * 100, 2) AS coverage_pct,
    COUNT(*) - COUNT(DISTINCT f.date)       AS duplicate_count,
    COUNT(*) FILTER (WHERE f.temperature_max     IS NULL) AS missing_temperature_max,
    COUNT(*) FILTER (WHERE f.temperature_min     IS NULL) AS missing_temperature_min,
    COUNT(*) FILTER (WHERE f.temperature_mean    IS NULL) AS missing_temperature_mean,
    COUNT(*) FILTER (WHERE f.precipitation_mm    IS NULL) AS missing_precipitation_mm,
    COUNT(*) FILTER (WHERE f.rain_mm             IS NULL) AS missing_rain_mm,
    COUNT(*) FILTER (WHERE f.precipitation_hours IS NULL) AS missing_precipitation_hours,
    COUNT(*) FILTER (WHERE f.weather_code        IS NULL) AS missing_weather_code,
    COUNT(*) FILTER (WHERE f.wind_speed_max      IS NULL) AS missing_wind_speed_max,
    COUNT(*) FILTER (WHERE f.wind_direction      IS NULL) AS missing_wind_direction,
    COUNT(*) FILTER (WHERE f.sunshine_hours      IS NULL) AS missing_sunshine_hours,
    MAX(f.loaded_at)                        AS last_loaded_at
FROM fact_daily_weather f
JOIN dim_city d ON d.city_id = f.city_id
CROSS JOIN latest l
GROUP BY d.city_id, d.city, d.state, l.max_date;


