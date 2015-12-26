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

from collections import (
    namedtuple,
)
from itertools import (
    chain,
)

from . import protocol_options
from .. import channel_ids
from .protocol_options import (
    ProtocolOptions,
)
from .types import (
    MessageType,
)

__all__ = (
    'Handshake',
    'decode',
    'encode',
    'new',
)


class Handshake(namedtuple('Handshake', (
    'type',
    'source_channel_id',
    'protocol_options'
))):
    """To establish communication, peers must first exchange HANDSHAKE messages
    by means of a handshake procedure. These messages contains all important
    metadata about the Swarm, transfer options and integrity checks.

    The payload of the HANDSHAKE message contains a sequence of protocol
    options. See :class:`aioppspp.messages.protocol_options.ProtocolOptions`
    for more info.

    .. seealso::

        - :rfc:`7574#section-3.1`
        - :rfc:`7574#section-8.4`
    """
    __slots__ = ()

    def __new__(cls, type, source_channel_id, protocol_options):
        if not isinstance(type, MessageType):
            type = MessageType(type)
        if type is not MessageType.HANDSHAKE:
            raise ValueError('bad message type {}'.format(type))
        if not isinstance(source_channel_id, channel_ids.ChannelID):
            source_channel_id = channel_ids.ChannelID(source_channel_id)
        if not isinstance(protocol_options, ProtocolOptions):
            protocol_options = ProtocolOptions(**protocol_options)
        return super().__new__(cls, type, source_channel_id, protocol_options)


def decode(data):
    """Decodes HANDSHAKE message from bytes.

    :param memoryview data: Binary data
    :returns: Tuple of :class:`Handshake` message and the rest of the data
    :rtype: tuple
    """
    # 8.4.  HANDSHAKE
    #
    # 0                   1                   2                   3
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 0 0 0|            Source Channel ID (32)             |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |               |                                               ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |                                                               |
    # ~                     Protocol Options                          ~
    # |                                                               |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    channel_id, rest = channel_ids.decode(data)
    options, rest = protocol_options.decode(rest)
    handshake = Handshake(MessageType.HANDSHAKE, channel_id, options)
    return handshake, rest


def encode(message):
    """Encodes HANDSHAKE message to bytes.

    :param Handshake message: Handshake message instance
    :rtype: bytearray
    """
    return bytearray(chain.from_iterable([
        channel_ids.encode(message.source_channel_id),
        protocol_options.encode(message.protocol_options)
    ]))


def new(source_channel_id, protocol_options):
    """Creates new Handshake message.

    :param aioppspp.channel_ids.ChannelID source_channel_id: Source channel ID
    :param aioppspp.messages.protocol_options.ProtocolOptions protocol_options:
        Protocol options
    :rtype: :class:`Handshake`
    """
    return Handshake(MessageType.HANDSHAKE,
                     source_channel_id, protocol_options)
