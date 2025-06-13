from sqlalchemy import Column, Integer, String, Float, Enum, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import enum

class WindDirection(enum.Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"

class CountryWeather(Base):
    __tablename__ = "country_weather"

    id = Column(Integer, primary_key=True)
    country = Column(String(100))  # ✅ додано довжину
    last_updated = Column(Date)
    sunrise = Column(Time)
    wind = relationship("WindInfo", uselist=False, back_populates="weather")

class WindInfo(Base):
    __tablename__ = "wind_info"

    id = Column(Integer, primary_key=True)
    weather_id = Column(Integer, ForeignKey("country_weather.id"))
    wind_degree = Column(Integer)
    wind_kph = Column(Float)
    wind_direction = Column(Enum(WindDirection, native_enum=False))  # ✅ краще для MySQL
    go_outside = Column(Boolean)

    weather = relationship("CountryWeather", back_populates="wind")
