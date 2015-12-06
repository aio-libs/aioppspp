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

import aioppspp.connection
import aioppspp.tests.utils
import aioppspp.udp


class TestUDP(aioppspp.tests.utils.TestCase):

    def new_connector(self):
        return aioppspp.udp.Connector(loop=self.loop)

    async def test_ping_pong(self):
        connector = self.new_connector()
        server_address = aioppspp.connection.Address('127.0.0.1', 0)
        server = await connector.listen(server_address)
        client = await connector.connect(server.protocol.local_address)

        await client.send(b'ping', server.local_address)
        data, addr = await server.recv()
        self.assertEqual(data, b'ping')
        self.assertEqual(addr, client.local_address)

        await server.send(b'pong', addr)
        data, addr = await client.recv()
        self.assertEqual(data, b'pong')
        self.assertEqual(addr, server.local_address)

        server.close()
        client.close()
