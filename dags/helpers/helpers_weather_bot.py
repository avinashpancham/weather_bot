import pandas as pd


def kelvin_to_celsius(temperature: float) -> float:
    return temperature - 273.15


def get_first_day(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(by='dt').head(24).assign(hour= lambda df: pd.to_datetime(df.dt, unit='s').dt.hour)


def expand_weather(df: pd.DataFrame) -> pd.DataFrame:
    df_weather = pd.DataFrame(df.weather.str[0].tolist())
    return df.join(df_weather)


def get_weather_metrics(df: pd.DataFrame) -> (float, float, str):
    return kelvin_to_celsius(df.temp.mean()), kelvin_to_celsius(df.feels_like.mean()), 'Yes' if df.rain.notnull().any() else 'No'


def get_weather_description(df: pd.DataFrame) -> str:
    first_hour = df.iloc[0].hour
    df_description = df.assign(end_hour=lambda df: df.hour + 1,
                                        next_main=lambda df: df.main.shift(-1)) \
        .query('main!=next_main') \
        .assign(start_hour=lambda df: (df.hour.shift(1) + 1).fillna(first_hour).astype(int)) \
        .astype(str)
    
    return '\n'.join('From ' + df_description['start_hour'] + ' till ' + df_description['end_hour'] + ': ' + df_description.main)


def create_weather_message(temperature: float, apparent_temperature: float, rain: str, weather_description: str) -> str:
    return f"""
Goodmorning,

Todays weather forecast for Den Haag is:
Temperature: {temperature:.1f}
Apparent temperature: {apparent_temperature:.1f}
Rain: {rain}
Weather:
{weather_description}
"""


def parse_response(**context):
    response = context['task_instance'].xcom_pull(task_ids='get_weather')

    redundant_columns = ['dt', 'pressure', 'humidity', 'dew_point', 'clouds', 'visibility',
                         'wind_speed', 'wind_deg', 'pop', 'id', 'description',
                         'icon', 'weather']

    df_forecast = pd.DataFrame(response['hourly']).pipe(get_first_day).pipe(expand_weather).drop(columns=redundant_columns)

    temperature, apparent_temperature, rain = get_weather_metrics(df=df_forecast)
    weather_description = get_weather_description(df=df_forecast)

    return create_weather_message(temperature=temperature, apparent_temperature=apparent_temperature,
                                 rain=rain, weather_description=weather_description)


