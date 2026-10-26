"""
Statistics & Computer Science Analysis Module for Huffman Lab
Generates statistical metrics and computer science theoretical insights.
"""

from typing import Dict, Any, List
from .frequency import count_frequencies, calculate_probabilities, calculate_entropy
from .tree import build_tree, tree_to_dict, format_symbol_display
from .coder import generate_codes, calculate_avg_code_length, calculate_efficiency
from .bitpack import encode_bytes, pack_bits
from .file_format import compress

def generate_full_analysis(data: bytes, filename: str = "input_data") -> Dict[str, Any]:
    """
    Generates complete analysis dictionary for an input file or text string.
    Includes frequency table, tree structure, statistics, and theoretical CS insight.
    """
    total_bytes = len(data)

    if total_bytes == 0:
        return {
            "filename": filename,
            "original_size": 0,
            "compressed_size": 16, # header overhead
            "unique_symbols": 0,
            "entropy": 0.0,
            "avg_code_length": 0.0,
            "efficiency": 0.0,
            "space_saved": 0.0,
            "compression_ratio": 0.0,
            "code_table": [],
            "top_symbols": [],
            "tree": None,
            "cs_explanation": "The file is completely empty. Header metadata overhead exceeds data payload, resulting in net negative compression."
        }

    # 1. Frequency Analysis
    freq_map = count_frequencies(data)
    probs = calculate_probabilities(freq_map, total_bytes)
    entropy = calculate_entropy(probs)

    # 2. Tree Construction & Code Generation
    root, node_count = build_tree(freq_map)
    codes = generate_codes(root)
    avg_code_len = calculate_avg_code_length(probs, codes)
    efficiency = calculate_efficiency(entropy, avg_code_len)

    # 3. Encoding & Bit Packing
    bitstring, total_bits = encode_bytes(data, codes)
    packed_bytes, valid_bits_last = pack_bits(bitstring)

    # 4. Compression stats
    compressed_payload, comp_stats = compress(data)
    compressed_size = comp_stats["compressed_size"]
    space_saved = comp_stats["space_saved"]
    ratio = comp_stats["compression_ratio"]

    # 5. Build Code Table List
    code_table: List[Dict[str, Any]] = []
    for symbol, count in sorted(freq_map.items(), key=lambda x: (-x[1], x[0])):
        code = codes.get(symbol, "")
        prob = probs.get(symbol, 0.0)
        code_table.append({
            "symbol": symbol,
            "char_display": format_symbol_display(symbol),
            "freq": count,
            "prob": round(prob, 4),
            "prob_pct": round(prob * 100, 2),
            "code": code,
            "code_length": len(code)
        })

    # Top symbols for overview
    top_symbols = code_table[:5]

    # 6. JSON Tree representation
    tree_json = tree_to_dict(root, codes, total_bytes)

    # 7. Generate Theoretical CS Commentary
    cs_explanation = generate_cs_insight(
        unique_symbols=len(freq_map),
        entropy=entropy,
        avg_code_len=avg_code_len,
        efficiency=efficiency,
        space_saved=space_saved,
        total_bytes=total_bytes
    )

    return {
        "filename": filename,
        "original_size": total_bytes,
        "compressed_size": compressed_size,
        "total_bits": total_bits,
        "unique_symbols": len(freq_map),
        "entropy": entropy,
        "avg_code_length": avg_code_len,
        "efficiency": efficiency,
        "space_saved": space_saved,
        "compression_ratio": ratio,
        "code_table": code_table,
        "top_symbols": top_symbols,
        "tree": tree_json,
        "cs_explanation": cs_explanation
    }

def generate_cs_insight(
    unique_symbols: int,
    entropy: float,
    avg_code_len: float,
    efficiency: float,
    space_saved: float,
    total_bytes: int
) -> str:
    """
    Generates computer science analysis based on Shannon's Source Coding Theorem.
    """
    if total_bytes < 20:
        return (
            f"For small files ({total_bytes} bytes), header metadata overhead (.huff symbol table and length markers) "
            "may dominate the output size. Huffman coding achieves its theoretical efficiency as file size increases."
        )

    if unique_symbols == 1:
        return (
            "This file contains only 1 unique symbol! Entropy is 0.00 bits/symbol. "
            f"Huffman coding assigns a 1-bit code to all {total_bytes} symbols, achieving optimal ~87.5% payload reduction "
            "relative to 8-bit fixed representation."
        )

    # High skew vs uniform
    fixed_bits = 8.0
    if entropy < 3.0:
        return (
            f"High Frequency Skew: The symbol distribution is heavily non-uniform with a low Shannon Entropy of {entropy:.2f} bits/symbol. "
            f"Frequent symbols are assigned short bit sequences, resulting in an average code length of {avg_code_len:.2f} bits/symbol "
            f"and an impressive space savings of {space_saved:.1f}%."
        )

    if efficiency > 95.0 and space_saved > 0:
        return (
            f"Optimal Prefix Coding: The average code length ({avg_code_len:.2f} bits) closely approaches the theoretical Shannon Entropy "
            f"bound ({entropy:.2f} bits/symbol), reaching {efficiency:.1f}% coding efficiency. This demonstrates Shannon's Source Coding Theorem in practice."
        )

    if space_saved <= 0:
        return (
            f"High Entropy Data: The symbol distribution is nearly uniform (Entropy = {entropy:.2f} bits/symbol near 8.0 bits max). "
            f"When symbols occur with almost equal probability, variable-length prefix coding offers little to no advantage over fixed 8-bit encoding, "
            f"causing file size to stay similar or slightly increase due to header overhead."
        )

    return (
        f"Moderate Compression: Symbol entropy is {entropy:.2f} bits/symbol. Huffman coding compresses the stream to an average "
        f"code length of {avg_code_len:.2f} bits/symbol ({efficiency:.1f}% efficiency), saving {space_saved:.1f}% space."
    )
