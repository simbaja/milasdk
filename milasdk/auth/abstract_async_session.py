"""Support for MilaCares authentication, generic interface."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any
from aiohttp import ClientError, ClientResponse, ClientSession

from ..const import AUTH_HEADER
from ..exceptions import MilaError

_LOGGER = logging.getLogger(__name__)

class AbstractAsyncSession(ABC):
    """Abstract class to make authenticated async requests."""

    def __init__(self, session: ClientSession) -> None:
        """Initialize the auth."""
        self._session = session

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def post(
        self,
        url: str,
        data: Any = None,
        **kwargs
    ) -> ClientResponse:
        """Wrapper for authenticated post requests."""
        try:
            access_token = await self.async_get_access_token()
        except ClientError as err:
            raise MilaError(f"Access token failure: {err}") from err
        headers = {AUTH_HEADER: f"Bearer {access_token}"}

        resp : ClientResponse = None

        return await self._session.post(
            url,
            headers=headers,
            **kwargs
        )