import datetime
from gql.dsl import *

from .enums import ApplianceSensorKind, OutdoorStationSensorKind

def appliance_fields_fragment(ds: DSLSchema):
    return (
        ds.Appliance.id,
        ds.Appliance.name,
        ds.Appliance.room.select(
            ds.Room.id,
            ds.Room.kind,
            ds.Room.name,
            ds.Room.size,
            ds.Room.soundsConfig,
            ds.Room.bedtime.select(
                ds.Bedtime.localStart,
                ds.Bedtime.localEnd
            )
        ),
        ds.Appliance.state.select(
            ds.ApplianceState.firmware.select(
                ds.Firmware.version,
                ds.Firmware.hash 
            ),
            ds.ApplianceState.wifiRssi,
            ds.ApplianceState.rawMode,
            ds.ApplianceState.modes,
            ds.ApplianceState.actualMode
        ),
        ds.Appliance.smartModes.select(
            ds.SmartModes.quiet.select(ds.QuietMode.isEnabled),
            ds.SmartModes.housekeeper.select(ds.HousekeeperMode.isEnabled),
            ds.SmartModes.quarantine.select(ds.QuarantineMode.isEnabled),
            ds.SmartModes.sleep.select(ds.SleepMode.isEnabled),
            ds.SmartModes.turndown.select(ds.TurndownMode.isEnabled),
            ds.SmartModes.whitenoise.select(ds.WhitenoiseMode.isEnabled),
            ds.SmartModes.powerSaver.select(ds.PowerSaverMode.isEnabled),
            ds.SmartModes.childLock.select(ds.ChildLockMode.isEnabled)
        ),
        ds.Appliance.filter.select(
            ds.ApplianceFilter.kind,
            ds.ApplianceFilter.installedAt,
            ds.ApplianceFilter.calibratedAt
        ),
        ds.Appliance.sensors(kinds=[e.value for e in ApplianceSensorKind]).select(
            *appliance_sensor_fields_fragment(ds)
        )
    )

def appliance_sensor_fields_fragment(ds: DSLSchema):
    return (
        ds.ApplianceSensor.kind,
        ds.ApplianceSensor.latest(precision={ "unit": "Minute", "value": "1" }).select(
            ds.InstantValue.instant,
            ds.InstantValue.value
        )
    )

def location_fragment(ds: DSLSchema):

    #I'm taking a guess here - there appear to be gaps in the pollen data
    #so, we can't just take today's value.  I'm taking the last value
    #for a given week, hopefully it works as expected
    now = datetime.datetime.utcnow()
    window = {
        "range": {
            "start": now - datetime.timedelta(days=6),
            "stop": now
        },
        "every": {
            "value": 7,
            "unit": "Day"
        },
        "fn": "Last"
    }

    return ds.Query.owner.select(
        ds.Owner.locations.select(
            ds.Location.id,
            ds.Location.address.select(
                ds.LocationAddress.city,
                ds.LocationAddress.country,
                ds.LocationAddress.point.select(
                    ds.LatLng.lat,
                    ds.LatLng.lon
                )
            ),
            ds.Location.environmentKind,
            ds.Location.homeKind,
            ds.Location.houseSize,
            ds.Location.houseAge,
            ds.Location.houseBedrooms,                        
            ds.Location.outdoorStation.select(
                ds.OutdoorStation.id,
                ds.OutdoorStation.name,
                ds.OutdoorStation.point.select(
                    ds.LatLng.lat,
                    ds.LatLng.lon
                ),
                ds.OutdoorStation.sensor(kind=OutdoorStationSensorKind.Pm2_5).select(
                    *outdoor_sensor_fields_fragment(ds)
                )
            ),
            ds.Location.pollenStation.select(
                ds.PollenStation.name,
                ds.PollenStation.aggregateWindow(input=window).select(
                    ds.DailyPollenStatus.date,
                    ds.DailyPollenStatus.status.select(
                        ds.PollenStatus.trees,
                        ds.PollenStatus.weeds,
                        ds.PollenStatus.grass,
                        ds.PollenStatus.mold
                    )
                )
            ),
            ds.Location.timezone
        )
    )

def outdoor_sensor_fields_fragment(ds: DSLSchema):
    return (
        ds.OutdoorStationSensor.kind,
        ds.OutdoorStationSensor.latest(precision={ "unit": "Day", "value": "1" }).select(
            ds.InstantValue.instant,
            ds.InstantValue.value
        )
    )
