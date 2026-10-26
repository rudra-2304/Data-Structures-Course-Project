"""
Flask Web Application & API Server for Huffman Lab (Matte White & Orange Edition)
Serves REST API endpoints for text file compression, live bit savings, and benchmark suite.
"""

import os
import base64
import glob
from flask import Flask, request, jsonify, render_template, Response

from huffman import (
    count_frequencies,
    calculate_probabilities,
    calculate_entropy,
    build_tree,
    generate_codes,
    calculate_avg_code_length,
    calculate_efficiency,
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

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    """Serves main Huffman Lab application interface."""
    return render_template("index.html")

@app.route("/visualiser")
def visualiser():
    """Serves the Huffman Tree Visualiser page."""
    return render_template("visualiser.html")

@app.route("/api/visualiser", methods=["POST"])
def api_visualiser():
    """
    Builds a Huffman tree from input text and returns:
      - Full tree JSON for SVG rendering
      - Priority queue steps for step-by-step log
      - Huffman codes table
      - Entropy and avg code length metrics
    """
    try:
        payload = request.get_json(silent=True) or {}
        text = payload.get("text", "")
        if not text.strip():
            return jsonify({"success": False, "error": "Input text cannot be empty."}), 400

        data = text.encode("utf-8")
        freq_map = count_frequencies(data)
        probs = calculate_probabilities(freq_map, len(data))
        entropy = calculate_entropy(probs)

        root, _ = build_tree(freq_map)
        codes = generate_codes(root)
        avg_len = calculate_avg_code_length(probs, codes)

        from huffman.tree import tree_to_dict, format_symbol_display

        tree_json = tree_to_dict(root, codes, len(data))

        # Build priority queue steps (mirrors the JS logic, using Python engine)
        sorted_items = sorted(freq_map.items(), key=lambda x: (x[1], x[0]))
        pq_steps = []
        pq_steps.append({
            "type": "init",
            "queue": [{"symbol": format_symbol_display(s), "freq": f} for s, f in sorted_items]
        })

        # Simulate merge steps
        import heapq
        sim_heap = []
        ctr = 0
        for sym, freq in sorted_items:
            heapq.heappush(sim_heap, (freq, ctr, {"symbol": format_symbol_display(sym), "freq": freq}))
            ctr += 1
        while len(sim_heap) > 1:
            fa, _, a = heapq.heappop(sim_heap)
            fb, _, b = heapq.heappop(sim_heap)
            merged = {"symbol": None, "freq": fa + fb}
            heapq.heappush(sim_heap, (fa + fb, ctr, merged))
            ctr += 1
            remaining = [item for _, _, item in sorted(sim_heap)]
            pq_steps.append({
                "type": "merge",
                "a": a,
                "b": b,
                "merged_freq": fa + fb,
                "queue": [{"symbol": x["symbol"] or "•", "freq": x["freq"]} for x in remaining]
            })

        codes_display = [
            {
                "symbol": format_symbol_display(sym),
                "freq": freq_map[sym],
                "prob_pct": round(probs[sym] * 100, 2),
                "code": codes[sym],
                "code_length": len(codes[sym])
            }
            for sym in sorted(codes.keys(), key=lambda s: len(codes[s]))
        ]

        return jsonify({
            "success": True,
            "tree": tree_json,
            "pq_steps": pq_steps,
            "codes": codes_display,
            "entropy": round(entropy, 4),
            "avg_code_length": round(avg_len, 4),
            "unique_symbols": len(freq_map),
            "total_chars": len(data)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Analyzes input text or uploaded file.
    Returns CS metrics, symbol frequencies, probabilities, codebook, and theoretical commentary.
    """
    try:
        data, filename = extract_request_data()
        analysis = generate_full_analysis(data, filename)
        return jsonify({"success": True, "data": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/simulator", methods=["POST"])
def api_simulator():
    """
    Generates live side-by-side comparison between 8-bit fixed ASCII bitstream
    and variable-length Huffman bitstream for input text.
    """
    try:
        payload = request.get_json(silent=True) or {}
        text = payload.get("text", "hello huffman")
        data = text.encode("utf-8") if isinstance(text, str) else bytes(text)

        if not data:
            return jsonify({"success": False, "error": "Input text cannot be empty."}), 400

        total_symbols = len(data)
        ascii_bits = total_symbols * 8

        freq_map = count_frequencies(data)
        root, _ = build_tree(freq_map)
        codes = generate_codes(root)

        bitstring, huffman_bits = encode_bytes(data, codes)
        space_saved = (1.0 - (huffman_bits / ascii_bits)) * 100.0 if ascii_bits > 0 else 0.0

        # Detailed character breakdown
        char_tokens = []
        ascii_bitstream = []
        for b_val in data:
            c_char = chr(b_val) if 32 <= b_val <= 126 else f"0x{b_val:02X}"
            if c_char == " ":
                c_char = "SPACE"
            c_code = codes.get(b_val, "0")
            c_ascii = f"{b_val:08b}"
            ascii_bitstream.append(c_ascii)
            char_tokens.append({
                "char": c_char,
                "ascii_bin": c_ascii,
                "huffman_code": c_code,
                "huffman_len": len(c_code),
                "bits_saved": 8 - len(c_code)
            })

        return jsonify({
            "success": True,
            "text": text,
            "total_symbols": total_symbols,
            "ascii_total_bits": ascii_bits,
            "huffman_total_bits": huffman_bits,
            "space_saved_pct": round(space_saved, 1),
            "ascii_bitstream": " ".join(ascii_bitstream),
            "huffman_bitstream": bitstring,
            "char_tokens": char_tokens
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/compress", methods=["POST"])
def api_compress():
    """
    Compresses input text or file data into binary .huff format wrapped as downloadable .compressed.txt.
    """
    try:
        data, filename = extract_request_data()
        compressed_bytes, stats = compress(data)

        # Base64 string payload stored inside downloadable .compressed.txt file
        base64_payload = base64.b64encode(compressed_bytes).decode("utf-8")
        out_filename = os.path.splitext(filename)[0] + ".compressed.txt"

        if request.args.get("download") == "true":
            return Response(
                base64_payload.encode("utf-8"),
                mimetype="text/plain",
                headers={"Content-Disposition": f"attachment; filename={out_filename}"}
            )

        return jsonify({
            "success": True,
            "filename": filename,
            "compressed_filename": out_filename,
            "stats": stats,
            "base64_payload": base64_payload
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/decompress", methods=["POST"])
def api_decompress():
    """
    Decompresses .compressed.txt payload back into original text file.
    Verifies cryptographic SHA-256 byte match.
    """
    try:
        huff_bytes = b""
        filename = "decompressed.txt"

        if "file" in request.files:
            file_item = request.files["file"]
            filename = file_item.filename or filename
            raw_content = file_item.read().decode("utf-8", errors="ignore").strip()
            huff_bytes = base64.b64decode(raw_content)
        else:
            json_data = request.get_json(silent=True) or {}
            raw_text = json_data.get("base64_payload") or json_data.get("text", "")
            huff_bytes = base64.b64decode(raw_text.strip())

        if not huff_bytes:
            return jsonify({"success": False, "error": "No compressed file payload provided."}), 400

        decompressed_bytes, dec_stats = decompress(huff_bytes)

        # UTF-8 text conversion
        try:
            recovered_text = decompressed_bytes.decode("utf-8")
            is_text = True
        except UnicodeDecodeError:
            recovered_text = None
            is_text = False

        base64_recovered = base64.b64encode(decompressed_bytes).decode("utf-8")
        out_name = filename.replace(".compressed.txt", "").replace(".txt", "") + "-recovered.txt"

        if request.args.get("download") == "true":
            return Response(
                decompressed_bytes,
                mimetype="text/plain",
                headers={"Content-Disposition": f"attachment; filename={out_name}"}
            )

        return jsonify({
            "success": True,
            "filename": filename,
            "recovered_filename": out_name,
            "stats": dec_stats,
            "is_text": is_text,
            "text": recovered_text,
            "base64_payload": base64_recovered
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/verify", methods=["POST"])
def api_verify():
    """Verifies that original data and decompressed data match byte-for-byte."""
    try:
        if "original_file" in request.files and "decompressed_file" in request.files:
            orig = request.files["original_file"].read()
            dec = request.files["decompressed_file"].read()
        else:
            payload = request.get_json(silent=True) or {}
            orig = base64.b64decode(payload.get("original_base64", ""))
            dec = base64.b64decode(payload.get("decompressed_base64", ""))

        result = verify_decompression(orig, dec)
        return jsonify({"success": True, "verification": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/experiment", methods=["POST"])
def api_experiment():
    """Runs multi-file benchmark matrix across sample datasets."""
    try:
        results = []
        sample_dir = os.path.join(os.path.dirname(__file__), "sample_data")
        sample_files = glob.glob(os.path.join(sample_dir, "*"))

        for filepath in sorted(sample_files):
            fname = os.path.basename(filepath)
            with open(filepath, "rb") as f:
                content = f.read()
            analysis = generate_full_analysis(content, fname)
            analysis["file_type"] = detect_file_type(fname)
            results.append(analysis)

        return jsonify({"success": True, "benchmark_results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

def extract_request_data() -> tuple[bytes, str]:
    """Extracts data bytes from file upload or JSON payload."""
    if "file" in request.files:
        file_item = request.files["file"]
        filename = file_item.filename or "uploaded_file.txt"
        data = file_item.read()
        return data, filename

    payload = request.get_json(silent=True) or {}
    if "base64" in payload:
        data = base64.b64decode(payload["base64"])
        filename = payload.get("filename", "binary_data.bin")
        return data, filename

    text = payload.get("text", "")
    data = text.encode("utf-8")
    filename = payload.get("filename", "text_input.txt")
    return data, filename

def detect_file_type(filename: str) -> str:
    """Categorizes file type for benchmark comparisons."""
    lower = filename.lower()
    if "dna" in lower:
        return "DNA Sequence"
    if lower.endswith(".bin"):
        return "Binary Data"
    if lower.endswith(".py") or lower.endswith(".js"):
        return "Source Code"
    if "single" in lower:
        return "Single Symbol Edge Case"
    if "empty" in lower:
        return "Empty File Edge Case"
    if "repetitive" in lower:
        return "Highly Repetitive Text"
    if "prose" in lower or lower.endswith(".txt"):
        return "Natural Text"
    return "General Data"

if __name__ == "__main__":
    print("Starting Huffman Lab (Matte White & Orange Edition) on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
