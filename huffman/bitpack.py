"""
Bit Packing & Decoding Module for Huffman Lab
Implements bit-level shifting, packing bitstrings into byte arrays, and tree decoding.
"""

from typing import Dict, Tuple, Optional
from .tree import HuffmanNode

def encode_bytes(data: bytes, codes: Dict[int, str]) -> Tuple[str, int]:
    """
    Converts data bytes into a concatenated binary bitstring.
    Returns (bitstring, total_bit_count).
    """
    bit_chunks = []
    for byte in data:
        if byte not in codes:
            raise KeyError(f"Byte {byte} (0x{byte:02X}) missing from Huffman code map.")
        bit_chunks.append(codes[byte])

    bitstring = "".join(bit_chunks)
    return bitstring, len(bitstring)

def pack_bits(bitstring: str) -> Tuple[bytes, int]:
    """
    Packs a string of '0' and '1' characters into actual binary bytes.
    Returns (packed_bytes, valid_bits_in_last_byte).
    """
    if not bitstring:
        return b"", 0

    total_bits = len(bitstring)
    valid_bits_last = total_bits % 8
    if valid_bits_last == 0:
        valid_bits_last = 8

    num_bytes = (total_bits + 7) // 8
    packed = bytearray(num_bytes)

    for i, bit_char in enumerate(bitstring):
        if bit_char == '1':
            byte_idx = i // 8
            bit_pos = 7 - (i % 8)
            packed[byte_idx] |= (1 << bit_pos)

    return bytes(packed), valid_bits_last

def unpack_bits(packed_bytes: bytes, total_bits: int) -> str:
    """
    Reconstructs the original bitstring from packed bytes using total_bits count.
    """
    if total_bits == 0 or not packed_bytes:
        return ""

    bits = []
    for i in range(total_bits):
        byte_idx = i // 8
        bit_pos = 7 - (i % 8)
        bit_val = (packed_bytes[byte_idx] >> bit_pos) & 1
        bits.append("1" if bit_val else "0")

    return "".join(bits)

def decode_bitstring(bitstring: str, root: Optional[HuffmanNode]) -> bytes:
    """
    Decodes a bitstring back into original bytes using the Huffman Tree.
    """
    if root is None or not bitstring:
        return b""

    # Single unique character tree edge case
    if root.is_leaf():
        if root.symbol is None:
            return b""
        return bytes([root.symbol]) * len(bitstring)

    result = bytearray()
    curr = root

    for bit in bitstring:
        curr = curr.left if bit == '0' else curr.right
        if curr is None:
            raise ValueError("Bitstream error: path navigated to non-existent node.")
        if curr.is_leaf():
            if curr.symbol is not None:
                result.append(curr.symbol)
            curr = root

    return bytes(result)
