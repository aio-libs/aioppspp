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

from hypothesis.strategies import (
    binary,
    booleans,
    builds,
    composite,
    integers,
    just,
    none,
    sampled_from,
    tuples,
)

import aioppspp.channel_ids
import aioppspp.messages
import aioppspp.messages.protocol_options as protocol_options
from aioppspp.constants import (
    BYTE,
    WORD,
    DWORD,
)
from aioppspp.messages import (
    MessageType,
)


def maybe(strategy):
    return strategy | none()


def byte():
    return binary(min_size=BYTE, max_size=BYTE)


def word():
    return binary(min_size=WORD, max_size=WORD)


def dword():
    return binary(min_size=DWORD, max_size=DWORD)


def sampled_from_enum(enum):
    return sampled_from([item.value for item in enum])


def channel_id():
    return builds(aioppspp.channel_ids.ChannelID, dword())


def handshake():
    return builds(aioppspp.messages.handshake.new,
                  channel_id(),
                  generic_protocol_options())


@composite
def generic_protocol_options(draw):
    cam = draw(maybe(option_cam()))
    args = map(draw, (
        option_version(),
        option_minimum_version(),
        option_swarm_id(),
        option_cipm(),
        option_mhtf(),
        option_lsa(),
        just(cam),
        none() if cam is None else option_ldw(cam),
        option_supported_messages(),
        option_chunk_size(),
    ))
    return protocol_options.ProtocolOptions(*args)


def option_version():
    return sampled_from_enum(protocol_options.Version)


def option_minimum_version():
    return sampled_from_enum(protocol_options.Version)


def option_swarm_id():
    return word()


@composite
def raw_swarm_id(draw):
    length = draw(integers(min_value=1, max_value=2 ** 8 * WORD))
    swarm_id = draw(binary(min_size=length, max_size=length))
    return length.to_bytes(WORD, 'big') + swarm_id


def option_cipm():
    return sampled_from_enum(protocol_options.CIPM)


def option_mhtf():
    return sampled_from_enum(protocol_options.MHTF)


def option_lsa():
    return sampled_from_enum(protocol_options.LSA)


def option_cam():
    return sampled_from_enum(protocol_options.CAM)


@composite
def raw_option_ldw(draw):
    value = draw(sampled_from_enum(protocol_options.CAM))
    method = protocol_options.CAM(value)
    window_size = protocol_options.LiveDiscardWindowSize[method.name].value
    ldw = draw(binary(min_size=window_size, max_size=window_size))
    return method, ldw


def option_ldw(cam):
    method = protocol_options.CAM(cam)
    window_size = protocol_options.LiveDiscardWindowSize[method.name].value
    return integers(min_value=window_size, max_value=window_size)


def option_supported_messages():
    return tuples(*[
        tuples(just(msgtype), booleans()) for msgtype in MessageType
    ]).filter(lambda i: i[1]).map(lambda i: {v for v, _ in i})


def option_chunk_size():
    return integers(min_value=1, max_value=2 ** 8 * DWORD)
