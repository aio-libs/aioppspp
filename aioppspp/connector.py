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

import abc
import asyncio
import sys
import traceback
import warnings
from collections import defaultdict
from itertools import chain

from .connection import (
    Address,
    Connection,
)

__all__ = (
    'BaseConnector',
    'BaseProtocol',
)


class BaseProtocol(asyncio.BaseProtocol, metaclass=abc.ABCMeta):
    """Base protocol interface.

    Should be used as mixin for regular asyncio Protocol classes.

    This is an :term:`abstract base class`.
    """

    def __init__(self, *, loop=None):
        self._loop = loop
        self._transport = None

    @property
    def closed(self):
        """Returns :const:`True` if connection is not made or closed."""
        return self._transport is None

    @property
    def local_address(self):
        """Returns local peer address or :const:`None` if not connected."""
        if self._transport is None:
            return None
        return Address(*self._transport._sock.getsockname()[:2])

    @property
    def remote_address(self):
        """Returns remote peer address or :const:`None` if not connected."""
        if self._transport is None:
            return None
        try:
            return Address(*self._transport._sock.getpeername()[:2])
        except OSError:
            # Transport is in "server" mode and not bounded with any specific
            # remote peer. No reason to crash then.
            return None

    @property
    def transport(self):
        """Returns the underlying transport instance."""
        return self._transport

    def connection_made(self, transport):
        """Called when a connection is made."""
        self._transport = transport

    def connection_lost(self, exc):
        """Called when the connection is lost or closed."""
        self._transport = None
        super().connection_lost(exc)

    @abc.abstractmethod
    async def recv(self):
        """Receives data from remote peer. Must be implemented in subclass.

        This method is :term:`awaitable`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, data, remote_address):
        """Sends data to remote peer. Must be implemented in subclass.

        This method is :term:`awaitable`.
        """
        raise NotImplementedError

    def close(self):
        """Closes protocol and the underlying transport."""
        self._transport.close()
        self._transport = None


class BaseConnector(object, metaclass=abc.ABCMeta):
    """Base connector.

    Connector is used as connections managers: it spawns them, controls them
    and kills them when time has come.

    This is an :term:`abstract base class`.
    """
    _closed = True
    _source_traceback = None
    connection_class = Connection

    def __init__(self, *, connection_class=None, connection_timeout=None,
                 loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        if loop.get_debug():  # pragma: no cover
            self._source_traceback = traceback.extract_stack(sys._getframe(1))

        if connection_class is not None:
            self.connection_class = connection_class

        self._acquired = defaultdict(set)
        self._closed = False
        self._loop = loop
        self._pool = {}
        self._connection_timeout = connection_timeout

    def __del__(self):
        if self.closed:
            return

        if not self._pool:
            return

        self.close()

        warnings.warn('Unclosed connector {!r}'.format(self), ResourceWarning)
        context = {'connector': self,
                   'message': 'Unclosed connector'}

        if self._source_traceback is not None:  # pragma: no cover
            context['source_traceback'] = self._source_traceback

        self._loop.call_exception_handler(context)

    @property
    def closed(self):
        """Returns :const:`True` whenever connector is closed."""
        return self._closed

    @property
    def loop(self):
        return self._loop

    @abc.abstractmethod
    async def create_endpoint(self, *args, **kwargs):
        """This method must be implemented in subclass in order to create
        an endpoint and return the BaseProtocol interface implementation.

        This method is :term:`awaitable`.
        """
        raise NotImplementedError

    async def connect(self, remote_address, **kwargs):
        """Creates a new outgoing connection to the specified remote peer.

        :param aioppspp.connection.Address remote_address: Remote peer address
        :returns: :class:`aioppspp.connection.Connection`

        This method is :term:`awaitable`.
        """
        return await self._connect(remote_address,
                                   remote_address=remote_address, **kwargs)

    async def listen(self, local_address, **kwargs):
        """Creates a new connection instance for incoming connections
        to the specified host and port pair.

        :param aioppspp.connection.Address local_address: Local peer address
        :returns: :class:`aioppspp.connection.Connection`

        This method is :term:`awaitable`.
        """
        return await self._connect(local_address,
                                   local_address=local_address, **kwargs)

    def close(self):
        """Closes connector and all served connections."""
        if self.closed:
            return

        try:
            if self._loop.is_closed():
                return

            for key, protocols in self._pool.items():
                for protocol in protocols:
                    protocol.close()

            # Copy acquired values to prevent iterator change error
            connections = map(list, self._acquired.values())
            for connection in chain.from_iterable(connections):
                connection.close()
        finally:
            self._pool.clear()
            self._acquired.clear()
            self._closed = True

    def close_connection(self, connection):
        """Closes the specified connection.

        :param aioppspp.connection.Connection connection: Connection to close
        """
        if self.closed:
            return

        key = connection.key
        acquired = self._acquired[key]

        try:
            acquired.remove(connection)
        except KeyError:  # pragma: no cover
            # this may be result of undetermined order of objects
            # finalization due garbage collection.
            pass
        finally:
            connection.protocol.close()

    def release_connection(self, connection):
        """Releases the connection and returns it back to the pool.

        :param aioppspp.connection.Connection connection: Connection to release
        """
        if self.closed:
            return

        key = connection.key
        acquired = self._acquired[key]

        try:
            acquired.remove(connection)
        except KeyError:  # pragma: no cover
            # this may be result of undetermined order of objects
            # finalization due garbage collection.
            pass
        finally:
            protocols = self._pool.get(key, None)
            if protocols is None:
                protocols = self._pool[key] = []
            protocols.append(connection.protocol)

    async def _connect(self, key, **connection_kwargs):
        try:
            connection = self._get_connection(key)
            if connection is None:
                connect_future = self.create_endpoint(**connection_kwargs)
                if self._connection_timeout:
                    connect_future = asyncio.wait_for(
                        connect_future,
                        self._connection_timeout,
                        loop=self._loop)

                protocol = await connect_future
                connection = self._spawn_connection(key, protocol)

        except asyncio.TimeoutError as exc:
            raise TimeoutError(
                'Connection timeout to host %s:%s' % key) from exc

        except OSError as exc:
            raise ConnectionError(
                'Cannot connect to host %s:%s' % key) from exc

        else:
            self._acquired[key].add(connection)
            return connection

    def _get_connection(self, key):
        protocols = self._pool.get(key)
        while protocols:
            protocol = protocols.pop()
            if not protocols:
                # The very last connection was reclaimed: drop the key
                del self._pool[key]
            return self._spawn_connection(key, protocol)
        assert key not in self._pool  # TODO: guard possible issue

    def _spawn_connection(self, key, protocol):
        return self.connection_class(self, key, protocol, loop=self._loop)
