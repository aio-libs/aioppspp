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

import gc
import unittest.mock

import aioppspp.connection
import aioppspp.connector
import aioppspp.tests.utils


class Protocol(aioppspp.connector.BaseProtocol):

    async def recv(self):
        pass

    async def send(self, data, remote_address):
        pass


class Connector(aioppspp.connector.BaseConnector):

    async def create_endpoint(self, *args, **kwargs):
        return Protocol(loop=self.loop)


class TestProtocol(aioppspp.tests.utils.TestCase):

    def new_protocol(self):
        return Protocol(loop=self.loop)

    def test_not_connected_by_default(self):
        protocol = self.new_protocol()
        self.assertTrue(protocol.closed)

    def test_connected_by_default(self):
        protocol = self.new_protocol()
        protocol.connection_made(unittest.mock.Mock())
        self.assertFalse(protocol.closed)

    def test_close(self):
        protocol = self.new_protocol()
        transport = unittest.mock.Mock()
        protocol.connection_made(transport)
        self.assertIs(transport, protocol.transport)
        protocol.close()
        self.assertTrue(protocol.closed)
        self.assertTrue(transport.close.called)

    def test_connection_lost(self):
        protocol = self.new_protocol()
        transport = unittest.mock.Mock()
        protocol.connection_made(transport)
        protocol.connection_lost(ConnectionError)
        self.assertTrue(protocol.closed)

    def test_local_address_not_connected(self):
        protocol = self.new_protocol()
        self.assertIsNone(protocol.local_address)

    def test_local_address(self):
        protocol = self.new_protocol()
        ipaddrport = ('127.0.0.1', 4242)
        transport = unittest.mock.Mock()
        transport._sock.getsockname.return_value = ipaddrport
        protocol.connection_made(transport)
        self.assertIsInstance(protocol.local_address,
                              aioppspp.connection.Address)
        self.assertEqual(protocol.local_address, ipaddrport)

    def test_remote_address_not_connected(self):
        protocol = self.new_protocol()
        self.assertIsNone(protocol.remote_address)

    def test_remote_address(self):
        protocol = self.new_protocol()
        ipaddrport = ('127.0.0.1', 4242)
        transport = unittest.mock.Mock()
        transport._sock.getpeername.return_value = ipaddrport
        protocol.connection_made(transport)
        self.assertIsInstance(protocol.remote_address,
                              aioppspp.connection.Address)
        self.assertEqual(protocol.remote_address, ipaddrport)

    def test_no_remote_address(self):
        protocol = self.new_protocol()
        transport = unittest.mock.Mock()
        transport._sock.getpeername.side_effect = OSError
        protocol.connection_made(transport)
        self.assertIsNone(protocol.remote_address)


class TestConnector(aioppspp.tests.utils.TestCase):
    def new_connector(self):
        return Connector(connection_class=aioppspp.connector.Connection,
                         connection_timeout=1,
                         loop=self.loop)

    def test_default_init(self):
        Connector()

    def test_del(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = unittest.mock.Mock()
        connector._pool[address] = [connection]
        connections = connector._pool

        exc_handler = unittest.mock.Mock()
        self.loop.set_exception_handler(exc_handler)

        with self.assertWarns(ResourceWarning):
            del connector
            gc.collect()

        self.assertFalse(connections)
        connection.close.assert_called_with()
        msg = {'connector': unittest.mock.ANY,
               'message': 'Unclosed connector'}
        if self.loop.get_debug():  # pragma: no cover
            msg['source_traceback'] = unittest.mock.ANY
        exc_handler.assert_called_with(self.loop, msg)

    def test_del_with_closed_loop(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = unittest.mock.Mock()
        connector._pool[address] = [connection]
        connections = connector._pool

        exc_handler = unittest.mock.Mock()
        self.loop.set_exception_handler(exc_handler)
        self.loop.close()

        with self.assertWarns(ResourceWarning):
            del connector
            gc.collect()

        self.assertFalse(connections)
        self.assertFalse(connection.close.called)
        self.assertTrue(exc_handler.called)

    def test_del_empty_connector(self):
        connector = self.new_connector()

        exc_handler = unittest.mock.Mock()
        self.loop.set_exception_handler(exc_handler)

        del connector

        self.assertFalse(exc_handler.called)

    async def test_create_connection(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        self.assertIsInstance(connection, connector.connection_class)

    def test_loop(self):
        connector = self.new_connector()
        self.assertIs(connector.loop, self.loop)

    def test_default_loop(self):
        connector = Connector()
        self.assertIs(connector.loop, self.loop)

    async def test_connect(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connector.create_endpoint = unittest.mock.Mock(
            wraps=connector.create_endpoint)
        await connector.connect(address)
        connector.create_endpoint.assert_called_with(remote_address=address)

    async def test_listen(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connector.create_endpoint = unittest.mock.Mock(
            wraps=connector.create_endpoint)
        await connector.listen(address)
        connector.create_endpoint.assert_called_with(local_address=address)

    def test_not_closed_by_default(self):
        connector = self.new_connector()
        self.assertFalse(connector.closed)

    def test_close(self):
        connector = self.new_connector()
        connector.close()
        self.assertTrue(connector.closed)

    def test_close_closed_connector(self):
        connector = self.new_connector()
        connector.close()
        connector.close()

    async def test_close_closes_active_connections(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connections = []
        for _ in range(3):
            connection = await connector.connect(address)
            connection.protocol.connection_made(unittest.mock.Mock())
            connections.append(connection)
        connector.close()
        for connection in connections:
            self.assertTrue(connection.closed)

    async def test_close_connection_when_closed(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connector.close()
        connector.close_connection(connection)

    async def test_release_reuse_connections(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection0 = await connector.connect(address)
        connection0.protocol.connection_made(unittest.mock.Mock())
        connection0.release()
        connection1 = await connector.connect(address)
        self.assertIsNot(connection0, connection1)
        connection1.protocol.connection_made(unittest.mock.Mock())
        connection1.close()

    async def test_release(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection0 = await connector.connect(address)
        connection1 = await connector.connect(address)
        connection0.protocol.connection_made(unittest.mock.Mock())
        connection1.protocol.connection_made(unittest.mock.Mock())
        connection0.release()
        connection1.release()
        await connector.connect(address)
        await connector.connect(address)
        connector.close()

    def test_release_connection_while_closed(self):
        connector = self.new_connector()
        connector.close()
        connector.release_connection(...)

    async def test_connect_timeout(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connector.create_endpoint = unittest.mock.Mock(
            return_value=self.future())
        with self.assertRaises(TimeoutError):
            await connector.connect(address)

    async def test_connection_error(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connector.create_endpoint = unittest.mock.Mock(
            return_value=self.future(exception=OSError('...')))
        with self.assertRaises(ConnectionError):
            await connector.connect(address)
