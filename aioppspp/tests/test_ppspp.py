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

import aioppspp.channel_ids
import aioppspp.connection
import aioppspp.datagrams
import aioppspp.ppspp
import aioppspp.tests.utils


class PPSPPTestCase(aioppspp.tests.utils.TestCase):

    def new_connector(self):
        return aioppspp.ppspp.Connector(loop=self.loop)

    async def test_keepalive_exchange(self):
        connector = self.new_connector()
        peer1_address = aioppspp.connection.Address('127.0.0.1', 0)
        peer1 = await connector.listen(peer1_address)
        peer2 = await connector.connect(peer1.local_address)

        channel_id1 = aioppspp.channel_ids.new()
        channel_id2 = aioppspp.channel_ids.new()

        datagram1 = aioppspp.datagrams.Datagram(channel_id1, [])
        datagram2 = aioppspp.datagrams.Datagram(channel_id2, [])

        await peer2.send(datagram2)

        datagram, address = await peer1.recv()
        self.assertEqual(datagram.channel_id, channel_id2)

        await peer1.send(datagram1, address)

        datagram, address = await peer2.recv()
        self.assertEqual(datagram.channel_id, channel_id1)

        peer1.close()
        peer2.close()
        connector.close()
