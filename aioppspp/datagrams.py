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

from . import channel_ids
from . import messages
from .channel_ids import (
    ChannelID,
)
from .messages import (
    Message,
)

__all__ = (
    'Datagram',
    'decode',
    'encode',
)


class Datagram(namedtuple('Datagram', ('channel_id', 'messages'))):
    """A sequence of messages that is offered as a unit to the
    underlying transport protocol (UDP, etc.) prefixed by channel ID.
    The datagram is PPSPP's Protocol Data Unit (PDU).

    .. seealso::

        - :rfc:`7574#section-1.3` (:rfc:`page 6 <7574#page-6>`)
    """
    __slots__ = ()

    def __new__(cls, channel_id, messages):
        assert all(isinstance(message, Message) for message in messages)
        return super().__new__(cls, ChannelID(channel_id), tuple(messages))


def decode(data):
    """Decodes bytes into datagram instance.

    :param memoryview data: Binary data
    :rtype: :class:`Datagram`
    """
    channel_id, rest = channel_ids.decode(data)
    return Datagram(channel_id, messages.decode(rest))


def encode(datagram):
    """Encodes datagram instance into bytes.

    :param Datagram datagram: Datagram instance
    :rtype: bytes
    """
    data = bytearray()
    data.extend(channel_ids.encode(datagram.channel_id))
    data.extend(messages.encode(datagram.messages))
    return bytes(data)
