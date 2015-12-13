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

import abc
from itertools import (
    chain,
)

from .types import (
    MessageType,
)
from ..constants import (
    BYTE,
)

__all__ = (
    'Message',
    'MessageType',
    'decode',
    'encode',
)


class Message(tuple, metaclass=abc.ABCMeta):
    """The basic unit of PPSPP communication.  A message will have
    different representations on the wire depending on the transport
    protocol used.  Messages are typically multiplexed into a
    datagram for transmission.

    This is an abstract base class for all PPSPP messages.

    .. seealso::

        - :rfc:`7574#section-1.3` (:rfc:`page 6 <7574#page-6>`)
    """
    __slots__ = ()

    @property
    @abc.abstractmethod
    def type(self):
        """Should return message type enumeration object."""
        raise NotImplementedError


def decode(data, *, handlers=None):
    """Decodes binary data into list of messages.

    :param memoryview data: Binary data
    :param dict handlers: Decode handlers mapping
    :returns: Tuple of :class:`Message`
    :rtype: tuple
    """
    messages = []
    while data:
        message, data = decode_message(data, handlers=handlers)
        messages.append(message)
    return tuple(messages)


def decode_message(data, *, handlers=None):
    handlers = handlers or decode_message_handlers()
    return handlers[MessageType(data[0])](data[BYTE:])


def encode(messages, *, handlers=None):
    """Encodes list of messages into bytes.

    :param tuple messages: List of :class:`Message`
    :param dict handlers: Encode handlers mapping
    :rtype: bytearray
    """
    data = bytearray()
    for message in messages:
        data.extend(encode_message(message, handlers=handlers))
    return data


def encode_message(message, *, handlers=None):
    handlers = handlers or encode_message_handlers()
    return bytearray(chain.from_iterable([
        [message.type.value],
        handlers[message.type](message),
    ]))


def decode_message_handlers():
    return {

    }


def encode_message_handlers():
    return {

    }
