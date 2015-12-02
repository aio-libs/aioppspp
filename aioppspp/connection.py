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
import ipaddress
import sys
import traceback
import warnings
from collections import namedtuple

__all__ = (
    'Address',
    'Connection',
)


class Address(namedtuple('Address', ('ip', 'port'))):
    """Represents Peer address information as IP address (:class:`str`)
    and port (:class:`int`) as :class:`tuple`.
    """
    __slots__ = ()

    def __new__(cls, ip, port):
        ip = ipaddress.ip_address(ip)
        if not isinstance(port, int):
            raise TypeError('port must be an integer')
        if not (0 <= port <= 2 ** 16 - 1):
            raise ValueError('port must be in range [0, 65535]')
        return super().__new__(cls, str(ip), port)

    def __str__(self):
        return '{}:{}'.format(self.ip, self.port)


class Connection(object):
    """Connection object is an interface to the underlying protocol
    implementation.

    You should use :class:`aioppspp.connector.BaseConnector` instance to create
    connections instead of doing that directly.
    """

    _source_traceback = None
    _protocol = None

    def __init__(self, connector, key, protocol, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        if loop.get_debug():  # pragma: no cover
            self._source_traceback = traceback.extract_stack(sys._getframe(1))

        self._connector = connector
        self._key = key
        self._loop = loop
        self._protocol = protocol

    def __del__(self):
        if self.closed:
            return

        if self._loop.is_closed():
            return

        self._connector.close_connection(self)

        warnings.warn('Unclosed connection {!r}'.format(self), ResourceWarning)
        context = {'connection': self,
                   'message': 'Unclosed connection'}

        if self._source_traceback is not None:  # pragma: no cover
            context['source_traceback'] = self._source_traceback

        self._loop.call_exception_handler(context)

    def __repr__(self):
        idx = id(self)
        closed_tag = ' [closed]' if self.closed else ''
        local_addr, remote_addr = self.local_address, self.remote_address
        return '<{}@{:x}: {} -> {}{}>'.format(
            self.__class__.__name__, idx, local_addr, remote_addr, closed_tag)

    @property
    def key(self):
        return self._key

    @property
    def closed(self):
        """Returns :const:`True` when connection is closed."""
        return self._protocol is None or self._protocol.closed

    @property
    def local_address(self):
        """Returns local address information."""
        return self._protocol.local_address

    @property
    def remote_address(self):
        """Returns remote peer address information.
        May return :const:`None` in case if connection is not bound with
        any remote peer (for instance, it in listening mode).
        """
        return self._protocol.remote_address

    @property
    def protocol(self):
        """Returns the underlying protocol instance."""
        return self._protocol

    @property
    def loop(self):
        return self._loop

    def close(self):
        """Closes connection."""
        if self.closed:
            return
        self._connector.close_connection(self)
        self._protocol = None

    def release(self):
        """Releases connection and returns it back to the pool."""
        if self.closed:
            return
        self._connector.release_connection(self)
        self._protocol = None

    async def recv(self):
        """Receives an incoming data from remote peer.
        Returned value is depended on the underlying protocol implementation.

        This method is :term:`awaitable`.
        """
        if self.closed:
            raise ConnectionError('not connected')
        return await self._protocol.recv()

    async def send(self, data, remote_address=None):
        """Sends data to connected peer.

        Data type is depended on the underlying protocol implementation.
        If connection is not strictly bound with some specific remote peer,
        the remote address must be provided in order to know where to send
        the data.

        This method is :term:`awaitable`.
        """
        if self.closed:
            raise ConnectionError('not connected')
        return await self._protocol.send(data, remote_address)
