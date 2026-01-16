"""Support for MilaCares authentication, default session."""

from operator import truediv
import time
from types import TracebackType
from typing import Optional, Type, cast
from aiohttp import ClientSession

from .mila_oath2 import MilaOauth2
from .abstract_async_session import AbstractAsyncSession

CLOCK_SKEW = 5

class DefaultAsyncSession(AbstractAsyncSession):
    """Default class to make authenticated async requests."""

    def __init__(self, session: ClientSession, username: str, password: str, auth: Optional[MilaOauth2] = None, close_session: bool = True) -> None:
        """Initialize the auth."""
        super().__init__(session)
        self._auth = auth if auth else MilaOauth2()
        self._close_session = close_session
        self._token: dict | None = None
        self._username = username
        self._password = password

    @property
    def token(self) -> dict | None:
        """Return the token."""
        return self._token

    @property
    def valid_token(self) -> bool:
        """Return if token is still valid."""
        if self.token is None:
          return False

        return (
            cast(float, self.token["expires_at"])
            > time.time()
        )

    async def async_ensure_token_valid(self) -> None:
        """Ensure that the current token is valid."""
        if self.valid_token:
            return

        if self._token is None or float(self._token["refresh_expires_at"]) > time.time():
            self._token = {}
            new_token = await self._auth.async_request_token(self._username, self._password)
            new_token["expires_at"] = int(time.time() + float(new_token["expires_in"]) - CLOCK_SKEW)
            new_token["refresh_expires_at"] = int(time.time() + float(new_token["refresh_expires_in"]) - CLOCK_SKEW)
        else:
            new_token = await self._auth.async_refresh_token()       
            new_token["expires_at"] = int(time.time() + float(new_token["expires_in"]) - CLOCK_SKEW)

        self._token.update(new_token)

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        await self.async_ensure_token_valid()
        assert self.token is not None
        return self.token["access_token"]

    @property
    def closed(self):
        return self._auth.closed and (self._session.closed or not self._close_session)

    async def close(self):
        if not self._auth.closed:
            await self._auth.close()
        if not self._session.closed and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "DefaultAsyncSession":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()