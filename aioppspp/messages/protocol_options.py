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
from collections import (
    namedtuple,
)

from .types import (
    MessageType,
)
from ..constants import (
    BYTE,
    WORD,
    DWORD,
    QWORD,
)

__all__ = (
    'ProtocolOptions',
    'Version',
    'ContentIntegrityProtectionMethod',
    'CIPM',
    'MerkleHashTreeFunction',
    'MHTF',
    'LiveSignatureAlgorithm',
    'LSA',
    'ChunkAddressingMethod',
    'CAM',
)


class ProtocolOptionsId(enum.IntEnum):
    """Protocol options identifiers enumeration.

    This enumeration is used to map protocol options codes with the record
    field names.

    .. seealso::

        - :rfc:`7574#section-7`
    """
    version = 0
    minimum_version = 1
    swarm_identifier = 2
    content_integrity_protection_method = 3
    merkle_hash_tree_function = 4
    live_signature_algorithm = 5
    chunk_addressing_method = 6
    live_discard_window = 7
    supported_messages = 8
    chunk_size = 9
    end_option = 255


class Version(enum.IntEnum):
    """Supported PPSPP version.

    +---------+----------------------------------------+
    | Version | Description                            |
    +=========+========================================+
    | 0       | Reserved                               |
    +---------+----------------------------------------+
    | 1       | Protocol as described in this document |
    +---------+----------------------------------------+
    | 2-255   | Unassigned                             |
    +---------+----------------------------------------+

    .. seealso::

        - :rfc:`7574#section-7.2`
    """
    rfc7574 = 1


class ContentIntegrityProtectionMethod(enum.IntEnum):
    """Content Integrity Protection Method enumeration.

    The "Merkle Hash Tree" method is the default for static content, see
    :rfc:`Section 5.1 <7574#section-5.1>. "Sign All", and "Unified Merkle Tree"
    are for live content, see :rfc:`Section 6.1 <7574#section-6.1>`, with
    "Unified Merkle Tree" being the default.

    +--------+-------------------------+
    | Method | Description             |
    +========+=========================+
    | 0      | No integrity protection |
    +--------+-------------------------+
    | 1      | Merkle Hash Tree        |
    +--------+-------------------------+
    | 2      | Sign All                |
    +--------+-------------------------+
    | 3      | Unified Merkle Tree     |
    +--------+-------------------------+
    | 4-255  | Unassigned              |
    +--------+-------------------------+

    .. seealso::

        - :rfc:`7574#section-7.5`
    """
    no_protection = 0
    merkle_hash_tree = 1
    sign_all = 2
    unified_merkle_tree = 3


class MerkleHashTreeFunction(enum.IntEnum):
    """Merkle Hash Tree function enumeration.

    When the content integrity protection method is "Merkle Hash Tree",
    this option defining which hash function is used for the tree MUST be
    included.

    +----------+-------------+
    | Function | Description |
    +==========+=============+
    | 0        | SHA-1       |
    +----------+-------------+
    | 1        | SHA-224     |
    +----------+-------------+
    | 2        | SHA-256     |
    +----------+-------------+
    | 3        | SHA-384     |
    +----------+-------------+
    | 4        | SHA-512     |
    +----------+-------------+
    | 5-255    | Unassigned  |
    +----------+-------------+

    .. seealso::

        - :rfc:`7574#section-7.6`
    """
    sha1 = 0
    sha224 = 1
    sha256 = 2
    sha384 = 3
    sha512 = 4


class LiveSignatureAlgorithm(enum.IntEnum):
    """Live Signature Algorithm enumeration.

    When the content integrity protection method is "Sign All" or
    "Unified Merkle Tree", this option MUST be defined.  The 8-bit value of
    this option is one of the values listed in the "Domain Name System Security
    (DNSSEC) Algorithm Numbers" registry.  The :rfc:`RSASHA1 <4034>`,
    :rfc:`RSASHA256 <5702>`, :rfc:`ECDSAP256SHA256 <6605>` and
    :rfc:`ECDSAP384SHA384 <6605>` algorithms are mandatory to implement.
    Default is ECDSAP256SHA256.

    .. seealso::

        - :rfc:`7574#section-7.6`
        - `Domain Name System Security (DNSSEC) Algorithm Numbers <http://www.iana.org/assignments/dns-sec-alg-numbers/dns-sec-alg-numbers.xhtml>`_
    """
    #: RSA/MD5 (deprecated, see 5) (:rfc:`3110`, :rfc:`4034`)
    rsamd5 = 1
    #: Diffie-Hellman (:rfc:`2539`)
    dh = 2
    #: DSA/SHA1 (:rfc:`3755`, :rfc:`2536`)
    dsa = 3
    #: RSA/SHA-1 (:rfc:`3110`, :rfc:`4034`)
    rsasha1 = 5
    #: DSA-NSEC3-SHA1 (:rfc:`5155`)
    dsa_nsec3_sha1 = 6
    #: RSASHA1-NSEC3-SHA1 (:rfc:`5155`)
    rsasha1_nsec3_sha1 = 7
    #: RSA/SHA-256 (:rfc:`5702`)
    rsasha256 = 8
    #: RSA/SHA-512 (:rfc:`5702`)
    rsasha512 = 10
    #: GOST R 34.10-2001 (:rfc:`5933`)
    ecc_gost = 12
    #: ECDSA Curve P-256 with SHA-256 (:rfc:`6605`)
    ecdsap256sha256 = 13
    #: ECDSA Curve P-384 with SHA-384 (:rfc:`6605`)
    ecdsap384sha384 = 13
    #: Private algorithm (:rfc:`4034`)
    privatedns = 253
    #: Private algorithm OID (:rfc:`4034`)
    privateoid = 254


class ChunkAddressingMethod(enum.IntEnum):
    """Chunk Addressing Method enumeration.

    Implementations MUST support "32-bit chunk ranges" and "64-bit chunk
    ranges".  Default is "32-bit chunk ranges".

    +--------+---------------------+
    | Method | Description         |
    +========+=====================+
    | 0      | 32-bit bins         |
    +--------+---------------------+
    | 1      | 64-bit byte ranges  |
    +--------+---------------------+
    | 2      | 32-bit chunk ranges |
    +--------+---------------------+
    | 3      | 64-bit bins         |
    +--------+---------------------+
    | 4      | 64-bit chunk ranges |
    +--------+---------------------+
    | 5-255  | Unassigned          |
    +--------+---------------------+

    .. seealso::

        - :rfc:`7574#section-7.8`
    """
    bins32 = 0
    bytes64 = 1
    chunks32 = 2
    bins64 = 3
    chunks64 = 4


class LiveDiscardWindowSize(enum.IntEnum):
    bins32 = DWORD
    bytes64 = QWORD
    chunks32 = DWORD
    bins64 = QWORD
    chunks64 = QWORD


# Short aliases because ETOOLONGNAMES
CAM = ChunkAddressingMethod
CIPM = ContentIntegrityProtectionMethod
LDWS = LiveDiscardWindowSize
LSA = LiveSignatureAlgorithm
MHTF = MerkleHashTreeFunction


class ProtocolOptions(namedtuple('ProtocolOptions', (
    'version',
    'minimum_version',
    'swarm_identifier',
    'content_integrity_protection_method',
    'merkle_hash_tree_function',
    'live_signature_algorithm',
    'chunk_addressing_method',
    'live_discard_window',
    'supported_messages',
    'chunk_size'
))):
    """Protocol options record.

    The payload of the HANDSHAKE message contains a sequence of protocol
    options.  The protocol options encode the swarm metadata just
    described to enable an end-to-end check to see whether the peers are
    in the right swarm.  Additionally, the options encode a number of
    per-peer configuration parameters.

    The list of protocol options MUST be sorted on code value (ascending) in
    a HANDSHAKE message:

    +--------+-------------------------------------+
    | Code   | Description                         |
    +========+=====================================+
    | 0      | Version                             |
    +--------+-------------------------------------+
    | 1      | Minimum Version                     |
    +--------+-------------------------------------+
    | 2      | Swarm Identifier                    |
    +--------+-------------------------------------+
    | 3      | Content Integrity Protection Method |
    +--------+-------------------------------------+
    | 4      | Merkle Hash Tree Function           |
    +--------+-------------------------------------+
    | 5      | Live Signature Algorithm            |
    +--------+-------------------------------------+
    | 6      | Chunk Addressing Method             |
    +--------+-------------------------------------+
    | 7      | Live Discard Window                 |
    +--------+-------------------------------------+
    | 8      | Supported Messages                  |
    +--------+-------------------------------------+
    | 9      | Chunk Size                          |
    +--------+-------------------------------------+
    | 10-254 | Unassigned                          |
    +--------+-------------------------------------+
    | 255    | End Option                          |
    +--------+-------------------------------------+


    .. seealso::

        - :rfc:`7574#section-7`
    """
    __slots__ = ()

    def __new__(cls,
                version: Version=None,
                minimum_version: Version=None,
                swarm_identifier: bytes=None,
                content_integrity_protection_method: CIPM=None,
                merkle_hash_tree_function: MHTF=None,
                live_signature_algorithm: LSA=None,
                chunk_addressing_method: CAM=None,
                live_discard_window: int=None,
                supported_messages: set=None,
                chunk_size: int=None):

        params = {key: value for key, value in locals().items()
                  if key not in {'cls', '__class__'}}

        for param, value in params.items():
            if value is None:
                continue

            typespec = cls.__new__.__annotations__[param]
            if isinstance(value, typespec):
                continue

            try:
                params[param] = typespec(value)
            except Exception as exc:
                raise TypeError('{} expected to be {}, got {}'.format(
                    param, typespec, type(value))) from exc

        return super().__new__(cls, **params)


def decode(data):
    handlers = decode_handlers()
    offset = 0
    options = {key.name: None for key in ProtocolOptionsId
               if key is not ProtocolOptionsId.end_option}
    while True:
        option_id, offset = decode_value(data, offset, BYTE)
        option = ProtocolOptionsId(option_id[0])
        if option is ProtocolOptionsId.end_option:
            break
        if options[option.name] is not None:
            raise ValueError('duplicate option {!r} provided'.format(option))
        value, offset = handlers[option](data, offset, options)
        options[option.name] = value
    return ProtocolOptions(**options), data[offset:]


def encode(options):
    data = bytearray()
    handlers = encode_handlers()
    for option_id, value in zip(ProtocolOptionsId, options):
        if value is None:
            continue
        value = handlers[option_id](value, options)
        if value is not None:
            data.append(option_id.value)
            data.extend(value)
    data.append(ProtocolOptionsId.end_option.value)
    return data


def decode_handlers():
    return {
        ProtocolOptionsId.chunk_addressing_method:
            decode_chunk_addressing_method,
        ProtocolOptionsId.chunk_size:
            decode_chunk_size,
        ProtocolOptionsId.content_integrity_protection_method:
            decode_content_integrity_protection_method,
        ProtocolOptionsId.live_discard_window:
            decode_live_discard_window,
        ProtocolOptionsId.live_signature_algorithm:
            decode_live_signature_algorithm,
        ProtocolOptionsId.merkle_hash_tree_function:
            decode_merkle_hash_tree_function,
        ProtocolOptionsId.minimum_version:
            decode_minimum_version,
        ProtocolOptionsId.supported_messages:
            decode_supported_messages,
        ProtocolOptionsId.swarm_identifier:
            decode_swarm_id,
        ProtocolOptionsId.version:
            decode_version,
    }


def encode_handlers():
    return {
        ProtocolOptionsId.chunk_addressing_method:
            encode_chunk_addressing_method,
        ProtocolOptionsId.chunk_size:
            encode_chunk_size,
        ProtocolOptionsId.content_integrity_protection_method:
            encode_content_integrity_protection_method,
        ProtocolOptionsId.live_discard_window:
            encode_live_discard_window,
        ProtocolOptionsId.live_signature_algorithm:
            encode_live_signature_algorithm,
        ProtocolOptionsId.merkle_hash_tree_function:
            encode_merkle_hash_tree_function,
        ProtocolOptionsId.minimum_version:
            encode_minimum_version,
        ProtocolOptionsId.supported_messages:
            encode_supported_messages,
        ProtocolOptionsId.swarm_identifier:
            encode_swarm_id,
        ProtocolOptionsId.version:
            encode_version,
    }


def decode_version(data, offset, _):
    # 7.2.  Version
    #
    #  0                   1
    #  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 0 0 0|  Version (8)  |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, BYTE)
    return Version(value[0]), offset


def encode_version(version, _):
    return version.value.to_bytes(BYTE, 'big')


def decode_minimum_version(data, offset, _):
    # 7.3.  Minimum Version
    #
    # 0                   1
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 0 0 1| Min. Ver. (8) |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, BYTE)
    return Version(value[0]), offset


def encode_minimum_version(version, _):
    return version.to_bytes(BYTE, 'big')


def decode_swarm_id(data, offset, _):
    # 7.4.  Swarm Identifier
    # This option has the following structure:
    #
    # 0                   1                   2                   3
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 0 1 0|     Swarm ID Length (16)      |               ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # ~                       Swarm Identifier (variable)             ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    # The Swarm ID Length field contains the length of the single Swarm
    # Identifier that follows in bytes.  The Length field is 16 bits wide
    # to allow for large public keys as identifiers in live streaming.
    #
    swarm_id_length, offset = decode_value(data, offset, WORD)
    swarm_id_length = int.from_bytes(swarm_id_length, 'big')
    swarm_id, offset = decode_value(data, offset, swarm_id_length)
    return bytes(swarm_id), offset


def encode_swarm_id(swarm_id: bytes, _):
    swarm_id_length = len(swarm_id).to_bytes(WORD, 'big')
    return swarm_id_length + swarm_id


def decode_content_integrity_protection_method(data, offset, _):
    # 7.5.  Content Integrity Protection Method
    #
    # 0                   1
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 0 1 1|   CIPM (8)    |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, BYTE)
    return ContentIntegrityProtectionMethod(value[0]), offset


def encode_content_integrity_protection_method(cipm, _):
    return cipm.to_bytes(BYTE, 'big')


def decode_merkle_hash_tree_function(data, offset, _):
    # 7.6.  Merkle Tree Hash Function
    #
    # 0                   1
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 1 0 0|    MHF (8)    |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, BYTE)
    return MerkleHashTreeFunction(value[0]), offset


def encode_merkle_hash_tree_function(mhtf, _):
    return mhtf.to_bytes(BYTE, 'big')


def decode_live_signature_algorithm(data, offset, _):
    # 7.7.  Live Signature Algorithm
    #
    # 0                   1
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 1 0 1|    LSA (8)    |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, BYTE)
    return LiveSignatureAlgorithm(value[0]), offset


def encode_live_signature_algorithm(lsa: LSA, _):
    return lsa.to_bytes(BYTE, 'big')


def decode_chunk_addressing_method(data, offset, _):
    # 7.8.  Chunk Addressing Method
    #
    # 0                   1
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 1 1 0|    CAM (8)    |
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, BYTE)
    return ChunkAddressingMethod(value[0]), offset


def encode_chunk_addressing_method(cam, _):
    return cam.to_bytes(BYTE, 'big')


def decode_live_discard_window(data, offset, options):
    # 7.9.  Live Discard Window
    # The unit of the discard window depends on the chunk addressing method
    # used, see Table 6.  For bins and chunk ranges, it is a number of chunks;
    # for byte ranges, it is a number of bytes.  Its data type is the same as
    # for a bin, or one value in a range specification.  In other words, its
    # value is a 32-bit or 64-bit integer in big-endian format.
    # If this option is used, the Chunk Addressing Method MUST appear before
    # it in the list.
    #
    # 0                   1                   2                   3
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 0 1 1 1|       Live Discard Window (32 or 64)          ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # ~                                                               ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    method = options[ProtocolOptionsId.chunk_addressing_method.name]
    window_size = LiveDiscardWindowSize[method.name].value
    value, offset = decode_value(data, offset, window_size)
    return int.from_bytes(value, 'big'), offset


def encode_live_discard_window(live_discard_window, options):
    method = options.chunk_addressing_method
    if method is None:
        return None
    window_size = LiveDiscardWindowSize[method.name].value
    return live_discard_window.to_bytes(window_size, 'big')


def decode_supported_messages(data, offset, _):
    # 7.10.  Supported Messages
    # The set of messages supported can be derived from the compressed
    # bitmap by padding it with bytes of value 0 until it is 256 bits in
    # length.  Then, a 1 bit in the resulting bitmap at position X
    # (numbering left to right) corresponds to support for message type X,
    # see Table 7.  In other words, to construct the compressed bitmap,
    # create a bitmap with a 1 for each message type supported and a 0 for
    # a message type that is not, store it as an array of bytes, and
    # truncate it to the last non-zero byte.  An example of the first 16
    # bits of the compressed bitmap for a peer supporting every message
    # except ACKs and PEXs is 11011001 11110000.
    #
    #  0                   1                   2                   3
    #  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 1 0 0 0| SupMsgLen (8) |                               ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # ~            Supported Messages Bitmap (variable, max 256)      ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #
    message_types_length, offset = decode_value(data, offset, BYTE)
    message_types_length = int.from_bytes(message_types_length, 'big')
    all_message_types = list(MessageType)
    supported_messages = set()
    for n in range(message_types_length):
        value, offset = decode_value(data, offset, BYTE)
        value = int.from_bytes(value, 'big')
        message_types = all_message_types[n * 8: n * 8 + 8]
        mapping = list(zip(map(int, bin(value)[2:]), message_types))
        supported_messages |= {msgtype for bit, msgtype in mapping if bit}
    return supported_messages, offset


def encode_supported_messages(messages, _):
    mask = [1 if msgtype in messages else 0 for msgtype in MessageType]
    fits = len(mask) % 8 == 0
    mask += [0] * (0 if fits else 8 - len(mask) % 8)
    supported_messages = int(''.join(map(str, mask)), 2)
    supported_messages = supported_messages.to_bytes(len(mask) // 8, 'big')
    supported_messages_length = len(supported_messages).to_bytes(BYTE, 'big')
    return supported_messages_length + supported_messages


def decode_chunk_size(data, offset, _):
    # 7.11.  Chunk Size
    # Its value is a 32-bit integer denoting the size of the chunks in bytes
    # in big-endian format.  When variable chunk sizes are used, this option
    # MUST be set to the special value 0xFFFFFFFF.  Section 8.1 explains how
    # content publishers can determine a value for this option.
    #
    # 0                   1                   2                   3
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # |0 0 0 0 1 0 0 1|       Chunk Size (32)                         ~
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # ~               |
    # +-+-+-+-+-+-+-+-+
    #
    value, offset = decode_value(data, offset, DWORD)
    return int.from_bytes(value, 'big'), offset


def encode_chunk_size(chunk_size, _):
    return chunk_size.to_bytes(DWORD, 'big')


def decode_value(data, offset, length):
    value = data[offset:offset + length]
    if len(value) != length:
        raise ValueError('Expected read {} bytes, got only {}'
                         ''.format(length, len(value)))
    return value, offset + length
