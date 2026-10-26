"""
Unit tests for Python Huffman Engine
Tests frequency, tree building, coding, bit packing, file format, and verification.
"""

import unittest
from huffman import (
    count_frequencies,
    calculate_probabilities,
    calculate_entropy,
    build_tree,
    generate_codes,
    encode_bytes,
    pack_bits,
    unpack_bits,
    decode_bitstring,
    build_huff_payload,
    parse_huff_payload,
    verify_decompression,
    generate_full_analysis,
)
from huffman.file_format import compress, decompress

class TestHuffmanEngine(unittest.TestCase):

    def test_frequency_and_entropy(self):
        text = b"aabbbc"
        freqs = count_frequencies(text)
        self.assertEqual(freqs[ord('a')], 2)
        self.assertEqual(freqs[ord('b')], 3)
        self.assertEqual(freqs[ord('c')], 1)

        probs = calculate_probabilities(freqs, len(text))
        entropy = calculate_entropy(probs)
        self.assertGreater(entropy, 1.0)
        self.assertLess(entropy, 2.0)

    def test_single_symbol_edge_case(self):
        data = b"aaaaaa"
        freqs = count_frequencies(data)
        root, _ = build_tree(freqs)
        codes = generate_codes(root)
        self.assertIn(ord('a'), codes)
        
        bitstring, total_bits = encode_bytes(data, codes)
        self.assertEqual(total_bits, 6)
        
        packed, valid_last = pack_bits(bitstring)
        unpacked = unpack_bits(packed, total_bits)
        self.assertEqual(unpacked, bitstring)

        decoded = decode_bitstring(unpacked, root)
        self.assertEqual(decoded, data)

    def test_compress_decompress_roundtrip(self):
        test_cases = [
            b"hello huffman lab! 1234567890",
            b"A B A C",
            b"x",
            b"",
            bytes(range(256)) * 2, # All byte values 0-255
            b"Repeated data repeated data repeated data repeated data repeated data"
        ]

        for original in test_cases:
            huff_bytes, comp_stats = compress(original)
            decompressed, dec_stats = decompress(huff_bytes)
            self.assertEqual(decompressed, original)
            
            verification = verify_decompression(original, decompressed)
            self.assertTrue(verification["verified"])
            self.assertEqual(verification["original_hash"], verification["decompressed_hash"])

    def test_full_analysis(self):
        data = b"The quick brown fox jumps over the lazy dog"
        analysis = generate_full_analysis(data, "test.txt")
        self.assertEqual(analysis["filename"], "test.txt")
        self.assertEqual(analysis["original_size"], len(data))
        self.assertIn("tree", analysis)
        self.assertIn("code_table", analysis)
        self.assertIn("cs_explanation", analysis)

if __name__ == "__main__":
    unittest.main()
