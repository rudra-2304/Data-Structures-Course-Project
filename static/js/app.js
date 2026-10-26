/**
 * Main Frontend Controller — Huffman Lab (Matte White & Orange Edition)
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Visualizer Instances
    const freqChart = new FrequencyChartVisualizer("freq-chart-svg");
    const experimentBench = new ExperimentBench("benchmark-body");

    let currentAnalysis = null;
    let selectedFileComp = null;
    let selectedFileDecomp = null;
    let sortState = { key: "freq", dir: "desc" };

    // 2. Navigation Tabs
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            navButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const tabId = btn.dataset.tab;
            const targetTab = document.getElementById(tabId);
            if (targetTab) targetTab.classList.add("active");
        });
    });

    // 3. Compressor Section
    const compDropzone = document.getElementById("comp-dropzone");
    const compFileInput = document.getElementById("comp-file-input");
    const compFileName = document.getElementById("comp-file-name");
    const btnCompress = document.getElementById("btn-compress");
    const compResults = document.getElementById("comp-results");
    const downloadHuffBtn = document.getElementById("download-huff-btn");

    if (compDropzone && compFileInput) {
        compDropzone.addEventListener("click", () => compFileInput.click());
        compDropzone.addEventListener("dragover", (e) => { e.preventDefault(); compDropzone.classList.add("dragover"); });
        compDropzone.addEventListener("dragleave", () => compDropzone.classList.remove("dragover"));
        compDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            compDropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                selectedFileComp = e.dataTransfer.files[0];
                compFileName.textContent = `${selectedFileComp.name} (${formatBytes(selectedFileComp.size)})`;
            }
        });
        compFileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                selectedFileComp = e.target.files[0];
                compFileName.textContent = `${selectedFileComp.name} (${formatBytes(selectedFileComp.size)})`;
            }
        });
    }

    btnCompress?.addEventListener("click", async () => {
        if (!selectedFileComp) {
            alert("Please select a text file to compress.");
            return;
        }
        try {
            const resp = await API.compressFile(selectedFileComp);
            if (resp.success && resp.stats) {
                document.getElementById("res-orig-size").textContent = formatBytes(resp.stats.original_size);
                document.getElementById("res-comp-size").textContent = formatBytes(resp.stats.compressed_size);
                document.getElementById("res-saved").textContent = `${resp.stats.space_saved.toFixed(1)}%`;
                document.getElementById("res-ratio").textContent = resp.stats.compression_ratio.toFixed(2);

                const blob = new Blob([resp.base64_payload], { type: "text/plain" });
                downloadHuffBtn.href = URL.createObjectURL(blob);
                downloadHuffBtn.download = resp.compressed_filename;

                compResults.classList.remove("hidden");
            } else {
                alert("Compression error: " + (resp.error || "Unknown"));
            }
        } catch (e) {
            alert("Compression error: " + e.message);
        }
    });

    // Decompressor Section
    const decompDropzone = document.getElementById("decomp-dropzone");
    const decompFileInput = document.getElementById("decomp-file-input");
    const decompFileName = document.getElementById("decomp-file-name");
    const btnDecompress = document.getElementById("btn-decompress");
    const decompResults = document.getElementById("decomp-results");
    const downloadDecompBtn = document.getElementById("download-decomp-btn");

    if (decompDropzone && decompFileInput) {
        decompDropzone.addEventListener("click", () => decompFileInput.click());
        decompDropzone.addEventListener("dragover", (e) => { e.preventDefault(); decompDropzone.classList.add("dragover"); });
        decompDropzone.addEventListener("dragleave", () => decompDropzone.classList.remove("dragover"));
        decompDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            decompDropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                selectedFileDecomp = e.dataTransfer.files[0];
                decompFileName.textContent = `${selectedFileDecomp.name} (${formatBytes(selectedFileDecomp.size)})`;
            }
        });
        decompFileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                selectedFileDecomp = e.target.files[0];
                decompFileName.textContent = `${selectedFileDecomp.name} (${formatBytes(selectedFileDecomp.size)})`;
            }
        });
    }

    btnDecompress?.addEventListener("click", async () => {
        if (!selectedFileDecomp) {
            alert("Please select a .compressed.txt file to decompress.");
            return;
        }
        try {
            const resp = await API.decompressFile(selectedFileDecomp);
            if (resp.success && resp.stats) {
                document.getElementById("dec-comp-size").textContent = formatBytes(resp.stats.compressed_size);
                document.getElementById("dec-orig-size").textContent = formatBytes(resp.stats.decompressed_size);

                const blob = new Blob([resp.text || ""], { type: "text/plain" });
                downloadDecompBtn.href = URL.createObjectURL(blob);
                downloadDecompBtn.download = resp.recovered_filename;

                decompResults.classList.remove("hidden");
            } else {
                alert("Decompression error: " + (resp.error || "Unknown"));
            }
        } catch (e) {
            alert("Decompression error: " + e.message);
        }
    });

    // 4. Live Bit-Savings Simulator Section
    const btnSim = document.getElementById("btn-run-sim");
    const simInput = document.getElementById("sim-input-text");

    btnSim?.addEventListener("click", () => runSimulator());
    simInput?.addEventListener("keyup", (e) => {
        if (e.key === "Enter") runSimulator();
    });

    async function runSimulator() {
        const text = simInput?.value || "hello huffman lab!";
        try {
            const resp = await API.runSimulator(text);
            if (resp.success) {
                document.getElementById("sim-ascii-bits").textContent = `${resp.ascii_total_bits} bits`;
                document.getElementById("sim-huffman-bits").textContent = `${resp.huffman_total_bits} bits`;
                document.getElementById("sim-saved-pct").textContent = `${resp.space_saved_pct.toFixed(1)}%`;

                document.getElementById("sim-ascii-stream").textContent = resp.ascii_bitstream;
                document.getElementById("sim-huffman-stream").textContent = resp.huffman_bitstream;

                // Character Breakdown Tokens
                const tokensContainer = document.getElementById("sim-tokens-container");
                tokensContainer.innerHTML = "";
                resp.char_tokens.forEach(tok => {
                    const unit = document.createElement("div");
                    unit.className = "token-unit";
                    unit.innerHTML = `
                        <div class="token-char">${escapeHtml(tok.char)}</div>
                        <div class="token-code">${tok.huffman_code}</div>
                        <div style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">
                            ${tok.huffman_len}b (Saved ${tok.bits_saved}b)
                        </div>
                    `;
                    tokensContainer.appendChild(unit);
                });
            }
        } catch (e) {
            console.error("Simulator error:", e);
        }
    }

    // 5. Analysis & Codebook Section
    const btnAnalysis = document.getElementById("btn-run-analysis");
    const analysisInput = document.getElementById("analysis-text-input");

    btnAnalysis?.addEventListener("click", () => runAnalysis());

    async function runAnalysis() {
        const text = analysisInput?.value || "hello huffman lab!";
        try {
            const resp = await API.analyzeData(text);
            if (resp.success && resp.data) {
                currentAnalysis = resp.data;
                document.getElementById("an-size").textContent = formatBytes(resp.data.original_size);
                document.getElementById("an-symbols").textContent = resp.data.unique_symbols;
                document.getElementById("an-entropy").textContent = resp.data.entropy.toFixed(2);
                document.getElementById("an-avg-len").textContent = resp.data.avg_code_length.toFixed(2);
                document.getElementById("an-efficiency").textContent = `${resp.data.efficiency.toFixed(1)}%`;
                document.getElementById("an-cs-explanation").textContent = resp.data.cs_explanation;

                freqChart.render(resp.data.code_table);
                renderCodebook(resp.data.code_table);
            }
        } catch (e) {
            console.error("Analysis error:", e);
        }
    }

    function renderCodebook(tableData) {
        const tbody = document.getElementById("codebook-body");
        if (!tbody || !tableData) return;
        tbody.innerHTML = "";

        const sorted = [...tableData].sort((a, b) => {
            let valA = a[sortState.key];
            let valB = b[sortState.key];

            if (typeof valA === "string") valA = valA.toLowerCase();
            if (typeof valB === "string") valB = valB.toLowerCase();

            if (valA < valB) return sortState.dir === "asc" ? -1 : 1;
            if (valA > valB) return sortState.dir === "asc" ? 1 : -1;
            return 0;
        });

        sorted.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${escapeHtml(row.char_display)}</strong> (ASCII: ${row.symbol})</td>
                <td>${row.freq}</td>
                <td>${(row.prob * 100).toFixed(2)}%</td>
                <td><span class="text-orange" style="font-weight:600;">${row.code}</span></td>
                <td>${row.code_length} bits</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Codebook Sorting Header Listeners
    const tableHeaders = document.querySelectorAll("#codebook-table th.sortable");
    tableHeaders.forEach(th => {
        th.addEventListener("click", () => {
            const key = th.dataset.sort;
            if (sortState.key === key) {
                sortState.dir = sortState.dir === "asc" ? "desc" : "asc";
            } else {
                sortState.key = key;
                sortState.dir = "desc";
            }
            if (currentAnalysis && currentAnalysis.code_table) {
                renderCodebook(currentAnalysis.code_table);
            }
        });
    });

    // Filter Codebook Input
    const filterInput = document.getElementById("codebook-filter");
    filterInput?.addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase();
        if (currentAnalysis && currentAnalysis.code_table) {
            const filtered = currentAnalysis.code_table.filter(item => 
                item.char_display.toLowerCase().includes(term) || item.code.includes(term)
            );
            renderCodebook(filtered);
        }
    });

    // 6. Benchmark Section Listener
    const btnBenchmark = document.getElementById("btn-run-benchmark");
    btnBenchmark?.addEventListener("click", () => experimentBench.runBenchmark());

    // Initial triggers on page load
    runSimulator();
    runAnalysis();
});

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
