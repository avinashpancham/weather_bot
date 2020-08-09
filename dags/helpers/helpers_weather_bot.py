import json
import os
from datetime import datetime

import pandas as pd


def get_lat_lon() -> pd.Series:
    city, country = [address.strip() for address in os.environ['LOCATION'].split(',')]
    df = pd.read_csv('dags/data/worldcities.csv', usecols=['iso2', 'country', 'city', 'lat', 'lng']).query(f"iso2=='{country}' and city=='{city}'")
    assert len(df) == 1, 'Provided location is either not found or ambiguous'
    return df.iloc[0]


def get_first_day(df: pd.DataFrame, timezone_offset: int) -> pd.DataFrame:
    return (
        df.sort_values(by="dt")
        .head(24)
        .assign(
            hour=lambda df: pd.to_datetime(df.dt + timezone_offset, unit="s").dt.hour
        )
    )


def expand_weather_column(df: pd.DataFrame) -> pd.DataFrame:
    df_weather = pd.DataFrame(df.weather.str[0].tolist())
    return df.join(df_weather)


def get_weather_metrics(df: pd.DataFrame) -> (float, float, str):
    return (
        df.temp.mean(),
        df.feels_like.mean(),
        "Yes" if "rain" in df else "No",
    )


def get_weather_description(df: pd.DataFrame) -> str:
    first_hour = df.iloc[0].hour
    df_description = (
        df.assign(
            end_hour=lambda df: df.hour + 1, next_main=lambda df: df.main.shift(-1)
        )
        .query("main!=next_main")
        .assign(
            start_hour=lambda df: (df.hour.shift(1) + 1).fillna(first_hour).astype(int)
        )
        .astype(str)
    )

    return "\n".join(
        "\t - From "
        + df_description["start_hour"]
        + " till "
        + df_description["end_hour"]
        + ": "
        + df_description.main
    )


def create_weather_message(
    city: str, temperature: float, apparent_temperature: float, rain: str, description: str
) -> str:
    return f"""
Weather forecast {city} for {datetime.now().strftime('%d-%m')}

Average temperature: {temperature:.1f} °C
Average apparent temperature: {apparent_temperature:.1f} °C
Potential rain: {rain}
Hourly forecast:
{description}
"""


def parse_weather_response(city: str, **context) -> str:
    response = json.loads(context["task_instance"].xcom_pull(task_ids="get_weather"))
    redundant_columns = [
        "dt",
        "pressure",
        "humidity",
        "dew_point",
        "clouds",
        "visibility",
        "wind_speed",
        "wind_deg",
        "pop",
        "id",
        "description",
        "icon",
        "weather",
    ]

    df_forecast = (
        pd.DataFrame(response["hourly"])
        .pipe(get_first_day, timezone_offset=response["timezone_offset"])
        .pipe(expand_weather_column)
        .drop(columns=redundant_columns)
    )

    temperature, apparent_temperature, rain = get_weather_metrics(df=df_forecast)
    weather_description = get_weather_description(df=df_forecast)

    return create_weather_message(
        city=city,
        temperature=temperature,
        apparent_temperature=apparent_temperature,
        rain=rain,
        description=weather_description,
    )
