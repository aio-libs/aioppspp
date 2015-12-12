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

import unittest

import aioppspp.channel_ids
import aioppspp.datagrams


class DatagramsTestCase(unittest.TestCase):

    def test_decode_encode_empty(self):
        data = bytes(aioppspp.channel_ids.new())

        datagram = aioppspp.datagrams.decode(memoryview(data))
        self.assertIsInstance(datagram, aioppspp.datagrams.Datagram)
        self.assertIsInstance(datagram.channel_id,
                              aioppspp.channel_ids.ChannelID)
        self.assertEqual(datagram.channel_id, data)
        self.assertEqual(datagram.messages, tuple())

        encoded_datagram = aioppspp.datagrams.encode(datagram)
        self.assertIsInstance(encoded_datagram, bytes)
        self.assertEqual(encoded_datagram, data)
