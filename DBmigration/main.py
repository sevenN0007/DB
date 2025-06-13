from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.weather import CountryWeather, WindInfo


def search_weather():
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    country = input("Введіть країну: ").strip()
    date_str = input("Введіть дату (yyyy-mm-dd): ").strip()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Невірний формат дати. Використовуйте формат yyyy-mm-dd.")
        return

    results = session.query(CountryWeather).join(WindInfo).filter(
        CountryWeather.country == country,
        CountryWeather.last_updated == date
    ).all()

    if not results:
        print("Даних не знайдено.")
    else:
        for record in results:
            print(f"""
Країна: {record.country}
Дата: {record.last_updated}
Схід сонця: {record.sunrise}
Напрямок вітру: {record.wind.wind_direction.value}
Швидкість вітру: {record.wind.wind_kph} км/год
Кут вітру: {record.wind.wind_degree}
Чи можна виходити: {"Так" if record.wind.go_outside else "Ні"}
            """)

    session.close()

if __name__ == "__main__":
    search_weather()


#
# alembic -c alembic.ini revision --autogenerate -m "Initial structure Postgresql"
# alembic upgrade head
# python -m services.import_csv


#alembic -c alembic_mysql.ini revision --autogenerate -m "Init MySQL"
#alembic -c alembic_mysql.ini upgrade head
#python -m services.import_csv
