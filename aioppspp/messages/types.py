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

import enum

__all__ = (
    'MessageType',
)


class MessageType(enum.IntEnum):
    """Enumeration of message types.

    .. seealso:

        - :rfc:`7574#section-8.2`.
    """
    HANDSHAKE = 0
    DATA = 1
    ACK = 2
    HAVE = 3
    INTEGRITY = 4
    PEX_RESv4 = 5
    PEX_REQ = 6
    SIGNED_INTEGRITY = 7
    REQUEST = 8
    CANCEL = 9
    CHOKE = 10
    UNCHOKE = 11
    PEX_RESv6 = 12
    PEX_REScert = 13
