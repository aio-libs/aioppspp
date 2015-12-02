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

import ipaddress
import unittest

import hypothesis
import hypothesis.strategies as st

import aioppspp.connection


def ipaddr():
    return ipv4() | ipv6()


def ipv4():
    return st.builds(
        ipaddress.IPv4Address,
        st.integers(min_value=0, max_value=(2 ** ipaddress.IPV4LENGTH) - 1)
    ).map(str)


def ipv6():
    return st.builds(
        ipaddress.IPv6Address,
        st.integers(min_value=0, max_value=(2 ** ipaddress.IPV6LENGTH) - 1)
    ).map(str)


def port():
    return st.integers(0, 2 ** 16 - 1)


class AddressTestCase(unittest.TestCase):
    @hypothesis.given(ipaddr(), port())
    def test_address(self, ipaddr, port):
        addr = aioppspp.connection.Address(ipaddr, port)
        self.assertEqual(addr.ip, ipaddr)
        self.assertEqual(addr.port, port)

    def test_bad_ip(self):
        with self.assertRaises(ValueError):
            aioppspp.connection.Address('bad', 42)

    def test_bad_port_type(self):
        with self.assertRaises(TypeError):
            aioppspp.connection.Address('0.0.0.0', '42')

    def test_bad_port_value(self):
        with self.assertRaises(ValueError):
            aioppspp.connection.Address('0.0.0.0', -1)
