"""Support for Milacares authentication."""

from __future__ import annotations
import logging
from types import TracebackType
from typing import Callable, Optional, Type

from oauthlib.oauth2 import LegacyApplicationClient
from async_oauthlib import OAuth2Session
from milasdk.const import AUTH_CLIENT_ID, AUTH_OIDC_TOKEN_ENDPOINT, AUTH_SCOPES
from milasdk.exceptions import OAuthError

LOG = logging.getLogger(__name__)

class MilaOauth2:
    """
    Handle authentication with Oidc.  Mila appears to use the legacy flow for its application
    authentication, so we'll implement that instead of the usual flows that don't handle passwords
    directly.
    """

    def __init__(
        self,
        token: dict[str, str] | None = None,
        token_updater: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize self.
        Keyword Arguments:
            token {Optional[Dict[str, str]]} -- Authorization token (default: {None})
            token_updater {Optional[Callable[[str], None]]} -- Callback when the token is updated (default: {None})
            scope {Optional[str]} -- List of scopes (default: "email profile")
        """
        self.client_id = AUTH_CLIENT_ID
        self.scope = AUTH_SCOPES
        self.token_updater = token_updater

        self.extra = {"client_id": self.client_id}

        self._oauth = OAuth2Session(
            client = LegacyApplicationClient(self.client_id),
            token=token,
            token_updater=self.token_updater,
            scope=self.scope
        )

    async def async_refresh_token(self) -> dict[str, str | int]:
        """Refresh and return new token."""
        try:
            token = await self._oauth.refresh_token(AUTH_OIDC_TOKEN_ENDPOINT, **self.extra)

            if self.token_updater is not None:
                self.token_updater(token)

            return token
        except Exception as ex:
            raise OAuthError(f"Refresh token failure: {ex}") from ex        

    async def async_request_token(
        self,
        username: str | None = None,
        password: str | None = None,
    ) -> dict[str, str | int]:
        """
        Generic method for fetching a Mila access token.
        :param username: Your Milacares username
        :param password: Your Milacares password
        :return: A token dict
        """
        try:
            return await self._oauth.fetch_token(
                AUTH_OIDC_TOKEN_ENDPOINT,
                username=username,
                password=password,
                include_client_id=True,
            )
        except Exception as ex:
            raise OAuthError(f"Request token failure: {ex}") from ex

    @property
    def closed(self):
        return self._oauth.closed

    async def close(self):
        if not self._oauth.closed:
            await self._oauth.close()

    async def __aenter__(self) -> "MilaOauth2":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()