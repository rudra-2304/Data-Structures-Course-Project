/**
 * Huffman Lab API Client
 * Wraps REST API communications with Flask backend.
 */

const API = {
    async analyzeData(textOrFile) {
        if (textOrFile instanceof File) {
            const formData = new FormData();
            formData.append("file", textOrFile);
            const resp = await fetch("/api/analyze", { method: "POST", body: formData });
            return await resp.json();
        } else {
            const resp = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: textOrFile })
            });
            return await resp.json();
        }
    },

    async runSimulator(text) {
        const resp = await fetch("/api/simulator", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        return await resp.json();
    },

    async compressFile(file) {
        const formData = new FormData();
        formData.append("file", file);
        const resp = await fetch("/api/compress", { method: "POST", body: formData });
        return await resp.json();
    },

    async decompressFile(file) {
        const formData = new FormData();
        formData.append("file", file);
        const resp = await fetch("/api/decompress", { method: "POST", body: formData });
        return await resp.json();
    },

    async runBenchmark() {
        const resp = await fetch("/api/experiment", { method: "POST" });
        return await resp.json();
    }
};

window.API = API;
