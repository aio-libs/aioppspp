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
import aioppspp.tests.utils

from .test_connector import Connector, Protocol


class TestConnection(aioppspp.tests.utils.TestCase):
    def new_connector(self):
        return Connector(connection_class=aioppspp.connection.Connection,
                         loop=self.loop)

    def new_connection(self):
        return aioppspp.connection.Connection(
            self.new_connector(),
            protocol=Protocol(loop=self.loop),
            key=aioppspp.connection.Address('0.0.0.0', 0),
            loop=self.loop)

    def test_loop(self):
        connection = self.new_connection()
        self.assertIs(connection.loop, self.loop)

    def test_default_loop(self):
        connection = aioppspp.connection.Connection(
            self.new_connector(),
            protocol=Protocol(loop=self.loop),
            key=aioppspp.connection.Address('0.0.0.0', 0))
        self.assertIs(connection.loop, self.loop)

    def test_del(self):
        connection = self.new_connection()
        connection.protocol.connection_made(unittest.mock.Mock())
        exc_handler = unittest.mock.Mock()
        self.loop.set_exception_handler(exc_handler)

        with self.assertWarns(ResourceWarning):
            del connection
            gc.collect()

        msg = {'connection': unittest.mock.ANY,
               'message': 'Unclosed connection'}
        exc_handler.assert_called_with(self.loop, msg)

    def test_del_with_closed_loop(self):
        connection = self.new_connection()
        connection.protocol.connection_made(unittest.mock.Mock())
        exc_handler = unittest.mock.Mock()
        self.loop.set_exception_handler(exc_handler)
        self.loop.close()

        with self.assertRaises(AssertionError):
            with self.assertWarns(ResourceWarning):
                del connection
                gc.collect()

        self.assertFalse(exc_handler.called)

    async def test_key(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        self.assertEqual(connection.key, address)

    def test_not_connected(self):
        connection = self.new_connection()
        self.assertTrue(connection.closed)

    def test_connected(self):
        connection = self.new_connection()
        connection.protocol.connection_made(unittest.mock.Mock())
        self.assertFalse(connection.closed)
        connection.close()

    def test_repr_closed(self):
        connection = self.new_connection()
        self.assertEqual(
            '<Connection@{:x}: None -> None [closed]>'.format(id(connection)),
            repr(connection))

    def test_repr_connected(self):
        connection = self.new_connection()
        transport = unittest.mock.Mock()
        transport._sock.getsockname.return_value = ('127.0.0.1', 4242)
        transport._sock.getpeername.return_value = ('10.5.0.45', 4242)
        connection.protocol.connection_made(transport)
        self.assertEqual('<Connection@{:x}: 127.0.0.1:4242 -> 10.5.0.45:4242>'
                         ''.format(id(connection)),
                         repr(connection))
        connection.close()

    async def test_close(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        connector.close_connection = unittest.mock.Mock(
            wraps=connector.close_connection)
        protocol_close = connection.protocol.close = unittest.mock.Mock(
            wraps=connection.protocol.close)
        connection.close()
        self.assertTrue(connector.close_connection.called)
        self.assertTrue(protocol_close.called)
        self.assertIsNone(connection.protocol)
        self.assertTrue(connection.closed)

    async def test_close_closed(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        connection.close()
        connector.close_connection = unittest.mock.Mock()
        connection.close()
        self.assertFalse(connector.close_connection.called)

    async def test_release(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        connector.release_connection = unittest.mock.Mock()
        connection.release()
        self.assertTrue(connector.release_connection.called)
        self.assertIsNone(connection.protocol)
        self.assertTrue(connection.closed)

    async def test_release_closed(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        connection.release()
        connector.release_connection = unittest.mock.Mock()
        connection.release()
        self.assertFalse(connector.release_connection.called)
        connector.close()

    async def test_recv_not_connected(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        with self.assertRaises(ConnectionError):
            await connection.recv()

    async def test_recv(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        connection.protocol.recv = unittest.mock.Mock(
            wraps=connection.protocol.recv)
        await connection.recv()
        self.assertTrue(connection.protocol.recv.called)
        connection.close()

    async def test_send_not_connected(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        with self.assertRaises(ConnectionError):
            await connection.send(b'...')

    async def test_send(self):
        connector = self.new_connector()
        address = aioppspp.connection.Address('0.0.0.0', 0)
        connection = await connector.connect(address)
        connection.protocol.connection_made(unittest.mock.Mock())
        connection.protocol.send = unittest.mock.Mock(
            wraps=connection.protocol.send)
        await connection.send(b'...', None)
        self.assertTrue(connection.protocol.send.called)
        connection.close()
