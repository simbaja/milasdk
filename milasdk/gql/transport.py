import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional, Union, NoReturn

import aiohttp
from aiohttp.client_exceptions import ClientResponseError
from graphql import DocumentNode, ExecutionResult, print_ast
from multidict import CIMultiDictProxy

from gql.transport import AsyncTransport

from .compat import GQL_V4

if GQL_V4:  # gql >= 4 passes a GraphQLRequest to the transport
    from gql import GraphQLRequest
else:  # gql 3.x passes the document and variables separately
    GraphQLRequest = None
from gql.transport.exceptions import (
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)

from ..auth import AbstractAsyncSession

log = logging.getLogger(__name__)

class AuthenticatedAIOHTTPTransport(AsyncTransport):
    """:ref:`Async Transport <async_transports>` to execute GraphQL queries
    on remote servers with an authenticated HTTP connection.

    This transport use the aiohttp library with asyncio.
    """

    def __init__(
        self,
        url: str,
        session: Optional[AbstractAsyncSession] = None
    ) -> None:
        """Initialize the transport with the given aiohttp parameters.

        :param url: The GraphQL server URL. Example: 'https://server.com:PORT/path'.
        :param session: The authenticated session to utilize

        """
        self.url: str = url
        self.session: AbstractAsyncSession | None = session
        self.response_headers: CIMultiDictProxy[str] | None

    async def connect(self) -> None:
        """Coroutine which will create an aiohttp ClientSession() as self.session.

        Don't call this coroutine directly on the transport, instead use
        :code:`async with` on the client and this coroutine will be executed
        to create the session.

        Should be cleaned with a call to the close coroutine.
        """
        # session management not performed by this transport

    async def close(self) -> None:
        """Coroutine which will close the aiohttp session.

        Don't call this coroutine directly on the transport, instead use
        :code:`async with` on the client and this coroutine will be executed
        when you exit the async context manager.
        """
        # session management not performed by this transport

    async def execute(
        self,
        request: Union["GraphQLRequest", DocumentNode],
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Optional[Dict[str, Any]] = None,
        upload_files: bool = False,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute the provided request against the configured remote server
        using the current authenticated session.

        Supports both gql 4 (a GraphQLRequest) and gql 3 (a DocumentNode plus
        variable_values / operation_name).

        Don't call this coroutine directly on the transport, instead use
        :code:`execute` on a client or a session.

        :param request: a GraphQLRequest (gql 4) or parsed DocumentNode (gql 3)
        :param variable_values: gql 3 only: an optional Dict of variable values
        :param operation_name: gql 3 only: an optional Operation name
        :param extra_args: additional arguments to send to the aiohttp post method
        :param upload_files: file uploads are not supported by the Mila API
        :returns: an ExecutionResult object.
        """

        if GraphQLRequest is not None and isinstance(request, GraphQLRequest):
            document = request.document
            variable_values = request.variable_values
            operation_name = request.operation_name
        else:
            document = request

        if upload_files:
            raise NotImplementedError("File uploads are not supported by this transport")

        query_str = print_ast(document)

        payload: Dict[str, Any] = {
            "query": query_str,
        }

        if operation_name:
            payload["operationName"] = operation_name

        if variable_values:
            payload["variables"] = variable_values

        if log.isEnabledFor(logging.DEBUG):
            log.debug(">>> %s", json.dumps(payload))

        post_args: Dict[str, Any] = {"json": payload}

        # Pass post_args to aiohttp post method
        if extra_args:
            post_args.update(extra_args)

        if self.session is None:
            raise TransportClosed("Transport is not connected")

        async with await self.session.post(self.url, **post_args) as resp:

            async def raise_response_error(resp: aiohttp.ClientResponse, reason: str) -> NoReturn:
                # We raise a TransportServerError if the status code is 400 or higher
                # We raise a TransportProtocolError in the other cases

                try:
                    # Raise a ClientResponseError if response status is 400 or higher
                    resp.raise_for_status()
                except ClientResponseError as e:
                    raise TransportServerError(str(e), e.status) from e

                result_text = await resp.text()
                raise TransportProtocolError(
                    f"Server did not return a GraphQL result: "
                    f"{reason}: "
                    f"{result_text}"
                )

            try:
                result = await resp.json(content_type=None)

                if log.isEnabledFor(logging.INFO):
                    result_text = await resp.text()
                    log.debug("<<< %s", result_text)

            except Exception:
                await raise_response_error(resp, "Not a JSON answer")

            if "errors" not in result and "data" not in result:
                await raise_response_error(resp, 'No "data" or "errors" keys in answer')

            # Saving latest response headers in the transport
            self.response_headers = resp.headers

            return ExecutionResult(
                errors=result.get("errors"),
                data=result.get("data"),
                extensions=result.get("extensions"),
            )

    def subscribe(
        self,
        request: Union["GraphQLRequest", DocumentNode],
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """Subscribe is not supported on HTTP.

        :meta private:
        """
        raise NotImplementedError(" The HTTP transport does not support subscriptions")