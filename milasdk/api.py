""" Implements support for the MilaCares GraphQL API """

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from graphql import DocumentNode, ExecutionResult
from gql import Client
from gql.dsl import *
from gql.transport.exceptions import (
    TransportQueryError,
    TransportProtocolError,
    TransportServerError,
)

from milasdk import (
    API_DEFAULT_429_WAIT,
    API_BASE_URL,
    AbstractAsyncSession,
    MilaError
)
from milasdk.exceptions import OAuthError

from .gql import *

_LOGGER = logging.getLogger(__name__)

class MilaApi:
    """ A class that provides API calling functionality to the Mila API """

    def __init__(self, session: AbstractAsyncSession) -> None:
        self._session = session
        self._transport = AuthenticatedAIOHTTPTransport(API_BASE_URL, session)
        self._client = self._setup_client()

    def _setup_client(self) -> Client:
        with open(Path(__file__).parent / './gql/mila_schema.gql') as f:
            schema_str = f.read()

        c = Client(
            schema=schema_str,
            transport=self._transport, 
            serialize_variables=True, 
            parse_results=True
        )

        register_enums(c)
        register_scalers(c)

        return c

    async def _execute(self, document: DocumentNode, variable_values: Optional[Dict[str,Any]] = None) -> ExecutionResult:
        """ Main function to call the Mila API over HTTPS """
        retry = 3
        authError = 0
        response: ExecutionResult = None
        async with self._client as session:
            while retry:
                retry -= 1
                try:
                    return await session.execute(document, variable_values)
                except TransportServerError as ex:
                    if ex.code == 429:    # Too Many Requests
                        wait_time = response.headers.get('Retry-After', API_DEFAULT_429_WAIT)
                        _LOGGER.debug('HTTP Error 429 - Too Many Requests. Sleeping for %s seconds and will retry', wait_time)
                        await asyncio.sleep(int(wait_time)+1)
                    elif ex.code == 401 or ex.code >= 500: # Unauthorized or service error
                        if ex.code == 401:
                            authError += 1
                        # This is probably caused by an expired token so the next retry will get a new one automatically
                        _LOGGER.debug("API call returned error code=%d - %d retries left", ex.code, retry)
                    else:
                        raise MilaError("Transport server error occurred") from ex
                except TransportProtocolError as ex:
                    raise MilaError("Transport protocol error occurred") from ex
                except TransportQueryError as ex:
                    raise MilaError("Transport reported query error") from ex
                except GraphQLError as ex:
                    raise MilaError("Invalid query") from ex
                except OAuthError:
                    raise
                except Exception as ex:                
                    _LOGGER.debug("Unknown error occurred", exc_info=ex)
                    if not retry:
                        raise MilaError("API call failed") from ex

        # if we have multiple auth errors, assume we have an issue so we can
        # get a new token
        if authError > 1:
            raise OAuthError("Multiple auth errors, assuming auth token invalid")

        # all retries were exhausted without a valid response
        raise MilaError("Failed to get a valid response from Mila API service")

    async def get_account(self) -> Dict[str, Any]:
        """ Returns the account information (account, home, etc) """
        ds = DSLSchema(self._client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.Query.owner.select(
                    ds.Owner.profile.select(
                        ds.Profile.email,
                        ds.Profile.firstName,
                        ds.Profile.lastName
                    )
                )
            )
        )
        result = await self._execute(query)

        return result["owner"]["profile"]

    async def get_appliances(self) -> Dict[str, Any]:
        """ Returns the information for all appliances """
        ds = DSLSchema(self._client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.Query.owner.select(
                    ds.Owner.appliances.select(
                        *appliance_fields_fragment(ds)
                    )
                )
            )
        )
        result = await self._execute(query)
        return result["owner"]["appliances"]

    async def get_appliance(self, device_id: str) -> Dict[str, Any]:
        """ Returns information for the selected appliance """
        ds = DSLSchema(self._client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.Query.owner.select(
                    ds.Owner.appliance(applianceId=device_id).select(
                        *appliance_fields_fragment(ds)
                    )
                )
            )
        )
        result = await self._execute(query)
        return result["owner"]["appliance"]

    async def get_appliance_sensor(self, device_id: str, sensor_kind: ApplianceSensorKind) -> Dict[str, Any]:
        """ Returns information for the selected appliance """
        ds = DSLSchema(self._client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.Query.owner.select(
                    ds.Owner.appliance(applianceId=device_id).select(
                        ds.Appliance.sensor(kind=sensor_kind).select(
                            *appliance_sensor_fields_fragment(ds)
                        )
                    )
                )
            )
        )
        result = await self._execute(query)
        return result["owner"]["appliance"]["sensor"]

    async def get_location_data(self) -> Dict[str, Any]:
        """ Returns location details """
        ds = DSLSchema(self._client.schema)
        query = dsl_gql(DSLQuery(location_fragment(ds)))
        result = await self._execute(query)
        return result["owner"]["locations"]

    async def set_smart_mode(self, device_id: str, mode: SmartModeKind, is_enabled: bool) -> Dict[str, Any]:
        ds = DSLSchema(self._client.schema)
        name: DSLField = None
        if mode == SmartModeKind.Sleep:
            name = ds.Mutation.applySleepMode(applianceId=device_id,isEnabled=is_enabled,fanMode=FanMode.Lowest)
        elif mode == SmartModeKind.Turndown:
            name = ds.Mutation.applyTurndownMode(applianceId=device_id,isEnabled=is_enabled,fanMode=FanMode.Highest)
        elif mode == SmartModeKind.Whitenoise:
            name = ds.Mutation.applyWhitenoiseMode(applianceId=device_id,isEnabled=is_enabled,fanMode=FanMode.Medium)
        elif mode == SmartModeKind.Housekeeper:
            name = ds.Mutation.applyHousekeeperMode(applianceId=device_id,isEnabled=is_enabled)
        elif mode == SmartModeKind.Quiet:
            name = ds.Mutation.applyQuietMode(applianceId=device_id,isEnabled=is_enabled)
        elif mode == SmartModeKind.Quarantine:
            name = ds.Mutation.applyQuarantineMode(applianceId=device_id,isEnabled=is_enabled)
        elif mode == SmartModeKind.PowerSaver:
            name = ds.Mutation.applyPowerSaverMode(applianceId=device_id,isEnabled=is_enabled)
        elif mode == SmartModeKind.ChildLock:
            name = ds.Mutation.applyChildLockMode(applianceId=device_id,isEnabled=is_enabled)

        mutation = DSLMutation(name.select(*appliance_fields_fragment(ds)))
        result = await self._execute(dsl_gql(mutation))

        return list(result.values())[0]

    async def set_sound_mode(self, device_id: str, mode: SoundsConfig) -> Dict[str, Any]:
        ds = DSLSchema(self._client.schema)
        mutation = DSLMutation(
            ds.Mutation.applySoundsConfig(applianceId=device_id, soundsConfig=mode).select(
                *appliance_fields_fragment(ds)
            )
        )
        result = await self._execute(dsl_gql(mutation))

        return list(result.values())[0]

    async def set_automagic_mode(self, room_id: int) -> None:
        ds = DSLSchema(self._client.schema)
        mutation = DSLMutation(
            ds.Mutation.applyRoomAutomagicMode(roomId=room_id).select(
                ds.Room.id
            )
        )
        result = await self._execute(dsl_gql(mutation))

    async def set_manual_mode(self, room_id: int, fan_speed: int, target_aqi: int = 10) -> None:
        ds = DSLSchema(self._client.schema)
        mutation = DSLMutation(
            ds.Mutation.applyRoomManualMode(roomId=room_id,fanSpeed=fan_speed,targetAqi=target_aqi).select(
                ds.Room.id
            )
        )
        result = await self._execute(dsl_gql(mutation))

    async def force_room_data(self, room_id: int) -> None:
        ds = DSLSchema(self._client.schema)
        mutation = DSLMutation(
            ds.Mutation.forceRoomData(roomId=room_id).select(
                ds.Room.id
            )
        )
        result = await self._execute(dsl_gql(mutation))       