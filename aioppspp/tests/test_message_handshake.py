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
import aioppspp.messages
import aioppspp.messages.handshake
import aioppspp.messages.protocol_options as protocol_options
from . import strategies as st


class HandshakeTestCase(unittest.TestCase):

    def test_decode_empty(self):
        with self.assertRaises(ValueError):
            aioppspp.messages.handshake.decode(memoryview(b''))

    @hypothesis.given(st.handshake())
    def test_decode_encode(self, message):
        data = aioppspp.messages.handshake.encode(message)
        self.assertIsInstance(data, bytearray)
        result, _ = aioppspp.messages.handshake.decode(memoryview(data))
        self.assertIsInstance(result, aioppspp.messages.Handshake)
        self.assertEqual(message, result)

    def test_init_with_bad_type(self):
        with self.assertRaises(ValueError):
            msgtype = 42
            aioppspp.messages.Handshake(msgtype, ..., ...)
        with self.assertRaises(ValueError):
            msgtype = aioppspp.messages.MessageType(2)
            aioppspp.messages.Handshake(msgtype, ..., ...)

    def test_init_cast_arguments(self):
        message = aioppspp.messages.Handshake(0, b'1234', {})
        self.assertIsInstance(message.type, aioppspp.messages.MessageType)
        self.assertIsInstance(message.source_channel_id,
                              aioppspp.channel_ids.ChannelID)
        self.assertIsInstance(message.protocol_options,
                              protocol_options.ProtocolOptions)
