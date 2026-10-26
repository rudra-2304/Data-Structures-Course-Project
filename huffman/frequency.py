"""
Frequency Analysis & Entropy Module for Huffman Lab
Computes symbol frequencies, probabilities, and Shannon Entropy.
"""

import math
from typing import Dict, Union

def count_frequencies(data: Union[bytes, bytearray]) -> Dict[int, int]:
    """
    Counts byte frequencies in a byte sequence.
    Returns a dictionary mapping byte value (0-255) -> frequency count.
    """
    freq_map: Dict[int, int] = {}
    for byte in data:
        freq_map[byte] = freq_map.get(byte, 0) + 1
    return freq_map

def calculate_probabilities(freq_map: Dict[int, int], total_bytes: int) -> Dict[int, float]:
    """
    Calculates probability P(x) for each symbol.
    """
    if total_bytes == 0:
        return {}
    return {symbol: count / total_bytes for symbol, count in freq_map.items()}

def calculate_entropy(probabilities: Dict[int, float]) -> float:
    """
    Calculates Shannon Entropy in bits per symbol:
    H(X) = - sum(P(x) * log2(P(x))) for all x with P(x) > 0.
    """
    if not probabilities:
        return 0.0
    
    entropy = 0.0
    for prob in probabilities.values():
        if prob > 0:
            entropy -= prob * math.log2(prob)
            
    return round(entropy, 4)
