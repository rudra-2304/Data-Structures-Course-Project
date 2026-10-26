"""
Huffman Code Generation & Analysis Module
Generates prefix codes from tree and calculates code statistics.
"""

from typing import Dict, Optional
from .tree import HuffmanNode

def generate_codes(root: Optional[HuffmanNode]) -> Dict[int, str]:
    """
    Generates binary prefix codes for each leaf in the Huffman tree.
    Returns a dictionary mapping byte value (0-255) -> bitstring ("010...").
    """
    codes: Dict[int, str] = {}
    if root is None:
        return codes

    # Single unique symbol edge case
    if root.is_leaf():
        codes[root.symbol] = "0"
        return codes

    def traverse(node: Optional[HuffmanNode], prefix: str):
        if node is None:
            return
        if node.is_leaf() and node.symbol is not None:
            codes[node.symbol] = prefix
            return
        traverse(node.left, prefix + "0")
        traverse(node.right, prefix + "1")

    traverse(root, "")
    return codes

def calculate_avg_code_length(probabilities: Dict[int, float], codes: Dict[int, str]) -> float:
    """
    Calculates Average Code Length:
    L_avg = sum(P(x) * len(code(x))) for all x.
    """
    if not probabilities or not codes:
        return 0.0

    avg_len = 0.0
    for symbol, prob in probabilities.items():
        if symbol in codes:
            avg_len += prob * len(codes[symbol])

    return round(avg_len, 4)

def calculate_efficiency(entropy: float, avg_code_length: float) -> float:
    """
    Calculates Huffman Coding Efficiency (%):
    Efficiency = (Entropy / Average Code Length) * 100
    Theoretical upper bound is 100%.
    """
    if avg_code_length == 0:
        return 0.0
    eff = (entropy / avg_code_length) * 100.0
    # Cap at 100% to account for precision rounding
    return round(min(eff, 100.0), 2)
