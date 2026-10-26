"""
.huff Binary File Format Module for Huffman Lab
Serializes and deserializes compressed binary streams with integrity headers.
"""

import struct
import hashlib
from typing import Dict, Tuple, Any

from .frequency import count_frequencies
from .tree import build_tree
from .coder import generate_codes
from .bitpack import encode_bytes, pack_bits, unpack_bits, decode_bitstring

MAGIC_HEADER = b"HUFF1"

def build_huff_payload(
    original_size: int,
    freq_map: Dict[int, int],
    packed_bytes: bytes,
    valid_bits_last: int,
    total_bits: int
) -> bytes:
    """
    Builds the complete binary .huff payload buffer.
    Format:
      [5 bytes] Magic 'HUFF1'
      [4 bytes] Original byte length (uint32 BE)
      [2 bytes] Symbol count N (uint16 BE)
      [N * 5 bytes] Symbol table: [1 byte symbol][4 bytes freq (uint32 BE)]
      [1 byte] Valid bits in last byte (uint8)
      [4 bytes] Total encoded bit count (uint32 BE)
      [M bytes] Packed bitstream payload
    """
    header = bytearray()
    header.extend(MAGIC_HEADER)
    header.extend(struct.pack(">I", original_size))
    
    entries = sorted(freq_map.items())
    header.extend(struct.pack(">H", len(entries)))

    for symbol, freq in entries:
        header.extend(struct.pack(">BI", symbol, freq))

    header.extend(struct.pack(">B", valid_bits_last))
    header.extend(struct.pack(">I", total_bits))

    return bytes(header) + packed_bytes

def parse_huff_payload(huff_bytes: bytes) -> Tuple[int, Dict[int, int], int, int, bytes]:
    """
    Parses a binary .huff payload buffer.
    Returns (original_size, freq_map, valid_bits_last, total_bits, packed_payload_bytes).
    """
    if len(huff_bytes) < 16:  # Min header size
        raise ValueError("Invalid .huff payload: File is too small.")

    offset = 0
    magic = huff_bytes[offset:offset + 5]
    offset += 5

    if magic != MAGIC_HEADER:
        raise ValueError("Invalid .huff payload: Bad magic identifier.")

    original_size, num_symbols = struct.unpack_from(">IH", huff_bytes, offset)
    offset += 6

    freq_map: Dict[int, int] = {}
    for _ in range(num_symbols):
        if offset + 5 > len(huff_bytes):
            raise ValueError("Invalid .huff payload: Corrupted symbol frequency table.")
        symbol, freq = struct.unpack_from(">BI", huff_bytes, offset)
        offset += 5
        freq_map[symbol] = freq

    if offset + 5 > len(huff_bytes):
        raise ValueError("Invalid .huff payload: Header incomplete.")

    valid_bits_last, total_bits = struct.unpack_from(">BI", huff_bytes, offset)
    offset += 5

    packed_payload = huff_bytes[offset:]
    return original_size, freq_map, valid_bits_last, total_bits, packed_payload

def compress(data: bytes) -> Tuple[bytes, Dict[str, Any]]:
    """
    Compresses raw data bytes into .huff binary format.
    """
    original_size = len(data)

    if original_size == 0:
        empty_payload = build_huff_payload(0, {}, b"", 0, 0)
        return empty_payload, {
            "original_size": 0,
            "compressed_size": len(empty_payload),
            "total_bits": 0,
            "space_saved": 0.0,
            "compression_ratio": 0.0
        }

    freq_map = count_frequencies(data)
    root, _ = build_tree(freq_map)
    codes = generate_codes(root)
    bitstring, total_bits = encode_bytes(data, codes)
    packed_bytes, valid_bits_last = pack_bits(bitstring)

    huff_payload = build_huff_payload(
        original_size=original_size,
        freq_map=freq_map,
        packed_bytes=packed_bytes,
        valid_bits_last=valid_bits_last,
        total_bits=total_bits
    )

    compressed_size = len(huff_payload)
    space_saved = (1.0 - (compressed_size / original_size)) * 100.0 if original_size > 0 else 0.0
    compression_ratio = compressed_size / original_size if original_size > 0 else 0.0

    stats = {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "total_bits": total_bits,
        "space_saved": round(space_saved, 2),
        "compression_ratio": round(compression_ratio, 4)
    }

    return huff_payload, stats

def decompress(huff_bytes: bytes) -> Tuple[bytes, Dict[str, Any]]:
    """
    Decompresses .huff binary payload back into original data bytes.
    """
    original_size, freq_map, valid_bits_last, total_bits, packed_payload = parse_huff_payload(huff_bytes)

    if original_size == 0:
        return b"", {"original_size": 0, "decompressed_size": 0, "status": "Success (Empty file)"}

    root, _ = build_tree(freq_map)
    bitstring = unpack_bits(packed_payload, total_bits)
    decompressed_data = decode_bitstring(bitstring, root)

    if len(decompressed_data) != original_size:
        raise ValueError(f"Decompression size mismatch: Expected {original_size} bytes, got {len(decompressed_data)} bytes.")

    stats = {
        "original_size": original_size,
        "compressed_size": len(huff_bytes),
        "decompressed_size": len(decompressed_data),
        "status": "Success"
    }

    return decompressed_data, stats

def verify_decompression(original: bytes, decompressed: bytes) -> Dict[str, Any]:
    """
    Verifies that decompressed data matches original data byte-for-byte.
    Computes SHA-256 hashes for cryptographic assurance.
    """
    orig_hash = hashlib.sha256(original).hexdigest()
    dec_hash = hashlib.sha256(decompressed).hexdigest()
    matches = orig_hash == dec_hash and original == decompressed

    return {
        "verified": matches,
        "original_hash": orig_hash,
        "decompressed_hash": dec_hash,
        "original_size": len(original),
        "decompressed_size": len(decompressed),
        "byte_difference": len(decompressed) - len(original)
    }
