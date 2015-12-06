# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import asyncio
import functools
import socket

from .connection import (
    Address,
)
from .connector import (
    BaseProtocol,
    BaseConnector,
)

__all__ = (
    'Connector',
    'Protocol',
)


class Protocol(asyncio.DatagramProtocol, BaseProtocol):
    """UDP protocol implementation."""

    def __init__(self, *, loop=None):
        super().__init__(loop=loop)
        self._buffer = asyncio.Queue()

    def datagram_received(self, data, addr):
        """Called when some datagram is received."""
        self._buffer.put_nowait((data, Address(*addr)))

    async def recv(self):
        """Receives datagram from remote Peer.

        :returns: Pair of received data and remote peer address
        :rtype: tuple

        This method is :term:`awaitable`.
        """
        return await self._buffer.get()

    async def send(self, data, remote_address=None):
        """Sends datagram to remote peer.

        :param bytes data: Data to send
        :param aioppspp.connection.Address remote_address: Recipient address

        This method is :term:`awaitable`.
        """
        self._transport.sendto(data, remote_address)


class Connector(BaseConnector):
    """UDP connector."""

    #: UDP protocol implementation
    protocol_class = Protocol

    def protocol_factory(self) -> functools.partial:
        """Produces factory for protocol implementation."""
        return functools.partial(self.protocol_class, loop=self._loop)

    async def create_endpoint(self, local_address=None, remote_address=None, *,
                              family=socket.AF_INET):
        """Creates datagram endpoint.

        :param aioppspp.connection.Address local_address: Local peer address
        :param aioppspp.connection.Address remote_address: Remote peer address
        :param socket.AddressFamily family: Socket address family

        This method is :term:`awaitable`.
        """
        _, protocol = await self._loop.create_datagram_endpoint(
            self.protocol_factory(),
            family=family,
            local_addr=local_address,
            remote_addr=remote_address)
        return protocol
