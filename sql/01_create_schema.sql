-- STORMTRACE warehouse schema. Safe to run more than once.

CREATE TABLE IF NOT EXISTS dim_city (
    city_id   INTEGER PRIMARY KEY,
    city      VARCHAR(100) NOT NULL,
    state     VARCHAR(100) NOT NULL,
    country   VARCHAR(100) NOT NULL,
    latitude  DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_daily_weather (
    city_id             INTEGER NOT NULL REFERENCES dim_city (city_id),
    date                DATE NOT NULL,
    temperature_max     DOUBLE PRECISION CHECK (temperature_max  BETWEEN -60 AND 60),
    temperature_min     DOUBLE PRECISION CHECK (temperature_min  BETWEEN -60 AND 60),
    temperature_mean    DOUBLE PRECISION CHECK (temperature_mean BETWEEN -60 AND 60),
    precipitation_mm    DOUBLE PRECISION CHECK (precipitation_mm >= 0),
    rain_mm             DOUBLE PRECISION CHECK (rain_mm >= 0),
    precipitation_hours DOUBLE PRECISION CHECK (precipitation_hours BETWEEN 0 AND 24),
    weather_code        INTEGER,
    wind_speed_max      DOUBLE PRECISION CHECK (wind_speed_max >= 0),
    wind_direction      DOUBLE PRECISION CHECK (wind_direction BETWEEN 0 AND 360),
    sunshine_hours      DOUBLE PRECISION CHECK (sunshine_hours BETWEEN 0 AND 24),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (city_id, date)
);

CREATE INDEX IF NOT EXISTS idx_fact_daily_weather_date ON fact_daily_weather (date);