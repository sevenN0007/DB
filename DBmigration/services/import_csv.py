import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.weather import Base, CountryWeather, WindInfo, WindDirection

def import_weather_data(file_path, db_url):
    df = pd.read_csv(file_path)

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    for _, row in df.iterrows():
        try:
            if pd.isna(row['sunrise']):
                continue

            sunrise_time = datetime.strptime(row['sunrise'], '%I:%M %p').time()

            direction = row['wind_direction']
            if direction in WindDirection.__members__:
                wind_direction_enum = WindDirection[direction]
            else:
                wind_direction_enum = WindDirection.N

            go_outside = row['wind_kph'] <= 10

            weather = CountryWeather(
                country=row['country'],
                last_updated=datetime.strptime(row['last_updated'], '%Y-%m-%d %H:%M').date(),
                sunrise=sunrise_time
            )

            wind = WindInfo(
                wind_degree=int(row['wind_degree']),
                wind_kph=float(row['wind_kph']),
                wind_direction=wind_direction_enum,
                go_outside=go_outside
            )

            weather.wind = wind
            session.add(weather)

        except Exception as e:
            print(f"Помилка обробки рядка: {e}")

    session.commit()
    session.close()

if __name__ == "__main__":
    from config import DB_URL
    import_weather_data("services/GlobalWeatherRepository.csv", DB_URL)

