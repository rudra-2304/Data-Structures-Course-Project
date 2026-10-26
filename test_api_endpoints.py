import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_json(endpoint):
    with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as resp:
        return json.loads(resp.read().decode("utf-8"))

print("Testing GET / ...")
with urllib.request.urlopen(BASE_URL) as resp:
    html = resp.read().decode("utf-8")
    assert "Huffman Lab" in html
    assert "Huffman" in html
    print("PASS: GET / (Huffman Lab UI)")

print("Testing POST /api/analyze ...")
res = post_json("/api/analyze", {"text": "hello huffman lab!"})
assert res["success"] == True
assert res["data"]["entropy"] > 0
print("PASS: POST /api/analyze")

print("Testing POST /api/simulator ...")
res = post_json("/api/simulator", {"text": "hello huffman lab!"})
assert res["success"] == True
assert res["ascii_total_bits"] > res["huffman_total_bits"]
assert res["space_saved_pct"] > 0
print("PASS: POST /api/simulator")

print("Testing POST /api/compress (.compressed.txt format) ...")
res = post_json("/api/compress", {"text": "testing text compression endpoint 12345"})
assert res["success"] == True
assert ".compressed.txt" in res["compressed_filename"]
base64_payload = res["base64_payload"]
print("PASS: POST /api/compress")

print("Testing POST /api/decompress (.compressed.txt format) ...")
res = post_json("/api/decompress", {"base64_payload": base64_payload})
assert res["success"] == True
assert res["text"] == "testing text compression endpoint 12345"
print("PASS: POST /api/decompress")

print("Testing POST /api/experiment ...")
res = post_json("/api/experiment", {})
assert res["success"] == True
assert len(res["benchmark_results"]) > 0
print("PASS: POST /api/experiment")

print("ALL MATTE WHITE & ORANGE HUFFMAN LAB API TESTS PASSED!")
