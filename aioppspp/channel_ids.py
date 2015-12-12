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

import os

from .constants import (
    DWORD,
)

__all__ = (
    'ChannelID',
    'ZeroChannelID',
    'decode',
    'encode',
    'new',
)


class ChannelID(bytes):
    """Unique, randomly chosen identifier for a channel, local to each peer.

    .. seealso::

        - :rfc:`7574#section-1.3` (:rfc:`page 8 <7574#page-8>`)
        - :rfc:`7574#section-12.1` (:rfc:`page 69 <7574#page-69>`)
    """
    __slots__ = ()

    def __new__(cls, data):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError('bytes expected, got {!r}'.format(data))
        if len(data) != DWORD:
            raise ValueError('channel id must be 4 bytes sized')
        return super().__new__(cls, bytes(data))


#: All-zero channel ID is used for handshake procedure. If datagram is sent
#: by the initiating peer, destination channel ID MUST be all-zero one. If
#: peer want to explicitly close channel, it SHOULD send a handshake with
#: all-zero source channel ID.
#:
#: .. seealso::
#:
#:    - :rfc:`7574#section-8.4`
#:
ZeroChannelID = ChannelID(b'\x00' * DWORD)


def decode(data):
    """Decodes channel ID from PPSPP datagram.

    :param memoryview data: Binary data
    :returns: :class:`ChannelID` instance and the remaining data
    :rtype: tuple
    """
    channel_id, rest = data[:DWORD], data[DWORD:]
    return ChannelID(channel_id), rest


def encode(channel_id):
    """Encodes channel ID into bytes.

    :param ChannelID channel_id: Channel ID
    :rtype: bytes
    """
    return bytes(ChannelID(channel_id))


def new():
    """Returns new random channel ID.

    :rtype: :class:`ChannelID`
    """
    return ChannelID(os.urandom(DWORD))
