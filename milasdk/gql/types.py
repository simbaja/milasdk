from dataclasses import dataclass
from datetime import datetime
from typing import List
from .enums import *

@dataclass
class Account:
    email: str
    firstName: str
    lastName: str
    #assume 1 location (multiple locations can't be added currently)
    address: str
    city: str
    country: str
    lat: float
    lon: float
    timezone: str
    environment_kind: EnvironmentKind
    home_kind: HomeKind
    home_size: HouseSize
    home_age: HouseAge
    home_bedrooms: HouseBedrooms

@dataclass
class Room:
    kind: RoomKind
    name: str
    size: int
    bedtime_start: str
    bedtime_end: str
    soundsConfig: SoundsConfig

@dataclass
class ApplianceFilter:
    kind: FilterKind
    days_left: int
    installed_at: datetime
    calibrated_at: datetime

@dataclass
class ApplianceState:
  firmware_version: str
  firmware_hash: str
  wifi_rssi: int
  raw_mode: int
  modes: List[ApplianceMode]

  actual_mode: ApplianceMode # none = offline

@dataclass
class SmartModes:
  quiet: bool
  housekeeper: bool
  quarantine: bool
  sleep: bool
  turndown: bool
  whitenoise: bool
  powerSaver: bool
  childLock: bool

@dataclass
class ApplianceSensor:
    kind: ApplianceSensorKind
    measured_at: datetime
    value: float

@dataclass
class Appliance:
    id: str #mac
    room: Room
    name: str
    state: ApplianceState
    filter: ApplianceFilter
    smart_modes: SmartModes
    sensors: List[ApplianceSensor]

@dataclass
class OutdoorStation:
    id: str
    name: str
    lat: float
    lon: float
    measured_at: datetime
    value: float

@dataclass
class PollenStation:
    id: str
    name: str
    measured_at: datetime
    trees: str #PollenIndex, but has None, so doesn't map right
    weeds: str #PollenIndex, but has None, so doesn't map right
    grass: str #PollenIndex, but has None, so doesn't map right
    mold: str #PollenIndex, but has None, so doesn't map right
