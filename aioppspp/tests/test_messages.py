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

import aioppspp.messages


class MessagesTestCase(unittest.TestCase):

    def test_decode_encode_empty(self):
        messages = aioppspp.messages.decode(memoryview(b''))
        self.assertEqual(messages, tuple())
        data = aioppspp.messages.encode(messages)
        self.assertEqual(data, b'')

    def test_unknown_message_type(self):
        class Message(aioppspp.messages.Message):
            @property
            def type(self):
                return 42

        with self.assertRaises(KeyError):
            aioppspp.messages.decode(memoryview(b'\xcc'))

        with self.assertRaises(KeyError):
            aioppspp.messages.encode([Message()])

    def test_dummy_message(self):
        class Message(aioppspp.messages.Message):
            @property
            def type(self):
                return 42

        data = Message().type.to_bytes(1, 'big')
        messages = aioppspp.messages.decode(
            memoryview(data),
            handlers={Message().type: lambda d: (Message(), d)})
        self.assertIsInstance(messages[0], Message)

        result = aioppspp.messages.encode(
            messages,
            handlers={Message().type: lambda m: b''})
        self.assertIsInstance(result, bytearray)
        self.assertEqual(result, data)
