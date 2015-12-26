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

import aioppspp.messages.protocol_options as protocol_options
from aioppspp.messages import (
    MessageType,
)
from . import strategies as st


class ProtocolOptionsTestCase(unittest.TestCase):

    @hypothesis.given(st.byte())
    @hypothesis.example(b'\x01')
    def test_version(self, data):
        try:
            value, _ = protocol_options.decode_version(
                memoryview(data), 0, ...)
        except ValueError:
            with self.assertRaises(ValueError):
                protocol_options.Version(int.from_bytes(data, 'big'))
        else:
            self.assertIsInstance(value, protocol_options.Version)
            result = protocol_options.encode_version(value, ...)
            self.assertEqual(data, result)

    @hypothesis.given(st.byte())
    @hypothesis.example(b'\x01')
    def test_minimum_version(self, data):
        try:
            value, _ = protocol_options.decode_minimum_version(
                memoryview(data), 0, ...)
        except ValueError:
            with self.assertRaises(ValueError):
                protocol_options.Version(int.from_bytes(data, 'big'))
        else:
            self.assertIsInstance(value, protocol_options.Version)
            result = protocol_options.encode_minimum_version(value, ...)
            self.assertEqual(data, result)

    @hypothesis.given(st.raw_swarm_id())
    def test_swarm_identifier(self, data):
        value, _ = protocol_options.decode_swarm_id(
            memoryview(data), 0, ...)
        self.assertIsInstance(value, bytes)
        result = protocol_options.encode_swarm_id(value, ...)
        self.assertEqual(data, result)

    def test_malformed_swarm_identifier(self):
        with self.assertRaises(ValueError):
            protocol_options.decode_swarm_id(
                memoryview(b'\x00\x10\x00'), 0, ...)

    @hypothesis.given(st.byte())
    def test_content_integrity_protection_method(self, data):
        decode = protocol_options.decode_content_integrity_protection_method
        encode = protocol_options.encode_content_integrity_protection_method
        try:
            value, _ = decode(memoryview(data), 0, ...)
        except ValueError:
            with self.assertRaises(ValueError):
                protocol_options.CIPM(int.from_bytes(data, 'big'))
        else:
            self.assertIsInstance(value, protocol_options.CIPM)
            result = encode(value, ...)
            self.assertEqual(data, result)

    @hypothesis.given(st.byte())
    def test_merkle_hash_tree_function(self, data):
        try:
            value, _ = protocol_options.decode_merkle_hash_tree_function(
                memoryview(data), 0, ...)
        except ValueError:
            with self.assertRaises(ValueError):
                protocol_options.MHTF(int.from_bytes(data, 'big'))
        else:
            self.assertIsInstance(value, protocol_options.MHTF)
            result = protocol_options.encode_merkle_hash_tree_function(
                value, ...)
            self.assertEqual(data, result)

    @hypothesis.given(st.byte())
    def test_live_signature_algorithm(self, data):
        try:
            value, _ = protocol_options.decode_live_signature_algorithm(
                memoryview(data), 0, ...)
        except ValueError:
            with self.assertRaises(ValueError):
                protocol_options.LSA(int.from_bytes(data, 'big'))
        else:
            self.assertIsInstance(value, protocol_options.LSA)
            result = protocol_options.encode_live_signature_algorithm(
                value, ...)
            self.assertEqual(data, result)

    @hypothesis.given(st.byte())
    def test_chunk_addressing_method(self, data):
        try:
            value, _ = protocol_options.decode_chunk_addressing_method(
                memoryview(data), 0, ...)
        except ValueError:
            with self.assertRaises(ValueError):
                protocol_options.CAM(int.from_bytes(data, 'big'))
        else:
            self.assertIsInstance(value, protocol_options.CAM)
            result = protocol_options.encode_chunk_addressing_method(
                value, ...)
            self.assertEqual(data, result)

    @hypothesis.given(st.raw_option_ldw())
    def test_live_discard_window(self, cam_ldw):
        cam, data = cam_ldw
        options = {'chunk_addressing_method': cam}
        value, _ = protocol_options.decode_live_discard_window(
            memoryview(data), 0, options)
        self.assertIsInstance(value, int)
        result = protocol_options.encode_live_discard_window(
            value, protocol_options.ProtocolOptions(**options))
        self.assertEqual(data, result)

    def test_cannot_encode_ldw_without_cam(self):
        expected = b'\xff'
        options = protocol_options.ProtocolOptions(live_discard_window=42)
        result = protocol_options.encode(options)
        self.assertEqual(result, expected)

    @hypothesis.given(st.option_supported_messages())
    def test_supported_messages(self, messages):
        data = protocol_options.encode_supported_messages(messages, ...)
        self.assertIsInstance(data, bytes)
        result, _ = protocol_options.decode_supported_messages(
            memoryview(data), 0, ...)
        self.assertIsInstance(result, set)
        self.assertEqual(messages, result)

    def test_supported_messages_spec(self):
        # 7.10.  Supported Messages
        # An example of the first 16 bits of the compressed bitmap for a peer
        # supporting every message except ACKs and PEXs is 11011001 11110000.
        #
        data = b'\x02\xd9\xf0'
        offset = 0
        supported_messages, _ = protocol_options.decode_supported_messages(
            memoryview(data), offset, ...)
        self.assertIsInstance(supported_messages, set)
        not_supported = [MessageType.ACK, MessageType.PEX_REQ,
                         MessageType.PEX_REScert, MessageType.PEX_RESv4,
                         MessageType.PEX_RESv6]
        for msgtype in MessageType:
            if msgtype in not_supported:
                self.assertNotIn(msgtype, supported_messages)
            else:
                self.assertIn(msgtype, supported_messages)

        result = protocol_options.encode_supported_messages(
            supported_messages, ...)
        self.assertEqual(data, result)

    @hypothesis.given(st.dword())
    def test_chunk_size(self, data):
        value, _ = protocol_options.decode_chunk_size(
            memoryview(data), 0, ...)
        self.assertIsInstance(value, int)
        result = protocol_options.encode_chunk_size(value, ...)
        self.assertEqual(data, result)

    @hypothesis.given(st.generic_protocol_options())
    def test_encode_decode(self, options):
        data = protocol_options.encode(options)
        self.assertIsInstance(data, bytearray)
        result, _ = protocol_options.decode(memoryview(data))
        from pprint import pformat
        self.assertEqual(result, options, pformat(list(zip(result, options))))

    def test_encode_decode_empty(self):
        data = b'\xff'
        options, _ = protocol_options.decode(memoryview(data))
        self.assertIsInstance(options, protocol_options.ProtocolOptions)
        self.assertTrue(all(option is None for option in options))
        result = protocol_options.encode(options)
        self.assertEqual(result, data)

    def test_decode_duplicate_options(self):
        data = b'\x00\x01\x00\x01'
        with self.assertRaises(ValueError):
            protocol_options.decode(memoryview(data))

    def test_init_bad_type(self):
        with self.assertRaises(TypeError):
            protocol_options.ProtocolOptions(version='42')
