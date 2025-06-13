from services.import_csv import import_weather_data
from config import DB_URL

file_path = "GlobalWeatherRepository.csv"
import_weather_data(file_path, DB_URL)
