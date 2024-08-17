from enum import auto
from strenum import StrEnum

class ApplianceMode(StrEnum):
  Automagic = auto()
  Sleep = auto()
  Housekeeper = auto()
  DeepClean = auto()
  Quiet = auto()
  Turndown = auto()
  WhiteNoise = auto()
  Quarantine = auto()
  Manual = auto()
  Safeguard = auto()
  PowerSaver = auto()

class SmartModeKind(StrEnum):
  Housekeeper = auto()
  Quiet = auto()
  Quarantine = auto()
  Sleep = auto()
  Turndown = auto()
  Whitenoise = auto()
  PowerSaver = auto()  
  ChildLock = auto()  

class ApplianceSensorKind(StrEnum):
  Ach = auto()
  FanSpeed = auto()
  Ttc = auto()
  Aqi = auto()
  Pm1 = auto()
  Pm2_5 = auto()
  Pm10 = auto()
  Voc = auto()
  Humidity = auto()
  Temperature = auto()
  Co2 = auto()
  Co = auto()

class EnvironmentKind(StrEnum):
  Urban = auto()
  Suburban = auto()
  Rural = auto()

class FanMode(StrEnum):
  Lowest = auto()
  Low = auto()
  Medium = auto()
  High = auto()
  Highest = auto()

class FilterKind(StrEnum):
  MamaToBe = auto()
  BasicBreather = auto()
  BigSneeze = auto()
  HomeWrecker = auto()
  CritterCuddler = auto()
  Overreactor = auto()
  RookieParent = auto()

class HomeKind(StrEnum):
  House = auto()
  Apartment = auto()

class HouseAge(StrEnum):
  Old = auto()
  New = auto()

class HouseBedrooms(StrEnum):
  One = auto()
  Two = auto()
  Three = auto()
  Four = auto()
  FiveOrMore = auto()

class HouseSize(StrEnum):
  Large = auto()
  Medium = auto()
  Small = auto()

class OutdoorStationSensorKind(StrEnum):
  Pm2_5 = auto()

class RoomKind(StrEnum):
  LivingRoom = auto()
  Kitchen = auto()
  Laundry = auto()
  HomeOffice = auto()
  Entry = auto()
  TvRoom = auto()
  MainBedroom = auto()
  KidsBedroom = auto()
  GuestBedroom = auto()
  Studio = auto()

class SoundsConfig(StrEnum):
  Enabled = auto()
  DaytimeOnly = auto()
  Disabled = auto()

class AggregateFunction(StrEnum):
  Mean = auto()
  Max = auto()
  Min = auto()
  Last = auto()
