from gql import Client
from gql.utilities import update_schema_enum, update_schema_scalar

from .enums import *
from .queries import *
from .scalars import *
from .transport import AuthenticatedAIOHTTPTransport

_LOGGER = logging.getLogger(__name__)

def register_enums(client: Client):
    if not client.schema:
        _LOGGER.warning("Client schema is None; skipping enum registration.")
        return

    update_schema_enum(client.schema, "ApplianceMode", ApplianceMode)
    update_schema_enum(client.schema, "ApplianceSensorKind", ApplianceSensorKind)
    update_schema_enum(client.schema, "EnvironmentKind", EnvironmentKind)
    update_schema_enum(client.schema, "FanMode", FanMode)
    update_schema_enum(client.schema, "FilterKind", FilterKind)
    update_schema_enum(client.schema, "HomeKind", HomeKind)
    update_schema_enum(client.schema, "HouseAge", HouseAge)
    update_schema_enum(client.schema, "HouseBedrooms", HouseBedrooms)
    update_schema_enum(client.schema, "OutdoorStationSensorKind", OutdoorStationSensorKind)
    #update_schema_enum(client.schema, "PollenIndex", PollenIndex) #can't use this one because "None" is a key
    update_schema_enum(client.schema, "RoomKind", RoomKind)
    update_schema_enum(client.schema, "SoundsConfig", SoundsConfig)

def register_scalers(client: Client):
    if not client.schema:
        _LOGGER.warning("Client schema is None; skipping scalar registration.")
        return

    update_schema_scalar(client.schema, "Date", DateScalar)
    update_schema_scalar(client.schema, "EpochSecond", EpochSecondScalar)
