from gql.dsl import *
from .enums import ApplianceSensorKind

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
            ds.ApplianceFilter.daysLeft,
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

def outdoor_sensor_fields_fragment(ds: DSLSchema):
    return (
        ds.OutdoorStationSensor.kind,
        ds.OutdoorStationSensor.latest(precision={ "unit": "Day", "value": "1" }).select(
            ds.InstantValue.instant,
            ds.InstantValue.value
        )
    )