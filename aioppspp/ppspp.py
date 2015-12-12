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

from . import datagrams
from . import udp

__all__ = (
    'Connector',
    'Protocol',
)


class Protocol(udp.Protocol):
    """PPSPP application protocol implementation over UDP."""

    async def recv(self):
        """Receives a datagram from remote peer.

        :rtype: :class:`aioppspp.datagrams.Datagram`

        This method is :term:`awaitable`.
        """
        data, addr = await super().recv()
        return datagrams.decode(memoryview(data)), addr

    async def send(self, datagram, remote_address=None):
        """Sends a datagram to remote peer.

        :param aioppspp.datagrams.Datagram datagram: PPSPP datagram
        :param aioppspp.connection.Address remote_address: Remote peer address

        This method is :term:`awaitable`.
        """
        return await super().send(datagrams.encode(datagram), remote_address)


class Connector(udp.Connector):
    """PPSPP connector that implements application protocol."""

    protocol_class = Protocol
