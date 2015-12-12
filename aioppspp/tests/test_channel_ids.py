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

import hypothesis

import aioppspp.channel_ids
from . import strategies as st


class ChannelIDTestCase(unittest.TestCase):

    def test_decode(self):
        data = memoryview(b'12345678')
        channel_id, rest = aioppspp.channel_ids.decode(data)
        self.assertIsInstance(channel_id, aioppspp.channel_ids.ChannelID)
        self.assertEqual(channel_id, b'1234')
        self.assertEqual(rest.tobytes(), b'5678')

    def test_encode(self):
        channel_id = aioppspp.channel_ids.new()
        data = aioppspp.channel_ids.encode(channel_id)
        self.assertEqual(data, bytes(channel_id))

    def test_new(self):
        channel_id = aioppspp.channel_ids.new()
        self.assertIsInstance(channel_id, aioppspp.channel_ids.ChannelID)

    def test_bad_channel_id(self):
        with self.assertRaises(TypeError):
            aioppspp.channel_ids.ChannelID(42)
        with self.assertRaises(ValueError):
            aioppspp.channel_ids.ChannelID(b'')
        with self.assertRaises(ValueError):
            aioppspp.channel_ids.ChannelID(b'.....')
        with self.assertRaises(ValueError):
            aioppspp.channel_ids.ChannelID(b'...')

    def test_zero_channel_id(self):
        self.assertIsInstance(aioppspp.channel_ids.ZeroChannelID,
                              aioppspp.channel_ids.ChannelID)
        self.assertEqual(aioppspp.channel_ids.ZeroChannelID, b'\x00' * 4)

    @hypothesis.given(st.channel_id())
    def test_strategy(self, channel_id0):
        data = aioppspp.channel_ids.encode(channel_id0)
        channel_id1, _ = aioppspp.channel_ids.decode(memoryview(data))
        self.assertEqual(channel_id0, channel_id1)
