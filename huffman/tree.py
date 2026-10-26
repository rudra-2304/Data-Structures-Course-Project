"""
Huffman Tree Module for Huffman Lab
Implements priority queue heap building, Huffman tree creation, and JSON serialization.
"""

import heapq
from typing import Dict, Optional, Any, Tuple

class HuffmanNode:
    def __init__(
        self,
        node_id: int,
        symbol: Optional[int],
        freq: int,
        left: Optional["HuffmanNode"] = None,
        right: Optional["HuffmanNode"] = None
    ):
        self.id = node_id
        self.symbol = symbol  # None for internal nodes, 0-255 for leaf nodes
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

def format_symbol_display(symbol: Optional[int]) -> str:
    """Formats symbol for human UI display."""
    if symbol is None:
        return ""
    if symbol == 32:
        return "SPACE"
    if symbol == 10:
        return "\\n"
    if symbol == 13:
        return "\\r"
    if symbol == 9:
        return "\\t"
    if 32 < symbol <= 126:
        return chr(symbol)
    return f"0x{symbol:02X}"

def build_tree(freq_map: Dict[int, int]) -> Tuple[Optional[HuffmanNode], int]:
    """
    Builds a Huffman Tree from a frequency map.
    Returns (root_node, total_node_count).
    Handles edge cases:
      - empty freq_map -> (None, 0)
      - single unique symbol -> parent node with single child
    """
    if not freq_map:
        return None, 0

    node_counter = 0
    heap = []

    # Sort items deterministically by frequency ascending, then symbol ascending
    sorted_items = sorted(freq_map.items(), key=lambda item: (item[1], item[0]))

    for symbol, freq in sorted_items:
        node = HuffmanNode(node_id=node_counter, symbol=symbol, freq=freq)
        node_counter += 1
        # Heap tuple: (frequency, tie_breaker_counter, node)
        heapq.heappush(heap, (freq, node.id, node))

    # Single unique symbol edge case
    if len(heap) == 1:
        _, _, child = heapq.heappop(heap)
        root = HuffmanNode(node_id=node_counter, symbol=None, freq=child.freq, left=child, right=None)
        node_counter += 1
        return root, node_counter

    # Standard min-heap tree construction
    while len(heap) > 1:
        freq1, _, left = heapq.heappop(heap)
        freq2, _, right = heapq.heappop(heap)

        parent = HuffmanNode(
            node_id=node_counter,
            symbol=None,
            freq=freq1 + freq2,
            left=left,
            right=right
        )
        node_counter += 1
        heapq.heappush(heap, (parent.freq, parent.id, parent))

    _, _, root = heapq.heappop(heap)
    return root, node_counter

def tree_to_dict(
    node: Optional[HuffmanNode],
    codes_map: Dict[int, str],
    total_bytes: int,
    current_code: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Converts a Huffman tree into a structured nested JSON dictionary
    designed for dynamic interactive visualization.
    """
    if node is None:
        return None

    prob = round(node.freq / total_bytes, 4) if total_bytes > 0 else 0.0
    display_label = format_symbol_display(node.symbol) if node.is_leaf() else f"Σ = {node.freq}"
    code_str = codes_map.get(node.symbol, current_code) if node.is_leaf() else current_code

    result = {
        "id": node.id,
        "symbol": node.symbol,
        "label": display_label,
        "freq": node.freq,
        "prob": prob,
        "is_leaf": node.is_leaf(),
        "code": code_str,
        "left": tree_to_dict(node.left, codes_map, total_bytes, current_code + "0"),
        "right": tree_to_dict(node.right, codes_map, total_bytes, current_code + "1"),
    }
    return result
