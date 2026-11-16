# STORMTRACE Data Dictionary

## Fact table: fact_daily_weather

| Column | Type | Description |
|---|---|---|
| city_id | INTEGER | City identifier |
| date | DATE | Local (Asia/Kolkata) date |
| temperature_max | DOUBLE PRECISION | Daily maximum temperature, °C |
| temperature_min | DOUBLE PRECISION | Daily minimum temperature, °C |
| temperature_mean | DOUBLE PRECISION | Daily mean temperature, °C |
| precipitation_mm | DOUBLE PRECISION | Daily precipitation total, mm |
| rain_mm | DOUBLE PRECISION | Daily rain total, mm |
| precipitation_hours | DOUBLE PRECISION | Hours with precipitation |
| weather_code | INTEGER | Model-derived WMO weather code |
| wind_speed_max | DOUBLE PRECISION | Maximum 10 m wind speed, km/h |
| wind_direction | DOUBLE PRECISION | Dominant wind direction, degrees |
| sunshine_hours | DOUBLE PRECISION | Sunshine duration, hours |

## Dimension table: dim_city

| Column | Type | Description |
|---|---|---|
| city_id | INTEGER | Primary key |
| city | VARCHAR | City name |
| state | VARCHAR | State |
| country | VARCHAR | Country |
| latitude | DOUBLE PRECISION | Requested latitude |
| longitude | DOUBLE PRECISION | Requested longitude |