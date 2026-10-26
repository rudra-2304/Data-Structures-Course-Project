"""
Huffman Engine Package
Provides core Huffman coding, entropy analysis, tree construction,
bit packing, .huff format serialization, and statistics calculation.
"""

from .frequency import count_frequencies, calculate_probabilities, calculate_entropy
from .tree import HuffmanNode, build_tree, tree_to_dict
from .coder import generate_codes, calculate_avg_code_length, calculate_efficiency
from .bitpack import encode_bytes, pack_bits, unpack_bits, decode_bitstring
from .file_format import build_huff_payload, parse_huff_payload, verify_decompression
from .stats import generate_full_analysis

__all__ = [
    "count_frequencies",
    "calculate_probabilities",
    "calculate_entropy",
    "HuffmanNode",
    "build_tree",
    "tree_to_dict",
    "generate_codes",
    "calculate_avg_code_length",
    "calculate_efficiency",
    "encode_bytes",
    "pack_bits",
    "unpack_bits",
    "decode_bitstring",
    "build_huff_payload",
    "parse_huff_payload",
    "verify_decompression",
    "generate_full_analysis",
]
